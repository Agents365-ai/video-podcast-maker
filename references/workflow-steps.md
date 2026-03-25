# Video Podcast Maker — Workflow Steps Reference

> **When to load:** Claude loads this file during workflow execution for detailed step instructions.

---

## Startup: Load User Preferences

**Claude behavior:** Auto-execute before Step 1, no user interaction needed.

1. Check if `user_prefs.json` exists in `${CLAUDE_SKILL_DIR}`
2. If not, copy from `${CLAUDE_SKILL_DIR}/user_prefs.template.json`
3. Read preferences and apply in subsequent steps

```bash
SKILL_DIR="${CLAUDE_SKILL_DIR}"
PREFS_FILE="$SKILL_DIR/user_prefs.json"
TEMPLATE_FILE="$SKILL_DIR/user_prefs.template.json"

if [ ! -f "$PREFS_FILE" ]; then
  cp "$TEMPLATE_FILE" "$PREFS_FILE"
  echo "✓ Created default preferences"
fi
```

4. At Step 1 start, inform user of active preferences (if customized):

```
"Based on your preferences:
 - Theme: [theme]
 - Scale: [scalePreference]x
 - Speech rate: [tts.rate]

Say 'show preferences' to see details."
```

---

## Step 1: Define Topic Direction

**Auto mode:** Infer all decisions from the user's topic description. Use sensible defaults (audience: general, style: educational intro, tone: professional-casual, duration: medium 3-7min). Save directly to `videos/{name}/topic_definition.md`.

**Interactive mode:** Confirm each item (use `brainstorming` skill if available, otherwise ask directly):
1. **Target audience**: developers / general / students / professionals
2. **Video style**: educational intro / deep analysis / news brief / hands-on tutorial
3. **Content scope**: background / technical principles / usage / comparison
4. **Tone**: serious / casual / fast-paced
5. **Duration**: short (1-3min) / medium (3-7min) / long (7-15min)

Save to `videos/{name}/topic_definition.md`

---

## Step 2: Research Topic

Use WebSearch and WebFetch. Save to `videos/{name}/topic_research.md`.

---

## Step 3: Design Video Sections

Design 5-7 sections:
- Hero/Intro (15-25s)
- Core concepts (30-45s each)
- Demo/Examples (30-60s)
- Comparison/Analysis (30-45s)
- Summary (20-30s)

### Content Density Selection

Assign each section a density tier:

| Tier | Items | Best For |
|------|-------|----------|
| **Impact** | 1 | Hook, hero, CTA, brand moment — largest text |
| **Standard** | 2-3 | Features, comparison, demo |
| **Compact** | 4-6 | Feature grid, ecosystem |
| **Dense** | 6+ | Data tables, detailed comparisons — smallest text |

### Topic Type Detection

Auto-detect category from keywords and merge matching `topic_patterns`:

| Keywords | Category | Applied Preferences |
|----------|----------|-------------------|
| AI, coding, software, hardware, tech | tech | topic_patterns.tech |
| investment, stocks, crypto, finance | finance | topic_patterns.finance |
| tutorial, learning, guide | education | topic_patterns.education |
| food, travel, lifestyle, vlog | lifestyle | topic_patterns.lifestyle |
| news, trending, breaking | news | topic_patterns.news |

### Title Position

**Auto mode:** Use `top-center` (default).
**Interactive mode:** Ask user: top-center (recommended) / top-left / full-center.

**Rule:** Keep title position consistent within a single video.

---

## Step 4: Write Narration Script

**Preference application:** Adjust script style from `user_prefs.content`:
- `tone: professional` → formal language
- `tone: casual` → conversational, interjections ok
- `verbosity: concise` → 50-80 chars per paragraph
- `verbosity: detailed` → 100-150 chars per paragraph

Create `videos/{name}/podcast.txt` with section markers:

```text
[SECTION:hero]
大家好，欢迎来到本期视频。今天我们聊一个...

[SECTION:features]
它有以下功能...

[SECTION:demo]
让我演示一下...

[SECTION:summary]
总结一下，xxx是目前最xxx的xxx。

[SECTION:references]
本期视频参考了官方文档和技术博客。

[SECTION:outro]
感谢观看！点赞投币收藏，关注我，下期再见！
```

**Numbers MUST use Chinese pronunciation** for correct TTS:

| Type | Wrong | Correct |
|------|-------|---------|
| Integer | 29, 3999 | 二十九，三千九百九十九 |
| Decimal | 1.2, 3.5 | 一点二，三点五 |
| Percentage | 15%, -10% | 百分之十五，负百分之十 |
| Date | 2025-01-15 | 二零二五年一月十五日 |
| Large number | 6144 | 六千一百四十四 |
| English units | 128GB | 一百二十八G |

**Section notes**:
- **summary**: Pure content summary, no interaction prompts
- **references** (optional): One sentence about sources
- **outro**: Thanks + triple-click CTA
- Empty `[SECTION:xxx]` = silent section

### Duration Estimation (Dry Run)

After writing `podcast.txt`, automatically run:

```bash
python3 ${CLAUDE_SKILL_DIR}/generate_tts.py --input videos/{name}/podcast.txt --output-dir videos/{name} --dry-run
```

Report estimated duration. If >12min or <3min, suggest adjustments.

---

## Step 5: Collect Media Assets

**Auto mode:** Skip media collection (text-only animated sections). Proceed to Step 6.
**Interactive mode:** Ask per-section media source (skip / local file / screenshot / web search / AI generated).

If user mentioned AI images, screenshots, or specific assets in initial request, collect those regardless of mode.

Save assets to `public/media/{video-name}/`, generate `media_manifest.json`.

**Available sources:**
- **Unsplash** / **Pexels** / **Pixabay** — free images
- **unDraw** — open-source SVG illustrations
- **Simple Icons** — brand SVG icons
- **Playwright** — web screenshots
- **imagen skill** — AI-generated images

---

## Step 6: Generate Publish Info (Part 1)

Based on `podcast.txt`, generate `publish_info.md`:
- Title (number + topic + hook)
- Tags (10, including product names / domain terms / trending tags)
- Description (100-200 chars)

---

## Step 7: Generate Video Thumbnail

**Auto mode:** Generate Remotion thumbnails (16:9 + 4:3).
**Interactive mode:** Ask user: Remotion-generated / AI (imagen skill) / both.

**MUST generate both aspect ratios**: 16:9 (playback page) and 4:3 (feed/activity), both required. 9:16 only when generating vertical video.

```bash
npx remotion still src/remotion/index.ts Thumbnail16x9 videos/{name}/thumbnail_remotion_16x9.png
npx remotion still src/remotion/index.ts Thumbnail4x3 videos/{name}/thumbnail_remotion_4x3.png
# Optional: vertical thumbnail (only if rendering vertical video)
npx remotion still src/remotion/index.ts Thumbnail9x16 videos/{name}/thumbnail_remotion_9x16.png
```

---

## Step 8: Generate TTS Audio

**Preference application:** Read backend/rate/voice from `user_prefs.tts`.

```bash
# Primary command (backend from user_prefs or env)
python3 ${CLAUDE_SKILL_DIR}/generate_tts.py --input videos/{name}/podcast.txt --output-dir videos/{name}

# Resume from breakpoint
python3 ${CLAUDE_SKILL_DIR}/generate_tts.py --input videos/{name}/podcast.txt --output-dir videos/{name} --resume

# Dry run (estimate duration)
python3 ${CLAUDE_SKILL_DIR}/generate_tts.py --input videos/{name}/podcast.txt --output-dir videos/{name} --dry-run
```

Backend selection via env: `TTS_BACKEND=azure|cosyvoice|edge`, rate via `TTS_RATE="+5%"`.

### Phoneme Correction (SSML)

Three tiers (highest to lowest priority):

**1. Inline annotation** (highest) — in podcast.txt:
```text
每个执行器[zhí xíng qì]都有自己的上下文窗口
```

**2. Project dictionary** — in `videos/{name}/phonemes.json`:
```json
{ "执行器": "zhí xíng qì", "重做": "chóng zuò" }
```

**3. Built-in dictionary** — common polyphones (auto-applied)

**Outputs**: `podcast_audio.wav`, `podcast_audio.srt`, `timing.json`

**timing.json `label` field**: Each section gets a human-readable label from the first line of content (before first punctuation, max 10 chars). Example: `[SECTION:hero]` with "大家好，欢迎来到本期视频" → `label: "大家好"`. Silent sections use section name as label.

---

## Step 9: Create Remotion Composition + Studio Preview

**Claude MUST read `references/design-guide.md` before this step.**

**Preference application:** From `user_prefs.visual` override `defaultVideoProps`:
- `typography.*` × `scalePreference` → apply font scaling
- `theme: dark` → swap backgroundColor/textColor
- `primaryColor`, `accentColor` → direct override

Copy files to public/:
```bash
cp videos/{name}/podcast_audio.wav videos/{name}/timing.json public/
```

### Standard Video Template

Use `${CLAUDE_SKILL_DIR}/templates/Video.tsx` as starting point.

**Shared infrastructure** — copy only if not already present:
```bash
[ ! -f src/remotion/Root.tsx ] && cp ${CLAUDE_SKILL_DIR}/templates/Root.tsx src/remotion/
[ ! -d src/remotion/components ] && cp -r ${CLAUDE_SKILL_DIR}/templates/components src/remotion/components
```

**Per-video composition** — NEVER overwrite `Video.tsx`. Create a unique file:
```bash
cp ${CLAUDE_SKILL_DIR}/templates/Video.tsx src/remotion/{PascalCaseName}Video.tsx
```

Register in `Root.tsx`. Each video gets its own composition file.

**Naming convention:**
| Video name | Composition file | Composition ID |
|------------|-----------------|----------------|
| `ai-agents` | `AiAgentsVideo.tsx` | `AiAgents` |
| `reference-manager` | `ReferenceManagerVideo.tsx` | `ReferenceManager` |

Components are modular:
```tsx
import { ComparisonCard, CodeBlock, FeatureGrid, MediaSection } from "./components";
```

### Component Selection Guide

Choose components based on section content type:

| Content Type | Recommended Component | Draw-On Effect |
|---|---|---|
| Process / pipeline steps | `FlowChart` | SVG arrow connectors draw progressively |
| History / milestones | `Timeline` | SVG nodes + connectors animate in sequence |
| Architecture / system diagram | `DiagramReveal` | Nodes + edges draw on with curve/elbow/straight |
| Comparison / vs | `ComparisonCard` | Entrance animation |
| Data / metrics | `DataBar`, `StatCounter`, `MetricsRow` | Bar fill + counter animations |
| Code / terminal | `CodeBlock` | Entrance animation |
| Key quote | `QuoteBlock` | Entrance animation |
| Feature list / grid | `FeatureGrid`, `IconCard` | Staggered entrance |
| Images / screenshots | `MediaSection`, `MediaGrid` | Entrance animation |
| After Effects animation | `LottieAnimation` | Frame-accurate Lottie playback |

**Audio visualization** — add `AudioWaveform` as a persistent overlay in the video:
```tsx
// Inside Video component, after Scale4K but before Audio elements:
<AudioWaveform props={props} position="bottom" mode="bars" barCount={32} height={40} opacity={0.25} />
```
Three modes: `"bars"` (spectrum), `"wave"` (filled area), `"dots"` (pulsing circles).

**Diagram architecture** — use `DiagramReveal` for system/architecture diagrams:
```tsx
<DiagramReveal
  props={props}
  nodes={[
    { id: "a", label: "Input", x: 100, y: 80 },
    { id: "b", label: "Process", x: 400, y: 80 },
    { id: "c", label: "Output", x: 700, y: 80 },
  ]}
  edges={[
    { from: "a", to: "b", style: "curve" },
    { from: "b", to: "c", style: "curve" },
  ]}
  width={900} height={200}
/>
```

**Lottie animations** — place JSON files in `public/animations/`:
```tsx
<LottieAnimation src="animations/brain.json" width={200} height={200} loop />
```

### Section Transitions

Template uses `@remotion/transitions` `TransitionSeries`.

| Property | Default | Description |
|----------|---------|-------------|
| `transitionType` | `fade` | fade / slide / wipe / none |
| `transitionDuration` | `15` (0.5s) | Frames |

Install dependencies:
```bash
npm install @remotion/transitions @remotion/paths @remotion/shapes @remotion/media-utils @remotion/lottie lottie-web
```

### Key Architecture

| Point | Description |
|-------|-------------|
| **ChapterProgressBar** | Must be **outside** `scale(2)` container |
| **Chapter width** | Use `flex: ch.duration_frames` for proportional width |
| **Progress indicator** | White progress bar within current chapter |
| **4K scaling** | Content area uses `scale(2)` from 1920×1080 to 3840×2160 |

### Triple-Click Outro

**Auto mode:** Use pre-made MP4 animation (white for light, black for dark theme).
**Interactive mode:** Ask: pre-made MP4 (recommended) / Remotion code-generated.

```bash
cp ${CLAUDE_SKILL_DIR}/assets/bilibili-triple-white.mp4 public/media/{video-name}/
```

```tsx
import { OffthreadVideo, staticFile } from "remotion";
<OffthreadVideo src={staticFile("media/{video-name}/bilibili-triple-white.mp4")} />
```

### Preview & Quality Gate

**Auto mode:** Skip Studio. Proceed to Step 10 for preview render (720p), Claude self-validates.

**Interactive mode:** Launch Studio:
```bash
npx remotion studio src/remotion/index.ts
```

1. Launch `remotion studio` (real-time preview, hot reload)
2. Ask user: "Preview OK? Describe changes if needed"
   - **Satisfied** → Step 10
   - **Changes needed** → apply, Studio hot reloads, repeat
3. Pronunciation fixes require re-running TTS (Step 8).

---

### Visual QA (Automated, part of Step 9)

**Claude behavior:** Auto-run after composition is created, before Step 10. No user prompt needed.

### Render Section Stills

Read `timing.json`, render still at each section's midpoint:

```bash
# midpoint_frame = start_frame + (duration_frames / 2)
npx remotion still src/remotion/index.ts CompositionId videos/{name}/qa_{section_name}.png --frame {midpoint_frame}
```

### Visual Inspection

Claude reads each still image (multimodal) and checks:

| Check | What to Look For | Severity |
|-------|-----------------|----------|
| **Blank frame** | All-white or all-black | FAIL |
| **Text size** | Too small at 1080p | FAIL |
| **Space utilization** | Content <50% of screen | WARN |
| **Text overflow** | Clipped at edges | FAIL |
| **Color contrast** | Text unreadable | FAIL |
| **Layout alignment** | Misaligned/overlapping | WARN |
| **Visual variety** | Consecutive sections identical | WARN |

### QA Report

```
=== Visual QA ===
✓ hero: Large title centered, good contrast
✓ features: 3 cards with distinct colors
⚠ demo: Content ~60% width — consider wider layout
✓ summary: Clean layout, readable
✓ outro: Triple-click animation visible

Result: 4/5 PASS, 1 WARNING
```

**On FAIL:** Auto-fix, re-render still, re-check.
**On WARN:** Note in report, proceed.
**All PASS:** Proceed to Step 10 silently.

### Cleanup

```bash
rm -f videos/{name}/qa_*.png
```

---

## Step 10: Render Video

### Preview Render — The Only Mandatory Stop (Auto mode)

```bash
npx remotion render src/remotion/index.ts CompositionId videos/{name}/preview.mp4 --scale 0.33 --crf 28
```

```bash
DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 videos/{name}/preview.mp4 | cut -d. -f1)
SIZE=$(ls -lh videos/{name}/preview.mp4 | awk '{print $5}')
echo "Preview: ${DUR}s, ${SIZE}"
```

**Ask user:** "720p preview ready: `videos/{name}/preview.mp4` (duration Xs). Please review:"
- **Confirm, render 4K** → proceed
- **Changes needed** → apply, re-render preview, repeat

This is the **only stop** in auto mode.

**Interactive mode:** Studio preview already done in Step 9. Skip preview render, go directly to 4K.

### 4K Render

```bash
npx remotion render src/remotion/index.ts CompositionId videos/{name}/output.mp4 --video-bitrate 16M
```

**Verify 4K:**
```bash
ffprobe -v quiet -show_entries stream=width,height -of csv=p=0 videos/{name}/output.mp4
# Expected: 3840,2160
```

### Optional: Vertical Highlight Clip (9:16)

```bash
npx remotion render src/remotion/index.ts MyVideoVertical videos/{name}/output_vertical.mp4 --video-bitrate 16M
npx remotion still src/remotion/index.ts Thumbnail9x16 videos/{name}/thumbnail_remotion_9x16.png
```

The vertical composition reuses Video.tsx with `orientation: "vertical"`. All components auto-adapt.

---

## Step 11: Mix with Background Music

### BGM Selection

**Auto mode:** Select BGM based on topic type:
- Tech/coding/tutorial → `snow-stevekaldes-piano-397491.mp3` (calm)
- Product review/news/upbeat → `perfect-beauty-191271.mp3` (positive)
- User provided custom BGM → use their file

**Interactive mode:** Ask user to choose or provide their own.

```bash
# Default: auto-selected track
cp ${CLAUDE_SKILL_DIR}/assets/{selected-track}.mp3 videos/{name}/bgm.mp3

# Or user's custom BGM
cp /path/to/user-bgm.mp3 videos/{name}/bgm.mp3
```

### Mix

BGM volume priority: `user_prefs.tts.bgmVolume` > topic-pattern default > `0.05` fallback.

```bash
# BGM_VOL from user_prefs.tts.bgmVolume (default 0.05)
ffmpeg -y \
  -i videos/{name}/output.mp4 \
  -stream_loop -1 -i videos/{name}/bgm.mp3 \
  -filter_complex "[0:a]volume=1.0[a1];[1:a]volume=${BGM_VOL:-0.05}[a2];[a1][a2]amix=inputs=2:duration=first[aout]" \
  -map 0:v -map "[aout]" \
  -c:v copy -c:a aac -b:a 192k \
  videos/{name}/video_with_bgm.mp4
```

> **More BGM options and volume tuning:** See `references/troubleshooting.md`.

---

## Step 12: Add Subtitles

**Auto mode:** Skip subtitles — copy `video_with_bgm.mp4` as `final_video.mp4`.
**Interactive mode:** Ask user: "Add burned-in subtitles?"

If subtitles requested:
```bash
# 1) Prefer system fonts first
ffmpeg -y -i videos/{name}/video_with_bgm.mp4 \
  -vf "subtitles=videos/{name}/podcast_audio.srt:force_style='FontName=PingFang SC,FontSize=20,PrimaryColour=&H00333333,OutlineColour=&H00FFFFFF,Bold=0,Outline=2,Shadow=0,MarginV=20'" \
  -c:v libx264 -crf 18 -preset slow -s 3840x2160 -c:a copy videos/{name}/final_video.mp4 \
|| \
# 2) Fallback to bundled external fonts
ffmpeg -y -i videos/{name}/video_with_bgm.mp4 \
  -vf "subtitles=videos/{name}/podcast_audio.srt:fontsdir=skills/video-podcast-maker/assets/fonts:force_style='FontName=Source Han Sans SC,FontSize=20,PrimaryColour=&H00333333,OutlineColour=&H00FFFFFF,Bold=0,Outline=2,Shadow=0,MarginV=20'" \
  -c:v libx264 -crf 18 -preset slow -s 3840x2160 -c:a copy videos/{name}/final_video.mp4
```

If skipping:
```bash
cp videos/{name}/video_with_bgm.mp4 videos/{name}/final_video.mp4
```

---

## Step 13: Complete Publish Info (Part 2)

Generate Bilibili chapters from `timing.json`:

```
00:00 Opening
00:23 Features
00:55 Demo
01:20 Summary
```

Format: `MM:SS Chapter Title`, each gap ≥5s.

---

## Step 14: Verify Output & Cleanup

### 14.1 Verification

```bash
VIDEO_DIR="videos/{name}"
echo "=== File Check ==="
for f in podcast.txt podcast_audio.wav podcast_audio.srt timing.json output.mp4 final_video.mp4; do
  [ -f "$VIDEO_DIR/$f" ] && echo "✓ $f" || echo "✗ $f missing"
done

echo "=== Technical Specs ==="
RES=$(ffprobe -v quiet -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "$VIDEO_DIR/final_video.mp4")
[ "$RES" = "3840,2160" ] && echo "✓ Resolution: 3840x2160 (4K)" || echo "✗ Resolution: $RES (not 4K)"
DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$VIDEO_DIR/final_video.mp4" | cut -d. -f1)
echo "✓ Duration: ${DUR}s"
SIZE=$(ls -lh "$VIDEO_DIR/final_video.mp4" | awk '{print $5}')
echo "✓ File size: $SIZE"
```

### 14.2 Cleanup

**Auto mode:** Auto-clean temp files, report what was removed.
**Interactive mode:** List files and ask for confirmation.

```bash
VIDEO_DIR="videos/{name}"
rm -f "$VIDEO_DIR"/part_*.wav "$VIDEO_DIR"/concat_list.txt
rm -f "$VIDEO_DIR"/output.mp4 "$VIDEO_DIR"/video_with_bgm.mp4
rm -f public/podcast_audio.wav public/timing.json public/media_manifest.json
rm -rf public/media/{name}
echo "✓ Temp files cleaned"
```

### 14.3 Final Report

```
=== Video Complete ===
✓ File: final_video.mp4
✓ Resolution: 3840x2160 (4K)
✓ Duration: XXs
✓ Size: XXX MB
✓ Thumbnails: thumbnail_remotion_16x9.png, thumbnail_remotion_4x3.png
✓ Publish info: publish_info.md
✓ Temp files cleaned
```

---

## Step 15: Generate Vertical Shorts (Optional)

**When:** After long-form video is complete (Step 14). Optional step.

**Claude behavior:** Offer to generate vertical shorts. If user agrees, run automatically.

### Generate shorts from sections

```bash
python3 generate_shorts.py --input-dir videos/{name}/ --title "视频标题"
```

This produces `videos/{name}/shorts/{section_name}/` for each qualifying section (>20s, not hero/outro) with:
- `short_audio.wav` — extracted audio slice
- `short_timing.json` — timing for intro (3s) + content + CTA (3s)
- `short_info.json` — composition metadata
- `register_snippet.tsx` — Root.tsx registration code

### Create short compositions

For each generated short:
1. Copy `templates/ShortVideo.tsx` as `src/remotion/{SectionName}ShortVideo.tsx`
2. Replace `SectionContent` placeholder with the actual section component from the long-form video
3. Update `SHORT_CONFIG` with values from `short_info.json`
4. Register composition in `Root.tsx` using `register_snippet.tsx`
5. Copy `short_audio.wav` to `public/`

### Render shorts

```bash
npx remotion render src/remotion/index.ts {CompId} videos/{name}/shorts/{section}/short.mp4 --video-bitrate 16M
```

Each short is a standalone 9:16 4K video (2160×3840) with:
- 3-second intro title card
- Section content (vertical layout, all components auto-adapt)
- 3-second CTA card ("关注看完整版")
