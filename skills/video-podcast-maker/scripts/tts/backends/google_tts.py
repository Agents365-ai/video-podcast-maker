"""Google Cloud TTS backend."""
import os
import re
import base64
import subprocess
import time
from .base import check_resume


def synthesize(chunks, config, output_dir, resume=False):
    """Synthesize using Google Cloud TTS API. Word boundaries are approximate.

    config keys: key, voice, language, speech_rate
    """
    import requests

    key = config['key']
    voice = config.get('voice', 'en-US-Neural2-F')
    language = config.get('language', 'en-US')
    speech_rate = config.get('speech_rate', '+5%')

    rate_match = re.match(r'([+-]?\d+)%', speech_rate)
    speaking_rate = 1.0 + int(rate_match.group(1)) / 100.0 if rate_match else 1.0
    speaking_rate = max(0.25, min(4.0, speaking_rate))

    url = "https://texttospeech.googleapis.com/v1/text:synthesize"
    headers = {"X-Goog-Api-Key": key, "Content-Type": "application/json"}

    part_files = []
    word_boundaries = []
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

        success = False
        for attempt in range(1, 4):
            try:
                payload = {
                    "input": {"text": chunk},
                    "voice": {
                        "languageCode": language,
                        "name": voice,
                    },
                    "audioConfig": {
                        "audioEncoding": "LINEAR16",
                        "sampleRateHertz": 48000,
                        "speakingRate": speaking_rate,
                    },
                }

                resp = requests.post(url, json=payload, headers=headers, timeout=120)
                resp.raise_for_status()
                data = resp.json()

                audio_b64 = data.get("audioContent")
                if not audio_b64:
                    raise RuntimeError("Google TTS returned empty audio")
                audio_bytes = base64.b64decode(audio_b64)

                tmp_file = part_file + ".tmp.wav"
                with open(tmp_file, 'wb') as f:
                    f.write(audio_bytes)

                result = subprocess.run(
                    ["ffmpeg", "-y", "-i", tmp_file, "-ar", "48000", "-ac", "1", part_file],
                    capture_output=True, text=True)
                if result.returncode != 0:
                    raise RuntimeError(f"FFmpeg normalize failed: {result.stderr}")
                os.remove(tmp_file)

                probe = subprocess.run(
                    ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", part_file],
                    capture_output=True, text=True)
                chunk_duration = float(probe.stdout.strip()) if probe.stdout.strip() else 0

                words = chunk.split()
                if words and chunk_duration > 0:
                    avg_word_duration = chunk_duration / len(words)
                    for wi, word in enumerate(words):
                        word_boundaries.append({
                            "text": word,
                            "offset": accumulated_duration + wi * avg_word_duration,
                            "duration": avg_word_duration,
                        })

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
