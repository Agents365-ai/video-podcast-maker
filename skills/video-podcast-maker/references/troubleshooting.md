# Video Podcast Maker — Troubleshooting & Reference

> **When to load:** Load this file when encountering errors, when the user asks about preferences, or when the user asks about BGM options.

## Contents

- [Discovery (when you're not sure which script to run)](#discovery-when-youre-not-sure-which-script-to-run) — `cli.py` entry point + envelope error codes
- [Troubleshooting](#troubleshooting) — TTS, FFmpeg, Remotion, encoding, audio-sync fixes
- [Azure TTS Deep-Dive](#azure-tts-deep-dive) — voice selection, SSML pitfalls, style matrix, hoarse/glitchy audio triage
- [Background Music Options](#background-music-options)
- [Preference Commands](#preference-commands)
- [Preference Learning](#preference-learning)
- [Design Learning Troubleshooting](#design-learning-troubleshooting)

## Discovery (when you're not sure which script to run)

The suite is reachable through one hierarchical entry point at `scripts/cli.py`:

```bash
python3 scripts/cli.py --help                       # 11 resources
python3 scripts/cli.py <resource> --help            # actions for one resource
python3 scripts/cli.py <resource> <action> --help   # full args (forwards to underlying script)
python3 scripts/cli.py schema                       # JSON list of all 20 methods
python3 scripts/cli.py schema <method>              # typed parameter schema for one method
```

When a script fails with a structured envelope (most do — see `--format json`), the `code` field tells an agent how to recover: `input_not_found`, `input_invalid`, `auth_missing_env`, `tool_missing`, `validation_failed`, `confirmation_required`, `ffmpeg_failed`, `backend_failed`, `internal_error`. Direct invocations (`python3 scripts/<name>.py ...`) still work — the dispatcher is additive.

Routes: `tts run|validate`, `verify`, `align`, `audit beats`, `shorts gen`, `design list|show|delete|add`, `assets init|add|list|validate`, `prereqs`, `capabilities`, `prefs get|migrate|backend|bgm-path`, `schema [<method>]`.

## Troubleshooting

### TTS: Azure API Key Error

**Symptoms**: `Error: Authentication failed`, `HTTP 401 Unauthorized`

**Solution**:

```bash
echo $AZURE_SPEECH_KEY
echo $AZURE_SPEECH_REGION

export AZURE_SPEECH_KEY="your-key-here"
export AZURE_SPEECH_REGION="eastasia"
```

---

### FFmpeg: BGM Mixing Issues

**Symptoms**: BGM too loud over voice, BGM ends abruptly

**Solution**:

```bash
# Basic mix (voice primary, BGM lowered)
ffmpeg -i voice.mp3 -i bgm.mp3 \
  -filter_complex "[0:a]volume=1.0[voice];[1:a]volume=0.15[bgm];[voice][bgm]amix=inputs=2:duration=first" \
  -ac 2 output.mp3

# With fade in/out
ffmpeg -i voice.mp3 -i bgm.mp3 \
  -filter_complex "
    [0:a]volume=1.0[voice];
    [1:a]volume=0.15,afade=t=in:st=0:d=2,afade=t=out:st=58:d=2[bgm];
    [voice][bgm]amix=inputs=2:duration=first
  " output.mp3
```

---

### Remotion: Render Out of Memory

**Symptoms**: `FATAL ERROR: CALL_AND_RETRY_LAST Allocation failed`, render crashes at ~50%

**Solution**:

```bash
# Reduce parallelism
npx remotion render ... --concurrency 1

# Or increase Node memory
NODE_OPTIONS="--max-old-space-size=8192" npx remotion render ...
```

---

### Remotion: Black Screen / No Content

**Symptoms**: Output video is all black or all white, no visual elements

**Solution**:

1. Verify `timing.json` exists in `videos/{name}/` and has correct `start_frame`/`duration_frames`
2. Check composition ID matches: `npx remotion render ... CompositionId` must match Root.tsx registration
3. Ensure `--public-dir videos/{name}/` is passed to all Remotion commands
4. Check browser console in `npx remotion studio` for JS errors

---

### Remotion: Command Not Found

**Symptoms**: `npx: command not found` or `remotion: not found`

**Solution**:

```bash
# Ensure you're in the Remotion project directory
cd your-remotion-project
npm i   # reinstall dependencies
npx remotion --version  # verify
```

---

### timing.json: Parse Error

**Symptoms**: `SyntaxError: Unexpected token`, sections missing or misaligned

**Solution**:

```bash
# Validate JSON
python3 -c "import json; json.load(open('videos/{name}/timing.json'))"

# Check section names match podcast.txt [SECTION:xxx] markers
```

Common cause: section name in `podcast.txt` doesn't match the composition code.

---

### SRT: Garbled Chinese Characters

**Symptoms**: Subtitles show `???` or mojibake

**Solution**:

```bash
# Check encoding
file videos/{name}/podcast_audio.srt
# Should show: UTF-8 Unicode text

# Convert if needed
iconv -f GBK -t UTF-8 videos/{name}/podcast_audio.srt > videos/{name}/podcast_audio_utf8.srt
mv videos/{name}/podcast_audio_utf8.srt videos/{name}/podcast_audio.srt
```

---

### Disk Space: 4K Render Fails

**Symptoms**: Render stops partway, `No space left on device`

**Solution**: 4K render needs ~10-20GB free space. Check with `df -h .` before rendering. Clean up old video outputs or use `--scale 0.5` for 1080p.

---

### Font Not Found (Linux)

**Symptoms**: Text renders in fallback font, Chinese characters show as boxes

**Solution**:

```bash
# Install Noto Sans SC
sudo apt install fonts-noto-cjk
# Or download PingFang SC manually
```

---

### Remotion: Chrome Headless Shell Re-Downloads Every Run

**Symptoms**: `npx remotion still ...` or `npx remotion render` takes 30s+ before starting, downloads a 90 MB Chrome zip every invocation.

**Cause**: The headless browser cache (`node_modules/.remotion/`) is missing the `VERSION` file, so Remotion thinks the browser isn't installed. This happens when the zip extraction was interrupted (e.g., by a session exit mid-download).

**Solution**: Copy the working browser cache from an existing project:

```bash
cp -r ~/path/to/existing-project/node_modules/.remotion/mac-arm64 \
     node_modules/.remotion/
```

Or delete the cache and let it download once cleanly:

```bash
rm -rf node_modules/.remotion
npx remotion still src/remotion/index.ts MyVideo videos/test.png --public-dir videos/test/ --frame 0
```

---

### TTS: Section Timing Mismatch (Word Boundaries)

**Symptoms**: `timing.json` shows wrong durations for some sections (e.g., a short paragraph gets 52s, a long one gets 31s). Console shows `⚠ 估算, 未找到:` warnings.

**Cause**: The section matcher tries to find each section's first text in the word-boundary stream. Some TTS backends return word boundaries in spoken form (e.g., MiniMax returns "三十七" for "37"), which won't match the written form in `podcast.txt`. The matcher falls back to estimation, which can be inaccurate.

**Solution**: After TTS, always verify section timing alignment:

```bash
python3 -c "import json; t=json.load(open('videos/{name}/timing.json')); [print(f\"{s['name']:20s} {s['duration']:.1f}s\") for s in t['sections']]"
```

If durations don't match paragraph lengths, re-run with a different backend or accept estimation (the total duration is always correct). For the current run, the SRT and audio are still valid — only `timing.json` section boundaries may need manual adjustment in the composition.

---

### Edge TTS: No Audio Output

**Symptoms**: Empty or zero-length WAV file, no error message

**Solution**: Edge TTS requires internet access (uses Microsoft's online TTS service). Check network connectivity. No API key needed.

---

### Quick Checklists

**Pre-render**:

- [ ] All asset files exist
- [ ] timing.json format correct
- [ ] Audio duration matches timing
- [ ] Environment variables set
- [ ] Disk space sufficient (>20GB for 4K)

**Post-render**:

- [ ] Video duration correct
- [ ] Audio-video sync
- [ ] Subtitles display correctly
- [ ] No black/blank frames

---

## Azure TTS Deep-Dive

> **When to load:** When choosing voice/style for the Azure backend, or when debugging hoarse / missing / glitchy audio. Skip for other backends.
>
> Since v4.0.0 Azure synthesis (SSML building, phoneme tags, English-term wrapping) runs inside the **ttscn component skill** — but everything below still applies: voice choice, `TTS_STYLE`, and phoneme behavior ride through the bridge via env vars and `phonemes_resolved.json`.

The Azure neural-TTS engine is excellent in the common path but has several deterministic failure modes that have wasted hours of iteration. This section documents the known traps and how to avoid them.

### Voice selection

#### Default: `zh-CN-XiaoxiaoNeural` (standard)

Use this for **content that is mostly Chinese with rare English abbreviations** (AI, ML, GPT, CLI, API, etc.). Chinese listeners read these abbreviations as letter-by-letter Chinese phonetics ("ei-ai", "em-el") in normal conversation — the standard voice produces exactly that, with no language switch and no artifacts.

#### Use `zh-CN-XiaoxiaoMultilingualNeural` ONLY when

- The script contains **substantial English passages** (sentences, paragraphs, dialogue)
- Heavy technical content with **proper nouns that genuinely need English pronunciation** (e.g. "Visual Studio Code", "Final Cut Pro", spoken URLs)
- Mixed bilingual narration where English flow matters

#### Multilingual voice known issues

| Issue | Manifestation | Workaround |
| --- | --- | --- |
| **Vocoder artifact at lang switch** | Hoarse / strained sound when going Chinese-tone → English-letter → Chinese-consonant. E.g. "观点是，AI让答案" → "AI" sounds glitched | Switch to standard voice. Or rewrite phrase to avoid bare English token after Chinese tonal particle. |
| **SAPI phoneme tags are silently dropped** | `<phoneme alphabet="sapi" ph="ka 3 zhu 4">卡住</phoneme>` — surrounding text gets eaten, only tag content survives | Use standard voice (better SAPI support). Or remove inline phoneme markers — Azure usually pronounces common multi-character words correctly without override. |
| **Style support is inconsistent** | `style="serious"` / `"newscast"` may produce strained/hoarse output | Use empty `TTS_STYLE=""` to disable express-as wrapper; or stick to `gentle` / `cheerful`. |
| **Word boundary timing** | `result.audio_duration` may under-report when `<break>` / `<phoneme>` present | Reconciled automatically by `reconcile_timing_with_wav` in `srt.py` |

#### Picking voice from content

The `tts/voice_advisor.py` module analyses your script and prints a recommendation at TTS startup. Heed its warnings. Override via `TTS_VOICE` env var if you disagree.

### SSML pitfalls

#### `<phoneme>` for Chinese with multilingual voice → text loss

**Symptom**: A line like "你没有被细节卡住" plays as only "卡住" — the preceding "你没有被细节" is missing from the audio.

**Cause**: Inline `卡住[kǎ zhù]` becomes `<phoneme alphabet="sapi" ph="ka 3 zhu 4">卡住</phoneme>`. Multilingual voice's SSML parser doesn't fully support SAPI Chinese phonemes; it silently drops the surrounding text in the same prosody block.

**Fix**:

1. Switch to standard `zh-CN-XiaoxiaoNeural` (better SAPI support), OR
2. Remove the `[pinyin]` annotation — Azure usually gets common compounds (重新, 卡住, 好的, 还是) right by default.

#### `<break>` and `<phoneme>` skew duration accounting

**Symptom**: After regen, `timing.json` total is ~250s but the actual WAV is ~258s. Last sections get truncated in Remotion render.

**Cause**: Azure's `result.audio_duration` may exclude `<break>` time and under-report `<phoneme>` duration.

**Fix**: Already automated. `generate_tts.py` calls `reconcile_timing_with_wav` after concat, ffprobing the actual file and rescaling sections proportionally if drift > 0.5s.

#### `<say-as interpret-as="characters">` nested in `<lang>` — undefined behaviour

**Symptom**: `<say-as>` appears to have no effect or produces unexpected output.

**Cause**: Under Multilingual voice, `mark_english_terms` runs in `aggressive` mode and wraps single English words in `<lang xml:lang="en-US">`. Pre-writing `<say-as>` around the same word produces `<say-as><lang>Word</lang></say-as>` — Azure picks one or the other unpredictably.

**Fix**: Avoid `<say-as>` for English tokens — let voice selection (above) handle it.

### How English-term wrapping works

English-term wrapping (`<lang xml:lang="en-US">` around brand phrases and, on Multilingual voices, longer English words) is performed by the ttscn azure adapter, not by this skill. The behavior to expect:

| Voice | What gets wrapped |
| --- | --- |
| Standard `zh-CN-XiaoxiaoNeural` | Brand / proper-noun phrases only (Visual Studio Code, Andrew Ng, Apple Intelligence, …). Bare abbreviations (AI, ML, GPT, CLI, API) are left alone — standard voice reads them as natural Chinese letter pronunciations. |
| `zh-CN-XiaoxiaoMultilingualNeural` | Brand phrases + single English words that look like real words (≥5 chars, lowercase letters, not common abbreviations like JSON/HTTPS). Bare abbreviations still skipped. |
| Non-azure platforms | Nothing — they consume plain text; ttscn strips or ignores SSML for them. |

To force a one-off proper-noun pronunciation in a single script, hand-write `<lang xml:lang="en-US">…</lang>` directly in `podcast.txt` (azure platform only), or prefer an inline `[pinyin]` marker / `phonemes.json` entry, which works through the phoneme path.

### Style support matrix

These styles are reliably supported on `zh-CN-XiaoxiaoNeural`:

| Style | Use for | Note |
| --- | --- | --- |
| `gentle` (default) | General narration | Safe default |
| `cheerful` | Light/positive tone | Energetic |
| `serious` | News, professional | Punchy |
| `newscast` | Reporting style | Steady cadence |
| `calm` | Slow-paced explainer | Soothing |
| `chat` | Casual conversation | Natural pause |
| (empty `""`) | Disable wrapper | When any style produces artifacts |

For Multilingual voice, restrict to `gentle` or `""`. Other styles are inconsistent.

Set per-run via env: `TTS_STYLE=cheerful python3 generate_tts.py ...` or persist in `user_prefs.json` → `global.tts.style`.

### Quick triage checklist

Hearing weird audio at a specific timestamp?

1. **Locate the bad word in `podcast_audio.srt`** (timestamp ranges → words said when)
2. **Check the surrounding context** — Chinese tonal particle + bare English letter is the #1 hoarse trigger on Multilingual voice
3. **Run voice advisor** — if it suggests standard voice and you're on Multilingual, switch
4. **Inspect inline phoneme markers near the bad word** — remove if any
5. **Try `TTS_STYLE=""`** — disable express-as wrapper as a low-risk first try
6. **Last resort**: substitute that one Chinese homophone for the bare English token (e.g. `AI` → `诶艾`). Surgical, audible difference is zero for Chinese listeners.

---

## Background Music Options

### Included Tracks

Available at `${SKILL_DIR}/assets/`:

| Track | Mood | Best For |
|-------|------|----------|
| `perfect-beauty-191271.mp3` | Upbeat, positive | Tech demos, product intros, tutorials |
| `snow-stevekaldes-piano-397491.mp3` | Calm piano | Reflective topics, analysis, comparisons |

### Using Custom BGM

```bash
cp /path/to/my-bgm.mp3 videos/{name}/bgm.mp3
```

If user says "use my own BGM" or provides a file path, skip the default BGM copy in Step 11.

### Royalty-Free BGM Sources

| Source | URL | License |
| -------- | ----- | --------- |
| Pixabay Music | <https://pixabay.com/music/> | Free, no attribution |
| Free Music Archive | <https://freemusicarchive.org/> | CC licenses |
| Incompetech | <https://incompetech.com/> | CC BY (attribution) |
| Uppbeat | <https://uppbeat.io/> | Free tier available |
| Chosic | <https://www.chosic.com/free-music/all/> | Various CC |

### BGM Selection Guide

| Video Type | Recommended Mood | Volume |
| ------------ | ----------------- | -------- |
| Tech/coding | Lo-fi, ambient | 0.03-0.05 |
| Product review | Upbeat, corporate | 0.05-0.08 |
| News/analysis | Neutral, minimal | 0.03-0.05 |
| Tutorial | Calm, steady | 0.04-0.06 |
| Lifestyle | Warm, acoustic | 0.05-0.08 |

**Agent behavior:** In auto mode, select most appropriate included track by topic type. In interactive mode, ask user.

---

## Preference Commands

Users can manage preferences in conversation:

### View Preferences

User says: "show preferences" / "显示偏好设置"

The agent outputs the current settings summary (visual, TTS, content, topic patterns, learning history count).

### Reset Preferences

User says: "reset preferences" / "重置偏好"

```bash
cp ${SKILL_DIR}/user_prefs.template.json ${SKILL_DIR}/user_prefs.json
echo "✓ Preferences reset to defaults"
```

### Save Current Settings

User says: "save this as tech default" / "把这个设置保存为科技类默认"

The agent extracts current visual/TTS/content settings and updates `topic_patterns.tech`.

### Manual Preference Setting

User says: "set speech rate to +10%" / "dark theme as default" / "title always 100px"

The agent directly updates the corresponding field in `user_prefs.json`.

### Platform & Language Commands

| User Says | Action |
| ----------- | -------- |
| "set platform youtube" | Update `global.platform` to `"youtube"` |
| "set platform bilibili" | Update `global.platform` to `"bilibili"` |
| "set platform xiaohongshu" | Update `global.platform` to `"xiaohongshu"` |
| "set platform douyin" | Update `global.platform` to `"douyin"` |
| "set platform weixin-channels" | Update `global.platform` to `"weixin-channels"` |
| "set language en-US" | Update `global.language` to `"en-US"` |
| "set language zh-CN" | Update `global.language` to `"zh-CN"` |
| "show platform" | Show current platform and language |
| "disable subtitles" | Set `global.subtitle.enabled` to `false` |
| "enable subtitles" | Set `global.subtitle.enabled` to `true` |
| "set subtitle font Arial" | Set `global.subtitle.fontName` to `"Arial"` |
| "set subtitle size 24" | Set `global.subtitle.fontSize` to `24` |
| "set CTA text" | Set `global.cta.type` to `"text"` |
| "set CTA animation" | Set `global.cta.type` to `"animation"` |
| "enable chapters" | Set `global.content.chapters` to `true` |
| "disable chapters" | Set `global.content.chapters` to `false` |

---

## Preference Learning

Preferences are set manually via the commands above.

---

## Design Learning Troubleshooting

### "ffmpeg not found" when learning from video

Install ffmpeg: `brew install ffmpeg` (macOS) or use image input instead.

### Playwright fails on Bilibili/YouTube

URL extraction is experimental. Fallback options:

1. Download the video and use: `learn ./video.mp4`
2. Take screenshots manually and use: `learn ./screenshot1.png ./screenshot2.png`

### Vision analysis colors look wrong

Color values from image analysis are approximate. After reviewing the report:

- Adjust colors manually: edit report.json or override when creating the style profile
- Use a color picker tool on the screenshots for precise hex values

### Style profile not applied

Check priority chain: `style_profiles` only override when explicitly specified by name.
Verify: `python3 scripts/learn_design.py --list` shows the reference exists.
Verify: `user_prefs.json` → `style_profiles` → your profile name exists with correct props_override.

### Orphaned references (deleted directory but still in index)

Run `references list` — orphaned entries are auto-cleaned on list.

---

### Phoneme Support by Platform

**Symptoms**: Inline phoneme markers `执行器[zhí xíng qì]` and `phonemes.json` entries are ignored.

**Explanation**: The phoneme dictionary is passed to ttscn, which applies it only on platforms with a pronunciation-override mechanism: `azure` (SSML `<phoneme>`) and `minimax` (pinyin annotations). All other platforms consume plain text and ignore the file.

**Workaround**: If pronunciation accuracy is critical, use `TTS_BACKEND=azure` or `TTS_BACKEND=minimax`.

---

### Word-Boundary Precision by Platform

- **Native per-word timings**: only platforms with boundary events (`edge`, `azure`, `doubao`, `minimax`, `cosyvoice` — ttscn ≥1.5.0 for doubao/minimax, ≥1.6.0 for cosyvoice) — ttscn returns them and the bridge shifts offsets per chunk
- **All other platforms**: subtitle timing is estimated by distributing each measured chunk duration across its characters (chunks are capped at 400 chars to bound the error)
- **Workaround**: If subtitle precision is critical, use one of the native-boundary platforms (`edge`, `azure`, `doubao`, `minimax`, `cosyvoice`)

---

### Doubao TTS: API Error Codes

**Symptoms**: `Doubao API error code=XXXX`

**Common codes**:

- `code != 3000`: Non-success response. Check VOLCENGINE_APPID and VOLCENGINE_ACCESS_TOKEN.
- HTTP 401/403: Invalid or expired access token. Regenerate at [Volcengine Console](https://console.volcengine.com/speech/service/8).
- Timeout: Increase via `VOLCENGINE_TIMEOUT_SEC` env var (default: 60s).
