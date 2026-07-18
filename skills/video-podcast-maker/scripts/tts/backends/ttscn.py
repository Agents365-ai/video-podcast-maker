"""Bridge to the ttsCN component skill — the single synthesis engine.

Every BACKENDS id routes here with config['platform'] set. Chunks are sent
RAW (expressiveness markers intact): ttsCN owns per-platform rendering of
[PAUSE:x] / sound tags and phoneme application (--phonemes). Each chunk is
one `tts.py` invocation (ttsCN sub-chunks internally per provider limits),
then normalized to the suite's 48 kHz mono WAV.

Word boundaries: when ttsCN returns data.word_boundaries (platforms with
native boundary events: edge, azure, doubao, minimax, cosyvoice), each
offset_sec — absolute within that invocation's file — is shifted by the
accumulated duration of prior chunks, and non-spoken script characters
(punctuation) are reinserted between word tokens
(_merge_native_boundaries) because srt.py and section matching rely on
them. Otherwise (and for resume-skipped parts) boundaries are estimated
by distributing the measured chunk duration across visible characters.
Keep registry max_chars small (400): estimation error is bounded by chunk
length, and chunk durations themselves are always measured.

config keys: entry (tts.py path), platform, voice, speech_rate, phonemes_path,
style (azure only — injected as TTS_STYLE into the subprocess env).
"""
import json
import os
import subprocess
import sys
import time
from .base import check_resume
from ..markers import strip_markers


def _merge_native_boundaries(chunk, native, base_offset):
    """Convert native boundaries to absolute offsets, reinserting punctuation.

    Native streams carry spoken words only, but srt.py breaks cues at
    punctuation tokens and section matching compares against script text —
    so walk the visible chunk text and re-emit the skipped characters as
    short entries anchored to the preceding word's end.

    Some backends (MiniMax) return one entry per spoken syllable, each
    labeled with the full source token — e.g. "37" spoken as "三十七"
    produces 3 entries all with text "37". Merge consecutive identical
    token entries into one before gap reconstruction.
    """
    # --- Merge consecutive identical tokens (syllable splitting) ---
    deduped = []
    for wb in native:
        if (deduped and deduped[-1]["text"] == wb["text"]
                and deduped[-1]["offset_sec"] + deduped[-1]["duration_sec"]
                >= wb["offset_sec"] - 0.05):
            # Adjacent same-token entry — extend duration to cover this syllable
            end = wb["offset_sec"] + wb["duration_sec"]
            deduped[-1]["duration_sec"] = end - deduped[-1]["offset_sec"]
        else:
            deduped.append(dict(wb))
    native = deduped

    text = strip_markers(chunk)
    merged = []
    pos = 0

    def emit_gap(upto, anchor_offset):
        nonlocal pos
        for ch in text[pos:upto]:
            if ch.strip():
                merged.append({"text": ch, "offset": anchor_offset,
                               "duration": 0.01})
        pos = upto

    for wb in native:
        offset = base_offset + wb["offset_sec"]
        idx = text.find(wb["text"], pos)
        if idx >= 0:
            emit_gap(idx, merged[-1]["offset"] + merged[-1]["duration"]
                     if merged else offset)
            pos = idx + len(wb["text"])
        # ponytail: idx < 0 means the engine rewrote the token text (rare
        # normalization) — keep the word, skip gap reconstruction; SRT still
        # works, just with fewer break points. Revisit if a platform rewrites.
        merged.append({"text": wb["text"], "offset": offset,
                       "duration": wb["duration_sec"]})
    if merged:
        emit_gap(len(text), merged[-1]["offset"] + merged[-1]["duration"])
    return merged


def synthesize(chunks, config, output_dir, resume=False):
    entry = config['entry']
    platform = config.get('platform') or 'edge'
    voice = config.get('voice')
    speech_rate = config.get('speech_rate')
    phonemes_path = config.get('phonemes_path')
    # ttsCN's azure adapter reads TTS_STYLE from env — inject the resolved
    # style so vpm's pre-4.0 default ('gentle') carries over.
    sub_env = os.environ.copy()
    if config.get('style') is not None:
        sub_env['TTS_STYLE'] = config['style']

    part_files = []
    word_boundaries = []
    accumulated_duration = 0

    def estimate_boundaries(chunk, duration, base_offset):
        """Distribute a measured chunk duration across its visible chars."""
        chars = [c for c in strip_markers(chunk) if c.strip()]
        if not chars or duration <= 0:
            return
        per = duration / len(chars)
        for idx, ch in enumerate(chars):
            word_boundaries.append({
                "text": ch,
                "offset": base_offset + idx * per,
                "duration": max(0.01, per),
            })

    for i, chunk in enumerate(chunks):
        part_file = os.path.join(output_dir, f"part_{i}.wav")
        part_files.append(part_file)

        if resume:
            dur = check_resume(part_file)
            if dur is not None:
                print(f"  ⏭ Part {i + 1}/{len(chunks)} skipped (resume, {dur:.1f}s)")
                estimate_boundaries(chunk, dur, accumulated_duration)
                accumulated_duration += dur
                continue

        raw_file = os.path.join(output_dir, f"part_{i}_ttscn.wav")
        cmd = [sys.executable, entry, chunk, raw_file,
               '--platform', platform, '--format', 'json']
        if voice:
            cmd += ['--voice', voice]
        if speech_rate:
            cmd += ['--rate', speech_rate]
        if phonemes_path:
            cmd += ['--phonemes', phonemes_path]

        success = False
        for attempt in range(1, 3):
            proc = subprocess.run(cmd, capture_output=True, text=True, env=sub_env)
            envelope = None
            try:
                envelope = json.loads(proc.stdout) if proc.stdout.strip() else None
            except json.JSONDecodeError:
                pass
            if proc.returncode == 0 and envelope and envelope.get('ok'):
                resample = subprocess.run(
                    ["ffmpeg", "-y", "-i", raw_file, "-ar", "48000", "-ac", "1", part_file],
                    capture_output=True, text=True)
                if resample.returncode != 0:
                    # Fail here with the real cause — otherwise the part is
                    # reported done at 0.0s and the run dies later at concat.
                    raise RuntimeError(
                        f"ffmpeg resample failed for part {i + 1}: "
                        f"{resample.stderr.strip()[-200:]}")
                os.remove(raw_file)
                chunk_duration = float(envelope['data'].get('duration_seconds') or 0)
                if not chunk_duration:
                    dur = check_resume(part_file)
                    chunk_duration = dur or 0
                native = envelope['data'].get('word_boundaries')
                if native:
                    word_boundaries.extend(_merge_native_boundaries(
                        chunk, native, accumulated_duration))
                else:
                    estimate_boundaries(chunk, chunk_duration, accumulated_duration)
                accumulated_duration += chunk_duration
                print(f"  ✓ Part {i + 1}/{len(chunks)} done via ttsCN/{platform} "
                      f"({len(chunk)} chars, {chunk_duration:.1f}s)")
                success = True
                break
            err = (envelope or {}).get('error', {})
            detail = err.get('message') or proc.stderr.strip()[-200:] or f"exit {proc.returncode}"
            print(f"  ✗ Part {i + 1} failed (attempt {attempt}/2): {detail}")
            # Auth errors won't heal on retry — surface immediately
            if err.get('code') in ('auth', 'auth_missing_env') or proc.returncode == 3:
                raise RuntimeError(f"ttsCN auth error: {detail}")
            if attempt < 2:
                time.sleep(attempt * 2)

        if not success:
            raise RuntimeError(f"Part {i + 1} synthesis failed via ttsCN/{platform}")

    return part_files, word_boundaries, accumulated_duration
