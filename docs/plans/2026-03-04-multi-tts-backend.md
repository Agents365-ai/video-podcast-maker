# Multi-TTS Backend (Azure + CosyVoice) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add CosyVoice as an alternative TTS backend to `generate_tts.py`, switchable via `TTS_BACKEND` env var, while keeping Azure as default.

**Architecture:** Single `generate_tts.py` with backend dispatch. Shared code (section parsing, phoneme handling, chunking, SRT generation, timing.json) stays unchanged. Only the TTS synthesis loop (lines 311-363) gets extracted into backend-specific functions that return a common `(part_files, word_boundaries, total_duration)` tuple.

**Tech Stack:** DashScope Python SDK (`dashscope`), CosyVoice v3-flash model

---

### Task 1: Add `--backend` argument and `TTS_BACKEND` env var

**Files:**
- Modify: `generate_tts.py:154-169`

**Step 1: Add backend argument to argparse**

Add `--backend` arg after line 160, and move Azure key validation to be conditional:

```python
parser.add_argument('--backend', '-b', default=None,
    help='TTS backend: azure or cosyvoice (default: env TTS_BACKEND or azure)')
```

**Step 2: Replace hardcoded Azure key check with backend dispatch**

Replace lines 164-169 with:

```python
BACKEND = args.backend or os.environ.get("TTS_BACKEND", "azure")
print(f"TTS backend: {BACKEND}")

if BACKEND == "azure":
    key = os.environ.get("AZURE_SPEECH_KEY")
    region = os.environ.get("AZURE_SPEECH_REGION", "eastasia")
    if not key:
        print("Error: AZURE_SPEECH_KEY not set", file=sys.stderr)
        sys.exit(1)
elif BACKEND == "cosyvoice":
    if not os.environ.get("DASHSCOPE_API_KEY"):
        print("Error: DASHSCOPE_API_KEY not set", file=sys.stderr)
        sys.exit(1)
else:
    print(f"Error: Unknown backend '{BACKEND}'. Use 'azure' or 'cosyvoice'", file=sys.stderr)
    sys.exit(1)
```

**Step 3: Move Azure import to conditional**

Replace line 10 (`import azure.cognitiveservices.speech as speechsdk`) with lazy import inside the Azure synthesis function (Task 2).

**Step 4: Verify script still works with `--backend azure`**

Run: `python3 generate_tts.py --help`
Expected: Shows `--backend` option with azure/cosyvoice choices

**Step 5: Commit**

```bash
git add generate_tts.py
git commit -m "feat: add --backend arg and TTS_BACKEND env var for multi-TTS support"
```

---

### Task 2: Extract Azure synthesis into function

**Files:**
- Modify: `generate_tts.py:257-363`

**Step 1: Create `synth_azure()` function**

Wrap lines 311-363 (Azure TTS synthesis loop) into a function. Move the Azure import inside it. The function receives chunks, phoneme_dict, speech_rate, output_dir and returns `(part_files, word_boundaries, total_duration)`:

```python
def synth_azure(chunks, phoneme_dict, speech_rate, output_dir):
    import azure.cognitiveservices.speech as speechsdk

    config = speechsdk.SpeechConfig(subscription=key, region=region)
    config.SpeechSynthesisVoiceName = "zh-CN-XiaoxiaoMultilingualNeural"
    part_files = []
    word_boundaries = []
    accumulated_duration = 0

    for i, chunk in enumerate(chunks):
        part_file = os.path.join(output_dir, f"part_{i}.wav")
        part_files.append(part_file)
        audio = speechsdk.audio.AudioOutputConfig(filename=part_file)
        synth = speechsdk.SpeechSynthesizer(speech_config=config, audio_config=audio)

        def word_boundary_cb(evt):
            word_boundaries.append({
                "text": evt.text,
                "offset": accumulated_duration + evt.audio_offset / 10000000.0,
                "duration": evt.duration.total_seconds(),
            })
        synth.synthesis_word_boundary.connect(word_boundary_cb)

        chunk_with_phonemes = apply_phonemes(chunk, phoneme_dict)
        processed = mark_english_terms(chunk_with_phonemes)

        ssml = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"
                   xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="zh-CN">
            <voice name="zh-CN-XiaoxiaoMultilingualNeural">
                <mstts:express-as style="gentle">
                    <prosody rate="{speech_rate}">{processed}</prosody>
                </mstts:express-as>
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
```

**Step 2: Replace inline Azure code with function call**

Replace lines 311-363 with:

```python
# TTS synthesis
if BACKEND == "azure":
    part_files, word_boundaries, total_duration = synth_azure(chunks, phoneme_dict, SPEECH_RATE, args.output_dir)
elif BACKEND == "cosyvoice":
    part_files, word_boundaries, total_duration = synth_cosyvoice(chunks, phoneme_dict, SPEECH_RATE, args.output_dir)
```

**Step 3: Test Azure still works**

Run with a short test file to verify refactoring didn't break anything.

**Step 4: Commit**

```bash
git add generate_tts.py
git commit -m "refactor: extract Azure TTS synthesis into synth_azure function"
```

---

### Task 3: Implement CosyVoice synthesis function

**Files:**
- Modify: `generate_tts.py` (add `synth_cosyvoice()` after `synth_azure()`)

**Step 1: Add `synth_cosyvoice()` function**

```python
def synth_cosyvoice(chunks, phoneme_dict, speech_rate, output_dir):
    from dashscope.audio.tts import SpeechSynthesizer, ResultCallback

    # Convert speech rate from Azure format "+5%" to CosyVoice format 1.05
    rate_match = re.match(r'([+-]?\d+)%', speech_rate)
    cosy_rate = 1.0 + int(rate_match.group(1)) / 100.0 if rate_match else 1.0
    cosy_rate = max(0.5, min(2.0, cosy_rate))

    model = os.environ.get("COSYVOICE_MODEL", "cosyvoice-v3-flash")
    voice = os.environ.get("COSYVOICE_VOICE", "longxiaochun_v2")

    part_files = []
    word_boundaries = []
    accumulated_duration = 0

    for i, chunk in enumerate(chunks):
        part_file = os.path.join(output_dir, f"part_{i}.wav")
        part_files.append(part_file)

        # Collect audio data and timestamps via callback
        audio_data = bytearray()
        timestamps = []

        class Callback(ResultCallback):
            def on_event(self, result):
                if result.get_audio_frame():
                    audio_data.extend(result.get_audio_frame())
                ts = result.get_timestamp()
                if ts:
                    timestamps.append(ts)

            def on_error(self, response):
                raise RuntimeError(f"CosyVoice error: {response}")

        success = False
        for attempt in range(1, 4):
            try:
                audio_data.clear()
                timestamps.clear()
                SpeechSynthesizer.call(
                    model=model,
                    text=chunk,
                    voice=voice,
                    sample_rate=48000,
                    format='wav',
                    rate=cosy_rate,
                    word_timestamp_enabled=True,
                    callback=Callback(),
                )

                with open(part_file, 'wb') as f:
                    f.write(bytes(audio_data))

                # Get duration from wav file
                import wave
                with wave.open(part_file, 'rb') as wf:
                    frames = wf.getnframes()
                    rate = wf.getframerate()
                    chunk_duration = frames / float(rate)

                # Convert CosyVoice timestamps to word_boundaries format
                # CosyVoice returns character-level timestamps
                if timestamps:
                    for ts in timestamps:
                        # Adapt timestamp format - structure TBD based on actual API response
                        # Expected: list of {word, begin_time, end_time} or similar
                        if isinstance(ts, list):
                            for item in ts:
                                word_boundaries.append({
                                    "text": item.get("text", item.get("word", "")),
                                    "offset": accumulated_duration + item.get("begin_time", 0) / 1000.0,
                                    "duration": (item.get("end_time", 0) - item.get("begin_time", 0)) / 1000.0,
                                })
                        elif isinstance(ts, dict):
                            word_boundaries.append({
                                "text": ts.get("text", ts.get("word", "")),
                                "offset": accumulated_duration + ts.get("begin_time", 0) / 1000.0,
                                "duration": (ts.get("end_time", 0) - ts.get("begin_time", 0)) / 1000.0,
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
```

**Step 2: Test with CosyVoice backend**

Create a minimal test file:
```bash
echo "[SECTION:hero]\nHello world, this is a test." > /tmp/test_podcast.txt
TTS_BACKEND=cosyvoice python3 generate_tts.py --input /tmp/test_podcast.txt --output-dir /tmp/tts_test
```

Inspect the timestamp format from CosyVoice and adjust the timestamp conversion code in `synth_cosyvoice()` if needed.

**Step 3: Commit**

```bash
git add generate_tts.py
git commit -m "feat: add CosyVoice TTS backend via DashScope SDK"
```

---

### Task 4: Update documentation and dependencies

**Files:**
- Modify: `requirements.txt`
- Modify: `CLAUDE.md:55-60` (Key Commands section)
- Modify: `SKILL.md:482-487` (Step 8)
- Modify: `README.md` (Environment Variables section)

**Step 1: Update requirements.txt**

```
azure-cognitiveservices-speech
dashscope
requests
```

**Step 2: Update CLAUDE.md Key Commands**

Add CosyVoice variant under TTS section:

```bash
# TTS with CosyVoice (alternative)
TTS_BACKEND=cosyvoice python3 generate_tts.py --input videos/{name}/podcast.txt --output-dir videos/{name}
```

**Step 3: Update SKILL.md Step 8**

Add backend selection note:

```markdown
## Step 8: Generate TTS Audio

```bash
cp ~/.claude/skills/video-podcast-maker/generate_tts.py .
python3 generate_tts.py --input videos/{name}/podcast.txt --output-dir videos/{name}

# Or use CosyVoice backend (requires DASHSCOPE_API_KEY)
TTS_BACKEND=cosyvoice python3 generate_tts.py --input videos/{name}/podcast.txt --output-dir videos/{name}
```
```

**Step 4: Update CLAUDE.md Environment Variables**

Add:
```bash
export DASHSCOPE_API_KEY="..."     # Required for CosyVoice TTS backend
```

**Step 5: Commit**

```bash
git add requirements.txt CLAUDE.md SKILL.md README.md
git commit -m "docs: add CosyVoice backend to TTS documentation and dependencies"
```

---

## Notes

- **Timestamp format uncertainty**: CosyVoice's `get_timestamp()` return format needs verification during implementation. The `synth_cosyvoice()` function includes defensive handling for both list and dict formats. Adjust after first successful API call.
- **Phoneme/SSML**: CosyVoice v3-flash supports SSML with `enable_ssml=True`. If phoneme correction is needed, a follow-up task can add SSML processing for CosyVoice (different alphabet than Azure's SAPI format). For now, CosyVoice uses plain text without phoneme tags — CosyVoice's native Chinese pronunciation is generally better than Azure's.
- **No `mark_english_terms()` for CosyVoice**: CosyVoice handles mixed Chinese-English text natively without needing `<lang>` SSML tags.
- **Chunk size**: CosyVoice limit is 2000 chars per call vs current 400 for Azure. Keep 400 for consistency and reliable timestamps.
