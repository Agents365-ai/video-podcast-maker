#!/usr/bin/env python3
"""
TTS Script for Video Podcast Maker — all backends route through the ttsCN component skill.
Generates audio from podcast.txt and creates SRT subtitles + timing.json for Remotion sync
"""
import json
import os
import sys
import re
import time
import argparse
import subprocess

import cli_envelope
from tts.markers import protect_pauses, restore_pauses, strip_markers
from tts.phonemes import load_phoneme_dicts, extract_inline_phonemes
from tts.sections import parse_sections, validate_sections, print_validation_report, match_section_times
from tts.srt import write_srt, write_timing, reconcile_timing_with_wav
from tts.voice_advisor import print_advisory


def build_parser():
    parser = argparse.ArgumentParser(
        description='Generate TTS audio from podcast script',
        epilog='Backends (all synthesized by the required ttsCN component skill): edge (default, '
               'free), azure, cosyvoice, doubao, tencent, baidu, minimax, xunfei, elevenlabs, '
               'openai, google, plus the ttscn alias (TTSCN_PLATFORM picks its platform). '
               'Env: TTS_BACKEND, TTS_VOICE, TTS_RATE + per-platform API keys (check_prereqs.py '
               'validates the active backend).'
    )
    parser.add_argument('--input', '-i', default='podcast.txt', help='Input script file (default: podcast.txt)')
    parser.add_argument('--output-dir', '-o', default='.', help='Output directory (default: current dir)')
    parser.add_argument('--phonemes', '-p', default=None, help='Phoneme dictionary JSON file')
    parser.add_argument('--backend', '-b', default=None,
        help='TTS backend (routed via ttsCN): edge, azure, cosyvoice, doubao, tencent, '
             'baidu, minimax, xunfei, elevenlabs, openai, google, or ttscn')
    parser.add_argument('--resume', action='store_true', help='Resume from last breakpoint')
    parser.add_argument('--dry-run', action='store_true',
        help='Plan synthesis without calling the TTS API. Emits backend, voice, '
             'chunk count, total chars, and estimated duration so an agent can '
             'preview cost. Requires backend env vars (uses init_backend).')
    parser.add_argument('--validate', action='store_true',
        help='Validate podcast.txt structure (section markers, content) without '
             'TTS API calls or backend env vars. Lighter than --dry-run; useful '
             'as a first gate before committing to a backend.')
    cli_envelope.add_format_arg(parser)
    return parser


_END_PUNCT = ("。", ".", "!", "?")
_SOFT_PUNCT = "，,;：:、 "
# Any punctuation that already gives the TTS engine a prosodic break — used to
# decide when NOT to append a synthetic "。" (which would force a falling-tone
# full-stop pause where a comma was intended).
_PROSODIC_END = _END_PUNCT + tuple(_SOFT_PUNCT.replace(" ", ""))


def _hard_split(sentence, max_chars):
    """Split an oversize sentence into pieces each <= max_chars.

    Walks char by char; once the buffer reaches `budget = max_chars - 1`,
    flushes at the most recent soft-punctuation point inside a small lookback
    window. The 1-char headroom is reserved for the "，" appended in the
    fixed-width fallback when no natural break is reachable.

    Pieces preserve their natural cut point (a soft-punct char like "，"),
    so when chunks are concatenated for TTS the seam reads as a comma pause
    instead of a synthesized full-stop pause.
    """
    if len(sentence) <= max_chars:
        return [sentence]
    budget = max_chars - 1
    lookback = max(8, max_chars // 4)
    pieces = []
    buf = ""
    for ch in sentence:
        buf += ch
        if len(buf) >= budget:
            cut = -1
            for i in range(len(buf) - 1, max(-1, len(buf) - lookback - 1), -1):
                # Never cut inside an unclosed [...] token — [PAUSE:0p8]
                # contains ':' which would otherwise be a soft-punct cut.
                if buf[i] in _SOFT_PUNCT and \
                        buf.rfind("[", 0, i + 1) <= buf.rfind("]", 0, i + 1):
                    cut = i
                    break
            if cut >= 0:
                pieces.append(buf[:cut + 1])
                buf = buf[cut + 1:]
            else:
                # Fixed-width fallback: a "，" gives the engine a soft pause
                # at the seam without the falling-tone of a "。".
                pieces.append(buf + "，")
                buf = ""
    if buf:
        pieces.append(buf)
    return pieces


def chunk_text(clean_text, max_chars):
    """Split text into chunks for TTS synthesis.

    Handles both Chinese (。；) and English (. ; ? !) sentence boundaries.
    Sentences longer than `max_chars` are hard-split on soft punctuation,
    then by fixed width — guarantees no chunk exceeds the backend's limit.

    A synthetic "。" is only appended to pieces with NO terminal punctuation
    (defensive — most scripts are punctuated). Pieces from `_hard_split`
    end with their natural soft-punct cut and are passed through unchanged
    so the TTS engine doesn't render a comma boundary as a full stop.
    """
    normalized = clean_text.replace("；", "。")
    raw_sentences = re.split(r'(?<=[。.!?])\s*', normalized)
    sentences = []
    for s in raw_sentences:
        s = s.strip()
        if not s:
            continue
        sentences.extend(_hard_split(s, max_chars))

    chunks = []
    current_chunk = ""
    for s in sentences:
        suffix = "" if s.endswith(_PROSODIC_END) else "。"
        addition = s + suffix
        if len(current_chunk) + len(addition) <= max_chars:
            current_chunk += addition
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = addition
    if current_chunk:
        chunks.append(current_chunk)
    return chunks


def main():
    parser = build_parser()
    args = parser.parse_args()
    started_at = time.time()
    json_mode = cli_envelope.use_json(args)
    if json_mode:
        # In JSON mode every progress line and helper print() must move off
        # stdout so the final envelope is the only payload an agent parses.
        # cli_envelope captured the real stdout at import time, so emit_*
        # still reaches it via cli_envelope._REAL_STDOUT.
        sys.stdout = sys.stderr
    try:
        return _run(args, started_at)
    finally:
        sys.stdout = sys.__stdout__


def _run(args, started_at):
    # --- Backend init (skip for validate-only) ---
    if not args.validate:
        from tts.backends import (
            BackendError, init_backend, get_synthesize_func, get_max_chars, resolve_backend,
        )
        if args.backend:
            BACKEND, source = args.backend, 'cli'
        else:
            BACKEND, source = resolve_backend()
        print(f"TTS backend: {BACKEND} [from {source}]")

        try:
            config = init_backend(BACKEND)
        except BackendError as exc:
            sys.exit(cli_envelope.emit_error(
                args, exc.code, str(exc),
                extra={"backend": BACKEND, "backend_source": source},
                started_at=started_at,
            ))
        MAX_CHARS = get_max_chars(BACKEND)
    else:
        # --validate path: skip backend init, but use the registry's edge limit
        # so chunk-count estimates stay in sync with real synthesis.
        from tts.backends import get_max_chars
        BACKEND = "edge"
        MAX_CHARS = get_max_chars(BACKEND)

    from tts.backends import resolve_speech_rate
    SPEECH_RATE, rate_source = resolve_speech_rate()
    print(f"Speech rate: {SPEECH_RATE} [from {rate_source}]")

    # --- Read input ---
    os.makedirs(args.output_dir, exist_ok=True)

    if not os.path.exists(args.input):
        sys.exit(cli_envelope.emit_error(
            args, "input_not_found",
            f"Input file not found: {args.input}",
            field="input", started_at=started_at,
        ))

    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read().strip()

    # --- Parse sections ---
    sections, matches, clean_text = parse_sections(text)

    # --- Validate mode ---
    if args.validate:
        errors, warnings = validate_sections(text, sections, matches)
        if cli_envelope.use_json(args):
            section_names = [s['name'] for s in sections]
            # Run the real chunker so the agent sees the actual chunk count
            # an agent gets from `tts run` — not a stale `len(text) // 200`
            # estimate that predates the 400 → 2000 max_chars bump.
            chunks = chunk_text(clean_text, MAX_CHARS)
            if errors:
                sys.exit(cli_envelope.emit_error(
                    args, "validation_failed",
                    f"{len(errors)} validation error(s) in {args.input}",
                    extra={"errors": errors, "warnings": warnings, "sections": section_names},
                    started_at=started_at,
                ))
            sys.exit(cli_envelope.emit_success(args, {
                "input": args.input,
                "sections": section_names,
                "warnings": warnings,
                "total_chars": len(clean_text),
                "chunks_count": len(chunks),
                "max_chars": MAX_CHARS,
            }, started_at=started_at))
        print_validation_report(args.input, sections, clean_text, errors, warnings)
        return  # print_validation_report calls sys.exit, but guard against refactoring

    # --- Phonemes ---
    clean_text, inline_phonemes = extract_inline_phonemes(clean_text)
    if inline_phonemes:
        print(f"Extracted inline phoneme annotations: {len(inline_phonemes)} entries")
        for word, pinyin in inline_phonemes.items():
            print(f"    {word} -> {pinyin}")

    file_phonemes = load_phoneme_dicts(args.input, args.phonemes)
    phoneme_dict = {**file_phonemes, **inline_phonemes}
    print(f"Phoneme dictionary: {len(phoneme_dict)} entries (file: {len(file_phonemes)} + inline: {len(inline_phonemes)})")

    # Phoneme application happens inside ttsCN (azure -> SSML <phoneme>,
    # minimax -> pinyin annotations; other platforms ignore the file).
    if phoneme_dict:
        print("Note: phonemes are applied by ttsCN where the platform "
              "supports them (azure SSML, minimax pinyin annotations).")

    # --- Default section ---
    if not sections:
        sections = [{'name': 'main', 'first_text': '', 'start_time': 0, 'end_time': None}]
        print("Note: No [SECTION:name] markers detected, generating single section")
    else:
        print(f"Detected {len(sections)} sections: {[s['name'] for s in sections]}")
        for s in sections:
            status = " (silent)" if s.get('is_silent') else ""
            print(f"  {s['name']}: \"{s['first_text'][:20]}...\"{status}")

    # --- Text cleanup ---
    # "Read-as" annotation: strip 'X，读作"Y"' (curly or straight quotes) and keep only Y.
    # This is a fourth, lightweight pronunciation override that works on backends without
    # SSML support (Doubao / ElevenLabs / OpenAI / Google) by rewriting the source text.
    # Trade-off: it also changes what the subtitle says (Y appears, X is gone). Prefer the
    # inline [pinyin] marker or phonemes.json when SSML is available (Azure / Edge).
    clean_text = re.sub(r'([A-Za-z0-9\-]+)，读作["""]([\u4e00-\u9fff]+)["""]', r"\2", clean_text)
    print(f"Text length: {len(clean_text)} characters")

    # Voice advisory — flag when content vs voice choice is suboptimal
    if BACKEND == 'azure':
        print_advisory(clean_text, config.get('voice'))

    # --- Dry run ---
    if args.dry_run:
        cn_chars = len(re.findall(r'[\u4e00-\u9fff]', clean_text))
        en_words = len(re.findall(r'[A-Za-z]+', clean_text))
        est_duration = cn_chars / 4.0 + en_words / 3.0
        rate_match = re.match(r'([+-]?\d+)%', SPEECH_RATE)
        if rate_match:
            est_duration /= 1.0 + int(rate_match.group(1)) / 100.0
        est_frames = int(est_duration * 30)
        non_silent = [s for s in sections if not s.get('is_silent')]
        chunks = chunk_text(clean_text, MAX_CHARS)
        print(f"\n--- Dry Run ---")
        print(f"Chinese chars: {cn_chars}, English words: {en_words}")
        print(f"Total chars: {len(clean_text)} -> {len(chunks)} chunk(s) (max {MAX_CHARS}/chunk)")
        print(f"Estimated duration: {est_duration:.0f}s ({est_duration/60:.1f}min)")
        print(f"Estimated frames: {est_frames} @ 30fps")
        print(f"Speech rate: {SPEECH_RATE}")
        print(f"Backend: {BACKEND}, voice: {config.get('voice')} (not called)")
        if len(non_silent) > 1:
            avg = est_duration / len(non_silent)
            print(f"Average section: ~{avg:.0f}s ({len(non_silent)} sections with content)")
        sys.exit(cli_envelope.emit_success(args, {
            "dry_run": True,
            "backend": BACKEND,
            "voice": config.get("voice"),
            "speech_rate": SPEECH_RATE,
            "max_chars": MAX_CHARS,
            "total_chars": len(clean_text),
            "cn_chars": cn_chars,
            "en_words": en_words,
            "chunks_count": len(chunks),
            "estimated_duration_seconds": round(est_duration, 2),
            "estimated_frames_at_30fps": est_frames,
            "sections": [s['name'] for s in sections],
            "non_silent_sections": len(non_silent),
        }, started_at=started_at))

    # --- Expressiveness markers ---
    # [PAUSE:x] / sound tags must never reach subtitles or section matching;
    # section anchors are compared against marker-free boundary text.
    for s in sections:
        s['first_text'] = strip_markers(s.get('first_text', ''))

    # --- Chunk text ---
    # protect_pauses keeps the '.' inside [PAUSE:0.8] from being treated as a
    # sentence boundary (a chunk split mid-marker would break it in half).
    chunks = [restore_pauses(c) for c in chunk_text(protect_pauses(clean_text), MAX_CHARS)]
    print(f"Split into {len(chunks)} chunks")

    # Chunks keep raw [PAUSE:x] / sound-tag markers — ttsCN renders or
    # strips them per platform.

    # --- Synthesize ---
    config['speech_rate'] = SPEECH_RATE
    if phoneme_dict:
        # ttsCN consumes phonemes as a file — write the merged dict
        # (global + project + inline) next to the audio parts.
        phonemes_path = os.path.join(args.output_dir, "phonemes_resolved.json")
        with open(phonemes_path, "w", encoding="utf-8") as f:
            json.dump(phoneme_dict, f, ensure_ascii=False, indent=2)
        config['phonemes_path'] = phonemes_path
    synthesize = get_synthesize_func(BACKEND)
    part_files, word_boundaries, total_duration = synthesize(chunks, config, args.output_dir, resume=args.resume)
    print(f"\nCollected {len(word_boundaries)} word boundaries")
    print(f"Total duration: {total_duration:.1f}s")

    # --- Match section times ---
    sections = match_section_times(sections, word_boundaries, total_duration)

    # --- Generate SRT + timing.json (before concat, so they're saved even if concat fails) ---
    print("\nGenerating subtitles...")
    output_srt = os.path.join(args.output_dir, "podcast_audio.srt")
    write_srt(word_boundaries, output_srt)

    output_timing = os.path.join(args.output_dir, "timing.json")
    write_timing(sections, total_duration, SPEECH_RATE, output_timing)

    # --- Concat audio ---
    print("\nConcatenating audio...")
    concat_list = os.path.join(args.output_dir, "concat_list.txt")
    output_wav = os.path.join(args.output_dir, "podcast_audio.wav")
    with open(concat_list, "w", encoding="utf-8") as f:
        for pf in part_files:
            f.write(f"file '{os.path.basename(pf)}'\n")

    # cwd is output_dir (the list entries are basenames), so the list and
    # output paths must be basenames too — a relative --output-dir would
    # otherwise be resolved twice and point nowhere.
    concat_result = subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
         "-i", os.path.basename(concat_list), "-c", "copy",
         os.path.basename(output_wav)],
        capture_output=True, text=True, cwd=args.output_dir)
    if concat_result.returncode != 0:
        sys.exit(cli_envelope.emit_error(
            args, "ffmpeg_failed",
            "FFmpeg concat failed; timing.json and podcast_audio.srt were saved.",
            extra={
                "stderr": concat_result.stderr.strip(),
                "saved_outputs": {"timing": output_timing, "subtitles": output_srt},
            },
            started_at=started_at,
        ))
    print(f"Done: {output_wav}")
    print(f"  Temp files kept: {len(part_files)} part_*.wav (manual cleanup: Step 14)")

    # Reconcile timing.json with actual WAV duration. Azure can under-report
    # audio_duration when SSML tags (break/phoneme/say-as) are present, leading
    # to drift between timing.json and the real audio. Conservative rescale here
    # ensures the Remotion composition's last sections aren't truncated.
    print("\nVerifying audio/timing alignment...")
    reconcile_timing_with_wav(output_timing, output_wav)

    sys.exit(cli_envelope.emit_success(args, {
        "backend": BACKEND,
        "speech_rate": SPEECH_RATE,
        "audio_wav": output_wav,
        "subtitles_srt": output_srt,
        "timing_json": output_timing,
        "total_duration_seconds": round(total_duration, 2),
        "chunks": len(chunks),
        "part_files": len(part_files),
        "sections": [
            {
                "name": s['name'],
                "start_time": s.get('start_time'),
                "duration": s.get('duration'),
                "is_silent": s.get('is_silent', False),
            }
            for s in sections
        ],
    }, started_at=started_at))


if __name__ == "__main__":
    main()
