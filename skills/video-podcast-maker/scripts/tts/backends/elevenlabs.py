"""ElevenLabs TTS backend."""
import os
import base64
import subprocess
import time
from .base import check_resume


def synthesize(chunks, config, output_dir, resume=False):
    """Synthesize using ElevenLabs TTS API with character-level timestamps.

    config keys: key, voice, model, speech_rate
    """
    import requests

    key = config['key']
    voice = config.get('voice', '21m00Tcm4TlvDq8ikWAM')
    model = config.get('model', 'eleven_multilingual_v2')

    part_files = []
    word_boundaries = []
    accumulated_duration = 0

    headers = {
        "xi-api-key": key,
        "Content-Type": "application/json",
    }

    for i, chunk in enumerate(chunks):
        part_file = os.path.join(output_dir, f"part_{i}.wav")
        part_files.append(part_file)

        if resume:
            dur = check_resume(part_file)
            if dur is not None:
                print(f"  ⏭ Part {i + 1}/{len(chunks)} skipped (resume, {dur:.1f}s)")
                accumulated_duration += dur
                continue

        success = False
        for attempt in range(1, 4):
            try:
                url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps"
                payload = {
                    "text": chunk,
                    "model_id": model,
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75,
                    },
                }

                resp = requests.post(url, headers=headers, json=payload, timeout=120)
                resp.raise_for_status()
                data = resp.json()

                audio_b64 = data.get("audio_base64")
                if not audio_b64:
                    raise RuntimeError("ElevenLabs returned empty audio")
                audio_bytes = base64.b64decode(audio_b64)

                mp3_file = part_file.replace('.wav', '.mp3')
                with open(mp3_file, 'wb') as f:
                    f.write(audio_bytes)

                result = subprocess.run(
                    ["ffmpeg", "-y", "-i", mp3_file, "-ar", "48000", "-ac", "1", part_file],
                    capture_output=True, text=True)
                if result.returncode != 0:
                    raise RuntimeError(f"FFmpeg convert failed: {result.stderr}")
                os.remove(mp3_file)

                probe = subprocess.run(
                    ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", part_file],
                    capture_output=True, text=True)
                chunk_duration = float(probe.stdout.strip()) if probe.stdout.strip() else 0

                alignment = data.get("alignment", {})
                chars = alignment.get("characters", [])
                char_starts = alignment.get("character_start_times_seconds", [])
                char_ends = alignment.get("character_end_times_seconds", [])

                if chars and char_starts and char_ends:
                    current_word = ""
                    word_start = 0
                    for ci, ch in enumerate(chars):
                        if ci < len(char_starts) and ci < len(char_ends):
                            if not current_word:
                                word_start = char_starts[ci]
                            current_word += ch
                            is_boundary = ch in " \t\n" or ci == len(chars) - 1
                            if is_boundary and current_word.strip():
                                word_end = char_ends[ci]
                                word_boundaries.append({
                                    "text": current_word.strip(),
                                    "offset": accumulated_duration + word_start,
                                    "duration": word_end - word_start,
                                })
                                current_word = ""

                print(f"  ✓ Part {i + 1}/{len(chunks)} done ({len(chunk)} chars, {chunk_duration:.1f}s)")
                accumulated_duration += chunk_duration
                success = True
                break
            except Exception as e:
                print(f"  ✗ Part {i + 1} failed (attempt {attempt}/3): {e}")
                if attempt < 3:
                    time.sleep(attempt * 2)

        if not success:
            raise RuntimeError(f"Part {i + 1} synthesis failed")

    return part_files, word_boundaries, accumulated_duration
