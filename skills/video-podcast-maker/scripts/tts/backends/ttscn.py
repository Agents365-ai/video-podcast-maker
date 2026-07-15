"""Bridge backend delegating synthesis to the ttsCN component skill.

Adds ttsCN's China-friendly providers (tencent, baidu, minimax, xunfei, ...)
without duplicating their adapters here. Each chunk is synthesized by one
`tts.py` invocation (ttsCN sub-chunks internally per provider limits and
concatenates), then normalized to the suite's 48 kHz mono WAV.

Word boundaries are estimated per chunk (measured chunk duration distributed
across characters, same fallback as doubao) so SRT and section matching work.
Keep registry max_chars small (400) — estimation error is bounded by chunk
length, and chunk durations themselves are always measured.

For platform=minimax the bridge also renders expressiveness:
[PAUSE:x] -> <#x#>, sound tags kept, and phonemes.json entries become
pinyin annotations (字(pin1)). Other platforms get marker-stripped text.

config keys: entry (tts.py path), platform (ttsCN backend id), voice,
speech_rate, phoneme_dict.
"""
import json
import os
import subprocess
import sys
import time
from .base import check_resume
from ..markers import SOUND_TAG_RE, render_markers, strip_markers
from ..phonemes import apply_phonemes_minimax


def synthesize(chunks, config, output_dir, resume=False):
    entry = config['entry']
    platform = config.get('platform') or 'edge'
    voice = config.get('voice')
    speech_rate = config.get('speech_rate')

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

        if platform == 'minimax':
            speak_text = apply_phonemes_minimax(
                render_markers(chunk, 'minimax'), config.get('phoneme_dict') or {})
            # Sound tags are only understood by speech-2.8 models — on older
            # models MiniMax reads "(chuckle)" aloud, so strip them instead.
            if not os.environ.get('MINIMAX_MODEL', '').startswith('speech-2.8'):
                if SOUND_TAG_RE.search(speak_text):
                    print("  ⚠ sound tags stripped: set MINIMAX_MODEL=speech-2.8-hd "
                          "to voice them")
                speak_text = SOUND_TAG_RE.sub('', speak_text)
        else:
            speak_text = render_markers(chunk, 'plain')

        raw_file = os.path.join(output_dir, f"part_{i}_ttscn.wav")
        cmd = [sys.executable, entry, speak_text, raw_file,
               '--platform', platform, '--format', 'json']
        if voice:
            cmd += ['--voice', voice]
        if speech_rate:
            cmd += ['--rate', speech_rate]

        success = False
        for attempt in range(1, 3):
            proc = subprocess.run(cmd, capture_output=True, text=True)
            envelope = None
            try:
                envelope = json.loads(proc.stdout) if proc.stdout.strip() else None
            except json.JSONDecodeError:
                pass
            if proc.returncode == 0 and envelope and envelope.get('ok'):
                subprocess.run(
                    ["ffmpeg", "-y", "-i", raw_file, "-ar", "48000", "-ac", "1", part_file],
                    capture_output=True)
                os.remove(raw_file)
                chunk_duration = float(envelope['data'].get('duration_seconds') or 0)
                if not chunk_duration:
                    dur = check_resume(part_file)
                    chunk_duration = dur or 0
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
