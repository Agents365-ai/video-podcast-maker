"""Bridge backend delegating synthesis to the ttsCN component skill.

Adds ttsCN's China-friendly providers (tencent, baidu, minimax, xunfei, ...)
without duplicating their adapters here. Each chunk is synthesized by one
`tts.py` invocation (ttsCN sub-chunks internally per provider limits and
concatenates), then normalized to the suite's 48 kHz mono WAV.

No word boundaries are available through the bridge — SRT falls back to the
same chunk-level estimation path as the other non-edge backends.

config keys: entry (tts.py path), platform (ttsCN backend id), voice,
speech_rate.
"""
import json
import os
import subprocess
import sys
import time
from .base import check_resume


def synthesize(chunks, config, output_dir, resume=False):
    entry = config['entry']
    platform = config.get('platform') or 'edge'
    voice = config.get('voice')
    speech_rate = config.get('speech_rate')

    part_files = []
    accumulated_duration = 0

    for i, chunk in enumerate(chunks):
        part_file = os.path.join(output_dir, f"part_{i}.wav")
        part_files.append(part_file)

        if resume:
            dur = check_resume(part_file)
            if dur is not None:
                print(f"  ⏭ Part {i + 1}/{len(chunks)} skipped (resume, {dur:.1f}s)")
                accumulated_duration += dur
                continue

        raw_file = os.path.join(output_dir, f"part_{i}_ttscn.wav")
        cmd = [sys.executable, entry, chunk, raw_file,
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

    return part_files, [], accumulated_duration
