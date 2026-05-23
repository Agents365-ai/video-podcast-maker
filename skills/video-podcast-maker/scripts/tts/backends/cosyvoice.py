"""Alibaba CosyVoice TTS backend."""
import os
import re
import sys
import time
from .base import check_resume


def synthesize(chunks, config, output_dir, resume=False):
    """Synthesize using CosyVoice with word-level timestamps.

    config keys: speech_rate, phoneme_dict
    """
    import struct
    import json as _json
    from dashscope.audio.tts_v2 import SpeechSynthesizer, ResultCallback, AudioFormat

    speech_rate = config.get('speech_rate', '+5%')
    rate_match = re.match(r'([+-]?\d+)%', speech_rate)
    cosy_rate = 1.0 + int(rate_match.group(1)) / 100.0 if rate_match else 1.0
    cosy_rate = max(0.5, min(2.0, cosy_rate))

    model = os.environ.get("COSYVOICE_MODEL", "cosyvoice-v3-flash")
    voice = os.environ.get("COSYVOICE_VOICE", "longxiaochun_v3")
    sample_rate = 48000

    phoneme_dict = config.get('phoneme_dict', {})
    if phoneme_dict:
        print("Warning: CosyVoice does not currently apply phoneme SSML. "
              "Inline markers and phonemes.json will be ignored. "
              "Consider using Azure for full phoneme support.", file=sys.stderr)

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
                audio_buf = bytearray()
                sentence_words = {}

                class Callback(ResultCallback):
                    def on_event(self, message):
                        d = _json.loads(message)
                        sentence = d.get('payload', {}).get('output', {}).get('sentence', {})
                        words = sentence.get('words', [])
                        idx = sentence.get('index', 0)
                        if words:
                            sentence_words[idx] = words
                    def on_data(self, data):
                        audio_buf.extend(data)
                    def on_error(self, message):
                        raise RuntimeError(f"CosyVoice error: {message}")

                synth = SpeechSynthesizer(
                    model=model,
                    voice=voice,
                    format=AudioFormat.PCM_48000HZ_MONO_16BIT,
                    speech_rate=cosy_rate,
                    callback=Callback(),
                    additional_params={'word_timestamp_enabled': True},
                )
                synth.streaming_call(chunk)
                synth.streaming_complete()

                if not audio_buf:
                    raise RuntimeError("No audio data received")

                pcm_data = bytes(audio_buf)
                data_size = len(pcm_data)
                wav_header = struct.pack('<4sI4s4sIHHIIHH4sI',
                    b'RIFF', 36 + data_size, b'WAVE',
                    b'fmt ', 16, 1, 1, sample_rate,
                    sample_rate * 2, 2, 16,
                    b'data', data_size)
                with open(part_file, 'wb') as f:
                    f.write(wav_header + pcm_data)

                chunk_duration = data_size / (sample_rate * 2)

                for idx in sorted(sentence_words.keys()):
                    for w in sentence_words[idx]:
                        word_boundaries.append({
                            "text": w["text"],
                            "offset": accumulated_duration + w["begin_time"] / 1000.0,
                            "duration": (w["end_time"] - w["begin_time"]) / 1000.0,
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
