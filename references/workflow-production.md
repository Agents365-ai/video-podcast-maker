# Video Podcast Maker — Workflow Phase 2: Production

> **When to load:** Load after the narration script exists, or when the user asks about media, TTS, Remotion composition, 4K render, or BGM mixing.
>
> **Covers:** Steps 5-11 (media collection → publish info draft → thumbnail → TTS → Remotion composition + Studio preview → 4K render → BGM mix).
>
> **Previous phase:** See `workflow-script.md` for Pre-workflow + Startup + Steps 1-4.
> **Next phase:** See `workflow-publish.md` for Steps 12-15 (subtitles, publish info, cleanup, shorts).

## Contents

- [Step 5: Collect Media Assets](#step-5-collect-media-assets)
- [Step 6: Generate Publish Info (Part 1)](#step-6-generate-publish-info-part-1)
- [Step 7: Generate Video Thumbnail](#step-7-generate-video-thumbnail)
- [Step 8: Generate TTS Audio](#step-8-generate-tts-audio) — voice selection, SSML, chunk seams
- [Step 9: Create Remotion Composition + Studio Preview](#step-9-create-remotion-composition--studio-preview)
- [Step 10: Render 4K Video](#step-10-render-4k-video)
- [Step 11: Mix with Background Music](#step-11-mix-with-background-music)

---

## Step 5: Collect Media Assets

**Auto mode:** Skip media collection (text-only animated sections). Proceed to Step 6.
**Interactive mode:** Ask per-section media source (skip / local file / screenshot / web search / AI generated).

If user mentioned AI images, screenshots, or specific assets in initial request, collect those regardless of mode.

Save assets to `videos/{name}/media/`, generate `media_manifest.json`.

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

**MUST generate both aspect ratios**: 16:9 (playback page) and 4:3 (feed/activity), both required for horizontal video. (9:16 thumbnail is generated alongside the vertical render in Step 10/15 — not here.)

**Thumbnail design rules** (see `references/design-guide.md` for full spec):
- Centered layout, title ≥120px bold, icons ≥120px — as large as text length allows
- Text + icons should fill most of the canvas, minimize empty space
- Must be legible at 300px feed size — use text-stroke or contrast overlay

```bash
npx remotion still src/remotion/index.ts Thumbnail16x9 videos/{name}/thumbnail_remotion_16x9.png --public-dir videos/{name}/
npx remotion still src/remotion/index.ts Thumbnail4x3 videos/{name}/thumbnail_remotion_4x3.png --public-dir videos/{name}/
```

**xiaohongshu:** Generate 3:4 thumbnail (replaces 4:3):
```bash
npx remotion still src/remotion/index.ts Thumbnail3x4 videos/{name}/thumbnail_remotion_3x4.png --public-dir videos/{name}/
```

---

## Step 8: Generate TTS Audio

> **Azure-specific gotchas:** if you're using `TTS_BACKEND=azure`, load **[azure-tts-pitfalls.md](azure-tts-pitfalls.md)** before picking a voice or style — covers Multilingual-variant phoneme behavior, SSML pitfalls, the style support matrix, and a triage checklist for hoarse/missing/glitchy audio. Worth ~30 seconds of reading time and saves a re-render.

**Preference application:** `generate_tts.py` reads `user_prefs.tts.{backend, rate, voices.<backend>}` automatically. No manual env extraction needed. Precedence for each setting: env var > `user_prefs.json` > hardcoded default. The script logs which source it picked at startup.

```bash
# Primary command — backend, rate, and voice all auto-resolved from user_prefs
python3 ${SKILL_DIR}/scripts/generate_tts.py --input videos/{name}/podcast.txt --output-dir videos/{name}

# Resume from breakpoint
python3 ${SKILL_DIR}/scripts/generate_tts.py --input videos/{name}/podcast.txt --output-dir videos/{name} --resume

# Dry run (estimate duration)
python3 ${SKILL_DIR}/scripts/generate_tts.py --input videos/{name}/podcast.txt --output-dir videos/{name} --dry-run
```

Override per-run (without editing user_prefs): `TTS_BACKEND=edge TTS_RATE="+10%" python3 ...`. CLI `--backend <name>` also works and takes top priority.

### Voice Selection by Language

The default path: edit `user_prefs.json` → `global.tts.voices.<backend>` once for the user's preferred language, then `generate_tts.py` picks it up automatically. Reference defaults if the user has not customized `tts.voices`:

| Language | Azure | Edge | Doubao | CosyVoice |
|----------|-------|------|--------|-----------|
| zh-CN | zh-CN-XiaoxiaoNeural | zh-CN-XiaoxiaoNeural | BV001_streaming | longxiaochun |
| en-US | en-US-JennyNeural | en-US-JennyNeural | BV700_streaming | longlaoshu_v2 |

**Manual override (one-off run, no prefs change)** — set the per-backend env var:

```bash
# Per-backend env vars: AZURE_TTS_VOICE / EDGE_TTS_VOICE / VOLCENGINE_VOICE_TYPE / etc.
EDGE_TTS_VOICE="en-US-JennyNeural" python3 ${SKILL_DIR}/scripts/generate_tts.py --input videos/{name}/podcast.txt --output-dir videos/{name}
```

Precedence: env var > `user_prefs.json` > hardcoded default. The script logs which source it picked at startup.

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

**3. Global dictionary** — `phonemes.json` in skill root (shared across all projects)

**Outputs**: `podcast_audio.wav`, `podcast_audio.srt`, `timing.json`

**timing.json `label` field**: Each section gets a human-readable label from the first line of content (before first punctuation, max 10 chars). Example: `[SECTION:hero]` with "大家好，欢迎来到本期视频" → `label: "大家好"`. Silent sections use section name as label.

---

## Step 9: Create Remotion Composition + Studio Preview

**The agent MUST read `references/design-guide.md` before this step.**

**Preference application:** From `user_prefs.visual` override `defaultVideoProps`:
- `typography.*` × `scalePreference` → apply font scaling
- `theme: dark` → swap backgroundColor/textColor
- `primaryColor`, `accentColor` → direct override

All Remotion commands use `--public-dir videos/{name}/` so assets are read directly from the video directory (no copying needed).

### Style Profile Integration

Before choosing visual design, check in order:
1. Session-specified style profile? → Load `user_prefs.json` style_profiles[name], apply props_override
2. No profile? → Check design_references index for tag matches against detected topic
3. Found matches? → Suggest: "Your reference library has N references matching '{topic}'. Apply style '{profile_name}'?"
4. Nothing matches? → Fall back to global + topic_patterns (existing behavior)

Priority chain: Root.tsx defaults < global < topic_patterns[type] < style_profiles[name] < current instructions

### Standard Video Template

Use `${SKILL_DIR}/templates/Video.tsx` as starting point.

**Shared infrastructure** — copy only if not already present:
```bash
[ ! -f src/remotion/Root.tsx ] && cp ${SKILL_DIR}/templates/Root.tsx src/remotion/
[ ! -d src/remotion/components ] && cp -r ${SKILL_DIR}/templates/components src/remotion/components
```

**Per-video composition** — NEVER overwrite `Video.tsx`. Create a unique file:
```bash
cp ${SKILL_DIR}/templates/Video.tsx src/remotion/{PascalCaseName}Video.tsx
```

Register in `Root.tsx`. Each video gets its own composition file.

> **Localization required.** `templates/Video.tsx` is a zh-CN starter — every visible literal (titles, subtitles, "总结", "感谢观看", outro CTA "点赞 / 收藏 / 关注 / 下期再见！", placeholder bullets) is Chinese. When `user_prefs.global.language != "zh-CN"`, replace every literal in the copied composition file with the target-language equivalent before the Studio preview. Use the platform/language outro table from `workflow-script.md` Step 4 for the CTA text.

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

**Lottie animations** — place JSON files in `videos/{name}/animations/`:
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

**Auto mode:** Use pre-made MP4 animation. Pick the asset by `user_prefs.visual.theme`: `light` → `bilibili-triple-white.mp4`, `dark` → `bilibili-triple-black.mp4`.
**Interactive mode:** Ask: pre-made MP4 (recommended) / Remotion code-generated.

```bash
# Light theme:
cp ${SKILL_DIR}/assets/bilibili-triple-white.mp4 videos/{name}/media/
# Dark theme:
cp ${SKILL_DIR}/assets/bilibili-triple-black.mp4 videos/{name}/media/
```

```tsx
import { OffthreadVideo, staticFile } from "remotion";
<OffthreadVideo src={staticFile("media/bilibili-triple-white.mp4")} />
```

**Xiaohongshu:** No pre-made animation — use text-based CTA. The outro section renders the CTA text ("点赞收藏加关注，评论区见！") as an animated text overlay, similar to YouTube's text CTA mode.

**Douyin:** Text-only CTA (no animation). Douyin content is vertical shorts only — the CTA text ("点赞关注，评论区见！") is rendered as simple end text, not animated.

**WeChat Channels:** Text-only CTA (no animation). WeChat Channels content is vertical shorts only — the CTA text ("点赞关注，转发给朋友！") is rendered as simple end text, not animated.

### Preview & Quality Gate (Mandatory Stop)

Remotion Studio is **always launched** — both auto and interactive modes. This is the primary review step.

**Free port 3000 first** so a stale Studio from a previous run doesn't serve the wrong `--public-dir`. Prefer the port-scoped approach below — a naive `pkill -f "remotion studio"` matches *any* Remotion Studio across the system, including unrelated projects the user may have open in another terminal:

```bash
# Find the PID holding TCP port 3000 (Remotion Studio's default), if any.
STUDIO_PID=$(lsof -nP -iTCP:3000 -sTCP:LISTEN -t 2>/dev/null | head -1)

if [ -n "$STUDIO_PID" ]; then
  # Confirm it's actually Remotion before killing — refuses to kill a
  # non-Remotion process that happens to bind 3000 (Next.js dev server, etc.)
  if ps -p "$STUDIO_PID" -o command= | grep -q "remotion"; then
    kill "$STUDIO_PID"
  else
    echo "Port 3000 is held by a non-Remotion process (PID $STUDIO_PID). Free it manually or run Studio on a different port." >&2
    exit 1
  fi
fi

npx remotion studio src/remotion/index.ts --public-dir videos/{name}/
```

If you intentionally run multiple Remotion projects in parallel, launch Studio on a non-default port (`npx remotion studio ... --port 3001`) and adjust the `lsof -iTCP:<port>` line above accordingly.

1. Launch `remotion studio` (real-time preview, hot reload)
2. Ask user: "Studio is running at http://localhost:3000. Please review the video preview."
3. **Review loop** — user reviews, requests changes, the agent applies them, Studio hot reloads:
   - Layout/animation tweaks → edit components, Studio auto-refreshes
   - Script/content changes → edit `podcast.txt`, may need re-TTS (Step 8)
   - Pronunciation fixes → re-run TTS (Step 8)
4. **Exit condition**: User explicitly says "render 4K" / "render final version" / "looks good, render" → proceed to Step 10
5. Do NOT proceed to Step 10 until the user confirms.

---

### Visual QA (Automated, part of Step 9)

> **Planned feature.** Automated still rendering and multimodal inspection is not yet implemented. Currently, visual quality is verified manually via Remotion Studio preview. The agent may offer to render section stills for manual inspection if requested.

---

## Step 10: Render 4K Video

> **Prerequisite:** User has reviewed in Remotion Studio (Step 9) and explicitly requested final render.

### 4K Render

```bash
npx remotion render src/remotion/index.ts CompositionId videos/{name}/output.mp4 --video-bitrate 16M --public-dir videos/{name}/
```

**Verify 4K:**
```bash
ffprobe -v quiet -show_entries stream=width,height -of csv=p=0 videos/{name}/output.mp4
# Expected: 3840,2160
```

### Optional: Vertical Highlight Clip (9:16)

```bash
npx remotion render src/remotion/index.ts MyVideoVertical videos/{name}/output_vertical.mp4 --video-bitrate 16M --public-dir videos/{name}/
npx remotion still src/remotion/index.ts Thumbnail9x16 videos/{name}/thumbnail_remotion_9x16.png --public-dir videos/{name}/
```

The vertical composition reuses Video.tsx with `orientation: "vertical"`. All components auto-adapt.

**Platform-specific video format notes:**
- **xiaohongshu**: Primarily short-form vertical content. Long-form horizontal video is optional.
- **douyin**: Vertical shorts only (9:16). No horizontal long-form video generated. Uses existing `scripts/generate_shorts.py` pipeline.
- **weixin-channels**: Vertical shorts only (9:16). No horizontal long-form video generated. Uses existing `scripts/generate_shorts.py` pipeline.

---

## Step 11: Mix with Background Music

> **BGM source single-write rule (READ THIS FIRST).** Two paths can layer BGM
> on the final video: the Remotion `<Audio src="bgm.mp3">` block inside
> `Video.tsx`, and the FFmpeg `amix` below. **Pick exactly one.** Default
> behavior is FFmpeg-only — `Root.tsx::defaultVideoProps.bgmVolume` is `0`,
> so the Remotion BGM block is disabled and `output.mp4` from Step 10
> contains *only* narration. Step 11 then layers BGM via FFmpeg.
>
> If you intend to bake BGM inside Remotion instead (e.g. for a beat-synced
> video where the BGM drives animation): set `bgmVolume > 0` in Studio,
> ensure `bgm.mp3` is present in `--public-dir`, and **skip Step 11**. Running
> both layers it twice.

### BGM Selection

**Default**: track is read from `user_prefs.bgm.track` (logical name) and resolved to a file via `user_prefs.bgm.tracks` (logical → filename map). Use the helper:

```bash
# Copy the configured BGM track to the per-video dir
cp "$(python3 ${SKILL_DIR}/scripts/resolve_bgm_path.py)" videos/{name}/bgm.mp3
```

**Override (custom BGM)**: skip the helper and copy any file:
```bash
cp /path/to/user-bgm.mp3 videos/{name}/bgm.mp3
```

**Override (different built-in track)**: edit `user_prefs.bgm.track` to one of the keys in `bgm.tracks` (e.g. `"calm-piano"`, `"perfect-beauty"`). Add new tracks by dropping the mp3 in `${SKILL_DIR}/assets/` and registering it in `bgm.tracks`.

### Mix

BGM volume comes from `user_prefs.bgm.volume` (fallback `0.10`), resolved by `scripts/get_pref.py`. The narration bus is boosted +3.5 dB (`volume=1.5`) to lift TTS output (~-26 dB mean) closer to broadcast loudness (~-22 dB mean) without clipping. `amix` uses `normalize=0` so the input-count division (default `/N`) doesn't halve the narration:

```bash
BGM_VOL=$(python3 ${SKILL_DIR}/scripts/get_pref.py global bgm volume --default 0.10)

ffmpeg -y \
  -i videos/{name}/output.mp4 \
  -stream_loop -1 -i videos/{name}/bgm.mp3 \
  -filter_complex "[0:a]volume=1.5[a1];[1:a]volume=${BGM_VOL}[a2];[a1][a2]amix=inputs=2:duration=first:normalize=0[aout]" \
  -map 0:v -map "[aout]" \
  -c:v copy -c:a aac -b:a 192k \
  videos/{name}/video_with_bgm.mp4
```

**Why these specific values:**
- `volume=1.5` (narration): Azure TTS WAV is typically -25 to -27 dB mean. ×1.5 lifts it to ~-22 dB while keeping ≥2 dB headroom (no clip on common Chinese phonemes).
- `volume=${BGM_VOL}` (BGM): default `0.10` = -20 dB. With narration at 1.5×, this gives ~18 dB BGM-vs-narration headroom — clearly audible but never competing. (Previously `0.05` was too quiet relative to the boosted narration.)
- `amix=...:normalize=0`: prevents amix from dividing each input by `inputs=2`. Without this, narration gets cut to 50% and the whole video sounds quiet.

**Verify loudness after mix:**
```bash
ffmpeg -i videos/{name}/video_with_bgm.mp4 -af volumedetect -f null - 2>&1 | grep -E "mean_volume|max_volume"
# Target: mean -20 to -22 dB, max -1 to -3 dB
```

If still too quiet for your platform, add `loudnorm=I=-16:TP=-1.5:LRA=11` for EBU R128 broadcast normalization (slower — re-encodes audio).

> **More BGM options and volume tuning:** See `references/troubleshooting.md`.
