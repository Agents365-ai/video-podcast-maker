"""Azure Cognitive Services TTS backend."""
import os
import time
from ..phonemes import apply_phonemes
from ..ssml import mark_english_terms, wrap_mode_for
from .base import check_resume


def synthesize(chunks, config, output_dir, resume=False):
    """Synthesize using Azure TTS with word boundary tracking.

    config keys: key, region, voice, speech_rate, phoneme_dict
    """
    import azure.cognitiveservices.speech as speechsdk

    speech_config = speechsdk.SpeechConfig(subscription=config['key'], region=config['region'])
    voice = config.get('voice', 'zh-CN-XiaoxiaoNeural')
    speech_config.SpeechSynthesisVoiceName = voice
    part_files = []
    word_boundaries = []
    accumulated_duration = 0
    speech_rate = config.get('speech_rate', '+5%')
    phoneme_dict = config.get('phoneme_dict', {})
    style = config.get('style', 'gentle')  # empty string disables express-as

    for i, chunk in enumerate(chunks):
        part_file = os.path.join(output_dir, f"part_{i}.wav")
        part_files.append(part_file)

        if resume:
            dur = check_resume(part_file)
            if dur is not None:
                print(f"  ⏭ Part {i + 1}/{len(chunks)} skipped (resume, {dur:.1f}s)")
                accumulated_duration += dur
                continue

        audio = speechsdk.audio.AudioOutputConfig(filename=part_file)
        synth = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio)

        chunk_start = accumulated_duration  # snapshot for closure
        def word_boundary_cb(evt, _start=chunk_start):
            word_boundaries.append({
                "text": evt.text,
                "offset": _start + evt.audio_offset / 10000000.0,
                "duration": evt.duration.total_seconds(),
            })
        synth.synthesis_word_boundary.connect(word_boundary_cb)

        chunk_with_phonemes = apply_phonemes(chunk, phoneme_dict)
        processed = mark_english_terms(chunk_with_phonemes, mode=wrap_mode_for('azure', voice))

        prosody_block = f'<prosody rate="{speech_rate}">{processed}</prosody>'
        # Multilingual voices have inconsistent style support — when style produces
        # vocoder artifacts, disable via TTS_STYLE="". Skipping the wrapper keeps
        # natural neural prosody and avoids hoarse/strained transitions.
        if style:
            inner = f'<mstts:express-as style="{style}">{prosody_block}</mstts:express-as>'
        else:
            inner = prosody_block
        ssml = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"
                   xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="zh-CN">
            <voice name="{voice}">
                {inner}
            </voice>
        </speak>"""

        success = False
        for attempt in range(1, 4):
            result = synth.speak_ssml_async(ssml).get()
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                chunk_duration = result.audio_duration.total_seconds()
                print(f"  ✓ Part {i + 1}/{len(chunks)} done ({len(chunk)} chars, {chunk_duration:.1f}s)")
                accumulated_duration += chunk_duration
                success = True
                break
            else:
                details = result.cancellation_details.error_details
                print(f"  ✗ Part {i + 1} failed (attempt {attempt}/3): {details}")
                if attempt < 3:
                    time.sleep(attempt * 2)

        if not success:
            raise RuntimeError(f"Part {i + 1} synthesis failed")

    return part_files, word_boundaries, accumulated_duration
