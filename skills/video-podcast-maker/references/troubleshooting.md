# Video Podcast Maker — Troubleshooting & Reference

> **When to load:** Load this file when encountering errors, when the user asks about preferences, or when the user asks about BGM options.

## Contents

- [Discovery (when you're not sure which script to run)](#discovery-when-youre-not-sure-which-script-to-run) — `cli.py` entry point + envelope error codes
- [Troubleshooting](#troubleshooting) — TTS, FFmpeg, Remotion, encoding, audio-sync fixes
- [Background Music Options](#background-music-options)
- [Preference Commands](#preference-commands)
- [Preference Learning](#preference-learning)
- [Design Learning Troubleshooting](#design-learning-troubleshooting)

## Discovery (when you're not sure which script to run)

The suite is reachable through one hierarchical entry point at `scripts/cli.py`:

```bash
python3 scripts/cli.py --help                       # 9 resources
python3 scripts/cli.py <resource> --help            # actions for one resource
python3 scripts/cli.py <resource> <action> --help   # full args (forwards to underlying script)
python3 scripts/cli.py schema                       # JSON list of all 15 methods
python3 scripts/cli.py schema <method>              # typed parameter schema for one method
```

When a script fails with a structured envelope (most do — see `--format json`), the `code` field tells an agent how to recover: `input_not_found`, `input_invalid`, `auth_missing_env`, `tool_missing`, `validation_failed`, `confirmation_required`, `ffmpeg_failed`, `backend_failed`, `internal_error`. Direct invocations (`python3 scripts/<name>.py ...`) still work — the dispatcher is additive.

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
|--------|-----|---------|
| Pixabay Music | https://pixabay.com/music/ | Free, no attribution |
| Free Music Archive | https://freemusicarchive.org/ | CC licenses |
| Incompetech | https://incompetech.com/ | CC BY (attribution) |
| Uppbeat | https://uppbeat.io/ | Free tier available |
| Chosic | https://www.chosic.com/free-music/all/ | Various CC |

### BGM Selection Guide

| Video Type | Recommended Mood | Volume |
|------------|-----------------|--------|
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
|-----------|--------|
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

> **Planned feature (not yet implemented).** The schema supports `learning_history` records, but automatic detection of preference changes during Studio sessions is not yet coded. Currently, preferences are set manually via the commands above.

Planned capabilities:
- Detect repeated style modifications during Studio preview
- Ask user whether to promote changes to global defaults
- Track learning history in `user_prefs.json`

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

**Explanation**: The phoneme dictionary is passed to ttsCN, which applies it only on platforms with a pronunciation-override mechanism: `azure` (SSML `<phoneme>`) and `minimax` (pinyin annotations). All other platforms consume plain text and ignore the file.

**Workaround**: If pronunciation accuracy is critical, use `TTS_BACKEND=azure` or `TTS_BACKEND=minimax`.

---

### Word-Boundary Precision by Platform

- **Native per-word timings**: only platforms with boundary events (`edge`, `azure`, `doubao`, `minimax`, `cosyvoice` — ttsCN ≥1.5.0 for doubao/minimax, ≥1.6.0 for cosyvoice) — ttsCN returns them and the bridge shifts offsets per chunk
- **All other platforms**: subtitle timing is estimated by distributing each measured chunk duration across its characters (chunks are capped at 400 chars to bound the error)
- **Workaround**: If subtitle precision is critical, use one of the native-boundary platforms (`edge`, `azure`, `doubao`, `minimax`, `cosyvoice`)

---

### Doubao TTS: API Error Codes

**Symptoms**: `Doubao API error code=XXXX`

**Common codes**:
- `code != 3000`: Non-success response. Check VOLCENGINE_APPID and VOLCENGINE_ACCESS_TOKEN.
- HTTP 401/403: Invalid or expired access token. Regenerate at [Volcengine Console](https://console.volcengine.com/speech/service/8).
- Timeout: Increase via `VOLCENGINE_TIMEOUT_SEC` env var (default: 60s).
