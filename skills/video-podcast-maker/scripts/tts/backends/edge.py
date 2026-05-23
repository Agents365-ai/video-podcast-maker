"""Microsoft Edge TTS backend (free, no API key needed)."""
import os
import subprocess
import time
from .base import check_resume


def synthesize(chunks, config, output_dir, resume=False):
    """Synthesize using Edge TTS with word boundary tracking.

    config keys: voice, speech_rate, phoneme_dict
    """
    import asyncio
    import edge_tts

    voice = config.get('voice', 'zh-CN-XiaoxiaoNeural')
    speech_rate = config.get('speech_rate', '+5%')
    part_files = []
    word_boundaries = []
    accumulated_duration = 0

    async def synthesize_chunk(i, chunk):
        nonlocal accumulated_duration
        part_file = os.path.join(output_dir, f"part_{i}.wav")
        part_files.append(part_file)

        if resume:
            dur = check_resume(part_file)
            if dur is not None:
                print(f"  ⏭ Part {i + 1}/{len(chunks)} skipped (resume, {dur:.1f}s)")
                accumulated_duration += dur
                return

        mp3_file = part_file.replace('.wav', '.mp3')

        success = False
        for attempt in range(1, 4):
            try:
                audio_data = bytearray()
                chunk_words = []

                communicate = edge_tts.Communicate(
                    chunk, voice=voice, rate=speech_rate, boundary='WordBoundary')

                async for event in communicate.stream():
                    if event["type"] == "audio":
                        audio_data.extend(event["data"])
                    elif event["type"] == "WordBoundary":
                        chunk_words.append({
                            "text": event["text"],
                            "offset": accumulated_duration + event["offset"] / 10_000_000,
                            "duration": event["duration"] / 10_000_000,
                        })

                if not audio_data:
                    raise RuntimeError("No audio data received")

                with open(mp3_file, 'wb') as f:
                    f.write(bytes(audio_data))
                subprocess.run(
                    ["ffmpeg", "-y", "-i", mp3_file, "-ar", "48000", "-ac", "1", part_file],
                    capture_output=True)
                os.remove(mp3_file)

                probe = subprocess.run(
                    ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", part_file],
                    capture_output=True, text=True)
                chunk_duration = float(probe.stdout.strip())

                word_boundaries.extend(chunk_words)
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

    async def run_all():
        for i, chunk in enumerate(chunks):
            await synthesize_chunk(i, chunk)

    asyncio.run(run_all())
    return part_files, word_boundaries, accumulated_duration
