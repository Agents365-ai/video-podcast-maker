---
name: video-podcast-maker
description: Use when the user gives a topic and wants an automated topic-driven narrated explainer, podcast, or knowledge-summary video (Bilibili / YouTube / Xiaohongshu / Douyin / WeChat Channels), or asks to learn visual design patterns from a reference video/image. Trigger when the user mentions creating a knowledge video, narrated explainer, video podcast, or talking-head topic video from a topic — even if they don't say "video podcast" explicitly. Do NOT trigger for generic video editing, trimming, format conversion, color grading, or non-narrative video tasks. Produces 4K video via research → script → TTS → Remotion → MP4 + BGM.
argument-hint: "[topic]"
effort: high
author: Agents365-ai
category: Content Creation
version: 2.3.0
created: 2025-01-27
updated: 2026-05-06
bilibili: https://space.bilibili.com/441831884
github: https://github.com/Agents365-ai/video-podcast-maker
dependencies:
  - remotion-best-practices
metadata:
  openclaw:
    requires:
      bins: [python3, ffmpeg, node, npx]
    primaryEnv: AZURE_SPEECH_KEY
    emoji: "🎬"
    homepage: https://github.com/Agents365-ai/video-podcast-maker
    os: ["macos", "linux"]
    install:
      - kind: brew
        formula: ffmpeg
        bins: [ffmpeg]
      - kind: uv
        package: edge-tts
        bins: [edge-tts]
---

> **REQUIRED: Load Remotion Best Practices First**
>
> This skill depends on `remotion-best-practices`. **You MUST invoke it before proceeding:**
> ```
> Invoke the skill/tool named: remotion-best-practices
> ```

# Video Podcast Maker

Automated pipeline for **4K Bilibili horizontal knowledge videos** from a topic. Coding agent + TTS backend + Remotion + FFmpeg.

## Contents

- [Bootstrap](#bootstrap) — update check + prerequisites (run before Step 1)
- [Execution Modes](#execution-modes) — Auto vs Interactive, default decisions
- [Workflow](#workflow) — the 15 steps + phase-file pointers + mandatory stops
- [Hard Rules](#hard-rules) — non-negotiable production constraints + output specs
- [Per-Video Layout](#per-video-layout) — directory structure, `--public-dir`, naming
- [Additional Resources](#additional-resources) — when to load each `references/` file
- [User Preferences](#user-preferences)
- [Troubleshooting](#troubleshooting)

---

## Bootstrap

Resolve `SKILL_DIR` to the directory containing this `SKILL.md`. If your agent exposes a built-in skill directory variable (e.g. `${CLAUDE_SKILL_DIR}`), map it to `SKILL_DIR`.

```bash
SKILL_DIR="${SKILL_DIR:-${CLAUDE_SKILL_DIR}}"

# 1. Update check (notify-only, throttled to 24h)
"${SKILL_DIR}/scripts/check_update.sh"

# 2. Prerequisites (CLIs + backend env vars)
python3 "${SKILL_DIR}/scripts/check_prereqs.py"
```

**`check_update.sh` output**:
- `UPDATE_AVAILABLE vX.Y.Z -> vA.B.C` — tell the user the version delta and ask before running `git -C "${SKILL_DIR}" pull --ff-only`. **Notify-only by design — never pull without consent (the skill directory belongs to the user).**
- `UP_TO_DATE` / `SKIPPED_RECENT_CHECK` / `MANUAL_INSTALL` — continue silently.

**Prereqs failures** — see README.md for setup. The check is backend-aware (resolves `TTS_BACKEND` env → `user_prefs.json` `global.tts.backend` → `edge` default), so only env vars required by the active backend are validated.

> **Design Learning shortcut**: If the user provides a reference video/image or asks to save/list/delete style profiles, see [references/design-learning.md](references/design-learning.md) instead of running the workflow below.

---

## Execution Modes

Detect at workflow start:

- "Make a video about..." / no special instructions → **Auto Mode** (default)
- "I want to control each step" / "interactive" → **Interactive Mode**

### Auto Mode defaults

Full pipeline with sensible defaults. **Mandatory stop at Step 9** (Studio review); Step 10 (4K render) only fires when the user says "render 4K" / "render final".

| Step | Decision | Auto Default |
|------|----------|-------------|
| 3 | Title position | top-center |
| 5 | Media assets | Skip (text-only animations) |
| 7 | Thumbnail method | Remotion-generated (16:9 + 4:3) |
| 9 | Outro animation | Pre-made MP4 (white/black by theme) |
| 12 | Subtitle method | Remotion-native (skip legacy FFmpeg burn) |
| 14 | Cleanup | Auto-clean temp files |

Override any default in the initial request:
- "make a video about AI, burn subtitles" → auto + subtitles on
- "use dark theme, AI thumbnails" → auto + dark + imagen
- "need screenshots" → auto + media collection enabled

### Interactive Mode

Prompts at each decision point.

---

## Workflow

At Step 1 start, create one task per step in your agent's tracker (Claude Code `TaskCreate` / Codex todo list / equivalent). Mark `in_progress` on start, `completed` on finish. Files in `videos/{name}/` are the durable record — if interrupted, inspect the directory to determine where to resume.

| # | Step | Output | Phase file |
|---|------|--------|-----------|
| 1 | Define topic direction | `topic_definition.md` | [workflow-script.md](references/workflow-script.md) |
| 2 | Research topic | `topic_research.md` | [workflow-script.md](references/workflow-script.md) |
| 3 | Design 5-7 sections | (in-memory) | [workflow-script.md](references/workflow-script.md) |
| 4 | Write narration script | `podcast.txt` | [workflow-script.md](references/workflow-script.md) |
| 4.5 | Pronunciation pre-flight (zh-CN) | `phonemes.json` | [workflow-script.md](references/workflow-script.md) |
| 5 | Collect media (Auto: skip) | `media_manifest.json` | [workflow-production.md](references/workflow-production.md) |
| 6 | Generate publish info (Part 1) | `publish_info.md` | [workflow-production.md](references/workflow-production.md) |
| 7 | Generate thumbnails (16:9 + 4:3) | `thumbnail_*.png` | [workflow-production.md](references/workflow-production.md) |
| 8 | Generate TTS audio | `podcast_audio.wav`, `timing.json` | [workflow-production.md](references/workflow-production.md) |
| **9** | **Remotion composition + Studio preview** | — | [workflow-production.md](references/workflow-production.md) |
| 10 | Render 4K video (only on user request) | `output.mp4` | [workflow-production.md](references/workflow-production.md) |
| 11 | Mix background music | `video_with_bgm.mp4` | [workflow-production.md](references/workflow-production.md) |
| 12 | Finalize (optional legacy subtitle burn) | `final_video.mp4` | [workflow-publish.md](references/workflow-publish.md) |
| 13 | Complete publish info (Part 2) | chapter timestamps | [workflow-publish.md](references/workflow-publish.md) |
| **14** | **Verify output** (`scripts/verify_output.py`) | — | [workflow-publish.md](references/workflow-publish.md) |
| 15 | Generate vertical shorts (optional) | `shorts/` | [workflow-publish.md](references/workflow-publish.md) |

**Mandatory stops** (bold rows above):
- **Step 9 — Studio review.** MUST launch `npx remotion studio` and wait for user feedback before rendering. NEVER render 4K until the user explicitly confirms ("render 4K" / "render final").
- **Step 14 — `verify_output.py`.** MUST pass before declaring the video done. Exit 0 = green; exit 2 = warnings still publishable. Auto-fixes common omissions (creates `final_video.mp4` if missing). For machine-readable output add `--format json` (auto when piped).

**Pre-render audit (recommended)** — before Step 9:
```bash
python3 ${SKILL_DIR}/scripts/audit_beat_sync.py <Video.tsx> <timing.json>
```
Flags beats that drift > 1.5s from narration. Especially important for kinetic-typography videos.

### Validation Checkpoints

| After Step | Check |
|-----------|-------|
| 8 (TTS) | `podcast_audio.wav` plays · `timing.json` covers all sections · SRT is UTF-8 |
| 10 (Render) | `output.mp4` is 3840×2160 · audio-video sync · no black frames |
| 14 (Verify) | `verify_output.py` exits 0 (or 2 with reviewed warnings) |

---

## Hard Rules

| Rule | Requirement |
|------|-------------|
| **Single Project** | All videos under `videos/{name}/` in user's Remotion project. NEVER create a new project per video. |
| **4K Output** | 3840×2160 (or 2160×3840 vertical), use `scale(2)` wrapper over 1920×1080 design space |
| **Audio Sync** | All animations driven by `timing.json` timestamps |
| **Thumbnail** | MUST generate both 16:9 (1920×1080) AND 4:3 (1200×900) — see [design-guide.md](references/design-guide.md) |
| **Studio Before Render** | MUST launch `remotion studio` for review. NEVER render 4K until user explicitly confirms. |
| **`--public-dir`** | Every Remotion command uses `--public-dir videos/{name}/` |

Visual minimums (text sizes, content width, safe zones, animation safety) live in [references/design-guide.md](references/design-guide.md). **MUST load before Step 9.**

### Output Specs

| Parameter | Horizontal (16:9) | Vertical (9:16) |
|-----------|-------------------|-----------------|
| Resolution | 3840×2160 (4K) | 2160×3840 (4K) |
| Frame rate | 30 fps | 30 fps |
| Encoding | H.264, 16Mbps | H.264, 16Mbps |
| Audio | AAC, 192kbps | AAC, 192kbps |
| Duration | 1-15 min | 60-90s (highlight) |

---

## Per-Video Layout

```
project-root/                           # Remotion project root
├── src/remotion/                       # Remotion source (Root.tsx, compositions, index.ts)
├── videos/{video-name}/                # Per-video assets (the agent's working dir)
│   ├── topic_definition.md             # Step 1
│   ├── topic_research.md               # Step 2
│   ├── podcast.txt                     # Step 4: narration script
│   ├── phonemes.json                   # Step 4.5: zh-CN pronunciation overrides
│   ├── podcast_audio.wav               # Step 8: TTS audio
│   ├── podcast_audio.srt               # Step 8: subtitles
│   ├── timing.json                     # Step 8: timeline (drives animations)
│   ├── thumbnail_*.png                 # Step 7
│   ├── output.mp4                      # Step 10: 4K render (no BGM)
│   ├── video_with_bgm.mp4              # Step 11
│   ├── final_video.mp4                 # Step 12: final output
│   └── bgm.mp3                         # Background music
└── remotion.config.ts
```

### `--public-dir` per video

Remotion commands MUST use `--public-dir videos/{name}/` — each video's assets stay in its own directory, no copy to `public/`. Enables parallel renders.

```bash
npx remotion studio src/remotion/index.ts --public-dir videos/{name}/
npx remotion render src/remotion/index.ts CompositionId videos/{name}/output.mp4 --public-dir videos/{name}/ --video-bitrate 16M
npx remotion still src/remotion/index.ts Thumbnail16x9 videos/{name}/thumbnail.png --public-dir videos/{name}/
```

### Naming

- **Video name `{video-name}`**: lowercase English, hyphen-separated (e.g. `reference-manager-comparison`)
- **Section name `{section}`**: lowercase English, underscore-separated, matches `[SECTION:xxx]`
- **Thumbnail naming** (16:9 AND 4:3 both required):

| Type | 16:9 | 4:3 |
|------|------|-----|
| Remotion | `thumbnail_remotion_16x9.png` | `thumbnail_remotion_4x3.png` |
| AI | `thumbnail_ai_16x9.png` | `thumbnail_ai_4x3.png` |

---

## Additional Resources

Load on demand — **do NOT load all at once**:

| File | Load when |
|------|-----------|
| [references/workflow-script.md](references/workflow-script.md) | Steps 1-4 (topic → script) |
| [references/workflow-production.md](references/workflow-production.md) | Steps 5-11 (media → TTS → Remotion → render → BGM) |
| [references/workflow-publish.md](references/workflow-publish.md) | Steps 12-15 (subtitles, publish, cleanup, shorts) |
| [references/design-guide.md](references/design-guide.md) | **MUST load before Step 9** — visual minimums, typography, animation safety |
| [references/design-learning.md](references/design-learning.md) | User provides a reference video/image, or manages style profiles |
| [references/azure-tts-pitfalls.md](references/azure-tts-pitfalls.md) | Choosing Azure voice/style, debugging hoarse/glitchy audio |
| [references/troubleshooting.md](references/troubleshooting.md) | On error, or user asks about preferences/BGM |
| [templates/presets/kinetic-typography/](templates/presets/kinetic-typography/) | Bold type-driven preset (opinion / argument / declaration videos) |
| [examples/](examples/) | Reference for composition structure and `timing.json` format |

### Script suite dispatcher

All scripts under `${SKILL_DIR}/scripts/` are reachable through one hierarchical entry point:

```bash
python3 ${SKILL_DIR}/scripts/cli.py --help                  # list resources
python3 ${SKILL_DIR}/scripts/cli.py <resource> --help       # list actions
python3 ${SKILL_DIR}/scripts/cli.py <resource> <action> --help    # forwards to underlying script
python3 ${SKILL_DIR}/scripts/cli.py schema [<method>]       # JSON parameter schema
```

Routes: `tts run|validate`, `verify`, `audit beats`, `shorts gen`, `design list|show|delete|add`, `prereqs`, `prefs get|migrate|backend|bgm-path`, `schema [<method>]`. Direct script invocation (`python3 scripts/<name>.py ...`) keeps working — the dispatcher is additive.

---

## User Preferences

Skill auto-learns and applies preferences. Full commands and learning details: [references/troubleshooting.md](references/troubleshooting.md).

- **Storage**: `user_prefs.json` (auto-created from `user_prefs.template.json`, schema in `prefs_schema.json`).
- **Priority**: `Root.tsx defaults < global < topic_patterns[type] < current instructions`.
- **User commands**: "show preferences" · "reset preferences" · "save as X default".

---

## Troubleshooting

See [references/troubleshooting.md](references/troubleshooting.md) on errors, BGM options, preference learning, design-learning issues.
