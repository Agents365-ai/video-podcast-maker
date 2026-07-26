---
name: video-podcast-maker
description: Use when the user gives a topic and wants an automated topic-driven narrated explainer, podcast, or knowledge-summary video (Bilibili / YouTube / Xiaohongshu / Douyin / WeChat Channels), or asks to learn visual design patterns from a reference video/image. Trigger when the user mentions creating a knowledge video, narrated explainer, video podcast, or animated infographic-style video from a topic — even if they don't say "video podcast" explicitly. Also trigger when the user wants to regenerate, re-render, rebuild, update, or iterate on a narrated video this skill already produced — e.g. they edited the script/prompt, changed the visuals, or swapped the background music and want the final video remade (reuse the existing videos/{name}/ directory, never start a new project). Do NOT trigger for generic video editing, trimming, format conversion, color grading, or non-narrative video tasks. Produces 4K video via research → script → TTS → Remotion → MP4 + BGM.
argument-hint: "[topic]"
effort: high
author: Agents365-ai
category: Content Creation
version: 4.2.1
created: 2025-01-27
updated: 2026-07-18
permissions:
  - env
  - file_read
  - file_write
  - network
  - shell
bilibili: https://space.bilibili.com/441831884
github: https://github.com/Agents365-ai/video-podcast-maker
dependencies:
  - remotion-best-practices
metadata:
  openclaw:
    requires:
      bins: [python3, ffmpeg, node, npx]
      env: []
    emoji: "🎬"
    homepage: https://github.com/Agents365-ai/video-podcast-maker
    os: ["macos", "linux"]
    install:
      - kind: brew
        formula: ffmpeg
        bins: [ffmpeg]
---

> **REQUIRED: Load Remotion Best Practices First**
>
> This skill depends on `remotion-best-practices`.
>
> - **Pi**: read the loaded skill at `remotion-best-practices` (listed in available skills).
> - **Claude Code**: invoke `remotion-best-practices` skill/tool before proceeding.
>
> Not installed? Get it from [remotion-dev/skills](https://github.com/remotion-dev/skills) (docs: [remotion.dev/docs/ai/skills](https://www.remotion.dev/docs/ai/skills)).
>
> If `remotion-best-practices` is not installed, minimum rules: chromium must be available, always wrap 4K content in `<Scale4K>`, use `<TransitionSeries>` with `linearTiming`, and treat audio as the master clock.

# Video Podcast Maker

Automated pipeline for **4K Bilibili horizontal knowledge videos** from a topic. Coding agent + TTS backend + Remotion + FFmpeg.

## Contents

- [Bootstrap](#bootstrap) — prerequisites (run before Step 1)
- [Execution Modes](#execution-modes) — Auto vs Interactive → [references/workflow-script.md](references/workflow-script.md)
- [Regenerating an Existing Video](#regenerating-an-existing-video) — iterate on a finished video
- [Workflow](#workflow) — the 10 steps + phase-file pointers + mandatory stops
- [Hard Rules](#hard-rules) — non-negotiable production constraints
- [Audio-Master Clock & Sync](#audio-master-clock--sync)
- [Per-Video Layout](#per-video-layout)
- [Additional Resources](#additional-resources) — when to load each `references/` file
- [User Preferences](#user-preferences)
- [Troubleshooting](#troubleshooting)

---

## Bootstrap

Resolve `SKILL_DIR` to the directory containing this `SKILL.md`:

- **Pi**: the agent knows the skill path from the loaded skill list — set `SKILL_DIR` to that directory before running commands.
- **Claude Code**: `${CLAUDE_SKILL_DIR}` is auto-populated.

```bash
SKILL_DIR="${SKILL_DIR:-${CLAUDE_SKILL_DIR}}"

# Prerequisites (CLIs + backend env vars)
python3 "${SKILL_DIR}/scripts/check_prereqs.py"
```

Updates flow through the plugin marketplace (`/plugin update`); direct git-clone installs use `git pull` per the README. This skill performs no update checks.

**Prereqs failures** — see README.md for setup. The check is backend-aware (resolves `TTS_BACKEND` env → `user_prefs.json` `global.tts.backend` → `edge` default), so only env vars required by the active backend are validated.

**First video in a new project?** Prefer reusing an existing Remotion project with `node_modules/` already installed — creating a fresh project downloads ~2.2 GB of npm packages plus a 90 MB Chrome headless shell (one-time per project). If the user has a project from a previous video, use it. If a fresh project is necessary, run `npm install` in the background while you do Steps 1-4 (topic research and script writing).

**All rendering goes into `videos/{name}/`** — every `output.mp4`, `final_video.mp4`, and `thumbnail_*.png` lands directly in the per-video directory. Never render to an `out/` or `dist/` directory; the `--public-dir videos/{name}/` convention keeps everything self-contained.

**TTS engine** — all 11 backends (`TTS_BACKEND=edge|azure|cosyvoice|doubao|tencent|baidu|minimax|xunfei|elevenlabs|openai|google`, plus the legacy `ttscn` alias) synthesize through the **ttsCN component skill**, which is **required**: install it under `~/.claude/skills/ttsCN` or point `TTSCN_HOME` at its root ([Agents365-ai/ttsCN](https://github.com/Agents365-ai/ttsCN)). Each backend still needs only its own API keys (Edge needs none); `check_prereqs.py` validates both the install and the keys.

> **Design Learning shortcut**: If the user provides a reference video/image or asks to save/list/delete style profiles, see [references/design-learning.md](references/design-learning.md) instead of running the workflow below.

---

## Execution Modes

Detect Auto Mode (default) vs Interactive Mode at workflow start — the Auto-default decision table and per-request overrides are in [references/workflow-script.md](references/workflow-script.md#execution-modes).

---

## Regenerating an Existing Video

If `videos/{name}/` **already exists** and the user is iterating on a finished or in-progress video, **reuse that directory**. Do NOT start a new project or a new `videos/{newname}/`.

Pick the **smallest** re-run for what actually changed:

| Changed | Re-run | Reuses (don't redo) |
| --------- | -------- | --------------------- |
| Narration script (`podcast.txt`) | Step 7 (TTS) → Step 8 preview → render+mix | topic research + section design |
| Visuals only (components, layout, colors) | Step 8 preview → render+mix | audio (`podcast_audio.wav` / `timing.json`) |
| Background music only | Re-mix BGM | `output.mp4` (no re-render) |
| Subtitles only | Step 10 finalize | `output.mp4` / `video_with_bgm.mp4` |

Any re-run that changes what the viewer **sees or hears** re-enters the Step 8 gate: apply the change, let Studio hot-reload, and wait for a fresh explicit "render 4K" — the previous confirmation does **not** carry over. A **script** change shifts every downstream timestamp, so always regenerate `timing.json` through TTS — never hand-edit it. After any re-run, re-verify:

```bash
python3 ${SKILL_DIR}/scripts/verify_output.py videos/{name}/
```

---

## Workflow

> **Iterating on a finished video?** If `videos/{name}/` already exists, see [Regenerating an Existing Video](#regenerating-an-existing-video) above for the minimal re-run — do NOT start at Step 1.

At Step 1 start, create one task per step in your agent's tracker. Mark `in_progress` on start, `completed` on finish. Files in `videos/{name}/` are the durable record — if interrupted, inspect the directory to determine where to resume.

| # | Step | Output | Phase file |
| --- | ------ | -------- | ----------- |
| 1 | Define topic direction | `topic_definition.md` | [workflow-script.md](references/workflow-script.md) |
| 2 | Research topic | `topic_research.md` | [workflow-script.md](references/workflow-script.md) |
| 3 | Design 5-7 sections | (in-memory) | [workflow-script.md](references/workflow-script.md) |
| 4 | Write narration script | `podcast.txt` | [workflow-script.md](references/workflow-script.md) |
| 4.5 | Pronunciation pre-flight (zh-CN) | `phonemes.json` | [workflow-script.md](references/workflow-script.md) |
| 5 | Asset plan & resolve | `assets/manifest.json` | [workflow-assets.md](references/workflow-assets.md) |
| 6 | Generate thumbnails (16:9 + 4:3) | `thumbnail_*.png` | [workflow-production.md](references/workflow-production.md) |
| 7 | Generate TTS audio | `podcast_audio.wav`, `timing.json` | [workflow-production.md](references/workflow-production.md) |
| **8** | **Remotion composition + Studio preview** | — | [workflow-production.md](references/workflow-production.md) |
| 9 | Render 4K + mix BGM | `output.mp4`, `video_with_bgm.mp4` | [workflow-production.md](references/workflow-production.md) |
| **10** | **Publish info + verify output** | `publish_info.md`, `final_video.mp4` | [workflow-publish.md](references/workflow-publish.md) |
| 11 | Generate vertical shorts (optional) | `shorts/` | [workflow-publish.md](references/workflow-publish.md) |

**Mandatory stops** (bold rows above):

- **Step 8 — Studio review.** MUST launch `npx remotion studio` and wait for user feedback before rendering. NEVER render 4K until the user explicitly confirms ("render 4K" / "render final"). A reply containing adjustment requests is **not** confirmation — apply the changes, let Studio hot-reload, and ask again. Every round of adjustments needs its own fresh confirmation before Step 9.
- **Step 10 — `verify_output.py`.** MUST pass before declaring the video done. Exit 0 = green; exit 2 = warnings still publishable. Auto-fixes common omissions (creates `final_video.mp4` if missing). Generates publish info (title, description, tags, chapter timestamps) from the platform matrix. For machine-readable output add `--format json`.

**Pre-render audit (recommended)** — before Step 8:

```bash
python3 ${SKILL_DIR}/scripts/audit_beat_sync.py <Video.tsx> <timing.json>
```

Flags beats that drift > 1.5s from narration.

**Auto Mode: visual self-review.** When running in Auto Mode (no user watching Studio), render 3-5 key frame stills before asking for render confirmation:

```bash
npx remotion still src/remotion/index.ts <CompositionId> videos/{name}/_review_001.png --public-dir videos/{name}/ --frame=<midpoint_frame>
```

Pick frames at: hero title (~10% in), a dense section midpoint, and the outro. Read the stills back as images and run the [design-guide.md](references/design-guide.md) and [visual-taste.md](references/visual-taste.md) checklists against actual rendered output. Catch overflow, contrast, and layout regressions before the 4K render. Delete `_review_*.png` after review.

### Validation Checkpoints

| After Step | Check |
| ----------- | ------- |
| 7 (TTS) | `podcast_audio.wav` plays · `timing.json` covers all sections · SRT is UTF-8 |
| 9 (Render) | `output.mp4` is 3840×2160 · audio-video sync · no black frames |
| 10 (Verify) | `verify_output.py` exits 0 (or 2 with reviewed warnings) |

---

## Hard Rules

| Rule | Requirement |
| ------ | ------------- |
| **Single Project** | All videos under `videos/{name}/` in user's Remotion project. NEVER create a new project per video. |
| **4K Output** | 3840×2160 (or 2160×3840 vertical), use `scale(2)` wrapper over 1920×1080 design space |
| **Audio Sync** | Audio (`podcast_audio.wav` + `podcast_audio.srt`) is the master clock. `timing.json` MUST be generated from the real TTS output, never hand-estimated. Before rendering, final video duration must match audio within ±0.5s. See [Audio-Master Clock & Sync](#audio-master-clock--sync). |
| **Thumbnail** | MUST generate both 16:9 (1920×1080) AND 4:3 (1200×900) — see [design-guide.md](references/design-guide.md) |
| **Studio Before Render** | MUST launch `remotion studio` for review. NEVER render 4K until user explicitly confirms. Adjustment feedback ≠ confirmation — apply, hot-reload, ask again. |
| **`--public-dir`** | Every Remotion command uses `--public-dir videos/{name}/`. All output files (output.mp4, final_video.mp4, thumbnails) go directly into `videos/{name}/` — never an `out/` or `dist/` dir. |

Visual minimums (text sizes, content width, safe zones, animation safety) live in [references/design-guide.md](references/design-guide.md). **MUST load before Step 9.**

## Audio-Master Clock & Sync

### Golden rules

1. **Audio is the master clock.** Every slide start, subtitle, chapter, and animation beat is derived from `podcast_audio.wav` and `podcast_audio.srt`.
2. **Generate timing from TTS, not from text estimates.** Pipeline: `podcast.txt` → `generate_tts.py` → `podcast_audio.wav` + `podcast_audio.srt` + `timing.json` → composition → render.
3. **Never hand-write `timing.json` before audio exists.** If you already have curated slides, run `align_timing_from_srt.py` to anchor them to the real SRT.
4. **Compensate TransitionSeries overlap.** `TransitionSeries` renders `sum(section.duration_frames) - (N-1) * transitionFrames` frames. Scale every section proportionally to keep the rendered length equal to `timing.total_frames`. Do **not** stuff all overlap frames into the first section. The corrected pattern is in `templates/Video.tsx`.

### Mandatory sync checkpoints

| When | Check |
| ------ | ------- |
| After Step 7 (TTS) | `timing.json.total_duration` matches `podcast_audio.wav` within ±0.5s |
| Before render | `Video.tsx` scales all sections for transition overlap |
| After render | `final_video.mp4` duration matches `podcast_audio.wav` within ±0.5s |
| Step 10 (verify) | `verify_output.py` exits 0 and reports green on audio/timing |

If any checkpoint fails, stop. Do not publish.

### Output Specs

| Parameter | Horizontal (16:9) | Vertical (9:16) |
| ----------- | ------------------- | ----------------- |
| Resolution | 3840×2160 (4K) | 2160×3840 (4K) |
| Frame rate | 30 fps | 30 fps |
| Encoding | H.264, 16Mbps | H.264, 16Mbps |
| Audio | AAC, 192kbps | AAC, 192kbps |
| Duration | 1-15 min | 60-90s (highlight) |

## Per-Video Layout

```
project-root/                           # Remotion project root
├── src/remotion/                       # Remotion source (Root.tsx, compositions, index.ts)
├── videos/{video-name}/                # Per-video directory
│   ├── topic_definition.md             # Step 1
│   ├── topic_research.md               # Step 2
│   ├── podcast.txt                     # Step 4: narration script
│   ├── phonemes.json                   # Step 4.5: zh-CN pronunciation overrides
│   ├── assets/manifest.json            # Step 5: per-section asset registry
│   ├── publish_info.md                 # Step 10: title/description/tags
│   ├── podcast_audio.wav               # Step 7: TTS audio
│   ├── podcast_audio.srt               # Step 7: subtitles
│   ├── timing.json                     # Step 7: timeline (drives animations)
│   ├── thumbnail_*.png                 # Step 6
│   ├── output.mp4                      # Step 9: 4K render
│   ├── video_with_bgm.mp4              # Step 9: with BGM
│   ├── final_video.mp4                 # Step 10: final output
│   └── bgm.mp3                         # Background music
└── remotion.config.ts
```

### `--public-dir` per video

Every Remotion command uses `--public-dir videos/{name}/` — each video's assets stay in its own directory, enabling parallel renders:

```bash
npx remotion studio src/remotion/index.ts --public-dir videos/{name}/
npx remotion render ... videos/{name}/output.mp4 --public-dir videos/{name}/ --video-bitrate 16M
npx remotion still ... videos/{name}/thumbnail.png --public-dir videos/{name}/
```

### Naming

- **Video name `{video-name}`**: lowercase English, hyphen-separated (e.g. `reference-manager-comparison`)
- **Section name `{section}`**: lowercase English, underscore-separated, matches `[SECTION:xxx]`
- **Thumbnails** (16:9 AND 4:3 both required): `thumbnail_remotion_16x9.png` + `thumbnail_remotion_4x3.png` (or `_ai_` prefix for AI-generated)

---

## Additional Resources

Load on demand — **do NOT load all at once**:

| File | Load when |
| ------ | ----------- |
| [references/workflow-script.md](references/workflow-script.md) | Steps 1-4 (topic → script) + Execution Modes (Auto vs Interactive) |
| [references/natural-narration.md](references/natural-narration.md) | **Load before Step 4 script writing** — anti-slop rules for spoken narration (kill list, structural tells, checklist) |
| [references/script-polish.md](references/script-polish.md) | **Load after Step 4 draft is written** — deep editing toolkit with 24 EN+ZH before/after patterns, evidence boundaries, quality rubrics |
| [references/workflow-assets.md](references/workflow-assets.md) | Step 5, or when the user supplies images/clips or wants stock/AI media |
| [references/workflow-assets.md](references/workflow-assets.md#transparent-overlays-via-hyperframes-free-needs-node-22) | A section needs a data-chart/infographic animation beyond the component library (transparent overlay via Hyperframes) |
| [references/workflow-production.md](references/workflow-production.md) | Steps 6-9 (thumbnails → TTS → Remotion → render + BGM) |
| [references/workflow-publish.md](references/workflow-publish.md) | Steps 10-11 (publish info, verify, shorts) |
| [references/platform-matrix.md](references/platform-matrix.md) | Platform-specific behavior (thumbnails, chapters, outro, publish info, shorts) |
| [references/design-guide.md](references/design-guide.md) | **MUST load before Step 9** — visual minimums, typography, animation safety |
| [references/visual-taste.md](references/visual-taste.md) | **Load before Step 9** alongside design-guide — design dials, anti-default rules, visual modes, section rhythm |
| [references/design-learning.md](references/design-learning.md) | User provides a reference video/image, or manages style profiles |
| [references/troubleshooting.md](references/troubleshooting.md#azure-tts-deep-dive) | Choosing Azure voice/style, debugging hoarse/glitchy audio |
| [references/troubleshooting.md](references/troubleshooting.md) | On error, script/CLI discovery, or user asks about preferences/BGM |
| [templates/presets/kinetic-typography/](templates/presets/kinetic-typography/) | Bold type-driven preset (opinion / argument / declaration videos) |

All scripts are reachable through one dispatcher — start with `python3 ${SKILL_DIR}/scripts/cli.py --help`; full routes and envelope error codes: [references/troubleshooting.md](references/troubleshooting.md#discovery-when-youre-not-sure-which-script-to-run).

---

## User Preferences

Preferences are stored in `user_prefs.json`. Run "show preferences" to view, or "set X Y" to change. Full commands: [references/troubleshooting.md](references/troubleshooting.md).

---

## Troubleshooting

See [references/troubleshooting.md](references/troubleshooting.md) on errors, BGM options, preference learning, design-learning issues.
