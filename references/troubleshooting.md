# Video Podcast Maker — Troubleshooting & Reference

> **When to load:** Claude loads this file when encountering errors, when user asks about preferences, or when user asks about BGM options.

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
1. Verify `timing.json` exists in `public/` and has correct `start_frame`/`duration_frames`
2. Check composition ID matches: `npx remotion render ... CompositionId` must match Root.tsx registration
3. Ensure `podcast_audio.wav` is copied to `public/`
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
# Recommended: put fonts in skills assets directory for deterministic rendering
mkdir -p skills/video-podcast-maker/assets/fonts
# Add:
#   skills/video-podcast-maker/assets/fonts/SourceHanSansSC-Regular.otf
#   skills/video-podcast-maker/assets/fonts/SourceHanSansSC-Medium.otf
#   skills/video-podcast-maker/assets/fonts/SourceHanSansSC-Bold.otf
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

Available at `${CLAUDE_SKILL_DIR}/assets/`:

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

**Claude behavior:** In auto mode, select most appropriate included track by topic type. In interactive mode, ask user.

---

## Preference Commands

Users can manage preferences in conversation:

### View Preferences

User says: "show preferences" / "显示偏好设置"

Claude outputs current settings summary (visual, TTS, content, topic patterns, learning history count).

### Reset Preferences

User says: "reset preferences" / "重置偏好"

```bash
cp ${CLAUDE_SKILL_DIR}/user_prefs.template.json ${CLAUDE_SKILL_DIR}/user_prefs.json
echo "✓ Preferences reset to defaults"
```

### Save Current Settings

User says: "save this as tech default" / "把这个设置保存为科技类默认"

Claude extracts current visual/tts/content settings, updates `topic_patterns.tech`.

### Manual Preference Setting

User says: "set speech rate to +10%" / "dark theme as default" / "title always 100px"

Claude directly updates the corresponding field in `user_prefs.json`.

---

## Preference Learning

**Claude behavior:** Execute after Studio preview iteration completes.

### Detect Modifications

Compare values at start vs end of Studio preview session:

| Category | Detection |
|----------|-----------|
| Typography | titleSize, subtitleSize, bodySize changes |
| Color | primaryColor, backgroundColor changes |
| Layout | progress bar toggle, transition effect changes |

### Progressive Learning

- **First modification**: Current video only, don't update global preferences
- **Repeated modification** (≥2 same direction): Ask user if it should become default

```
"Detected [N] consecutive increases to title size (80 → 96). Set 96px as default?"
- Yes (recommended) → update user_prefs.json
- No → current video only
```

### Explicit Preference Capture

Detect expressions and learn:

| User Expression Pattern | Learning Action |
|------------------------|----------------|
| "always use this color" | Save primaryColor to global |
| "use this style for tech videos" | Save to topic_patterns.tech |
| "remember these settings" | Save all current modifications to global |

### Update Preference File

After learning, update `user_prefs.json` and add `learning_history` record:

```json
{
  "date": "2026-03-15",
  "source": "implicit",
  "change": { "path": "global.visual.typography.heroTitle", "from": 80, "to": 96 },
  "context": "User adjusted title size 3 times in Studio"
}
```
