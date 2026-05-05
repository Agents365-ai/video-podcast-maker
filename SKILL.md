---
name: video-podcast-maker
description: Use when the user gives a topic and wants an automated video podcast created, or asks to learn visual design patterns from a reference video/image. Make sure to use this skill whenever the user mentions creating a video, podcast, knowledge video, Bilibili content, or talking-head explainer from a topic — even if they don't say "video podcast" explicitly. Produces 4K video via research → script → TTS → Remotion → MP4 + BGM.
argument-hint: "[topic]"
effort: high
# `allowed-tools` intentionally omitted — the workflow uses Bash, Read, Write, Edit,
# Glob, Grep, WebFetch, WebSearch, Agent, AND optional MCP tools (Playwright for
# design learning). Listing a closed set here would silently break the Playwright
# fallback. Defer tool gating to the user's Claude Code permission settings.
# --- Frontmatter fields above are primarily for Claude Code / OpenClaw.
# Other agents such as Codex should ignore unknown fields and follow the workflow below. ---
author: Agents365-ai
category: Content Creation
version: 2.0.0
created: 2025-01-27
updated: 2026-04-03
bilibili: https://space.bilibili.com/441831884
github: https://github.com/Agents365-ai/video-podcast-maker
# `dependencies` is informational only — Claude Code does not auto-load skills
# from this list. The agent must invoke `remotion-best-practices` per the body
# section below. Kept for OpenClaw / SkillsMP discovery metadata.
dependencies:
  - remotion-best-practices
metadata:
  openclaw:
    requires:
      bins:
        - python3
        - ffmpeg
        - node
        - npx
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

## Quick Start

Open your coding agent and say: **"Make a video podcast about $ARGUMENTS"**

Or invoke directly: `/video-podcast-maker AI Agent tutorial`

---

## Design Learning (Optional)

Extract visual design patterns from reference videos or images and apply them to new video compositions. **Skip this section unless** the user provides a reference video/image or asks to save/list/delete style profiles.

→ See **[references/design-learning.md](references/design-learning.md)** for commands, reference-library management, style-profile management, and integration with Pre-workflow / Step 9.

---

## Auto Update Check

**Agent behavior:** Check for updates at most once per day (throttled by timestamp file). Compare the frontmatter `version` against the latest `v*` tag on the upstream remote — release tags are the explicit "this is intended for users" signal; comparing against every commit on `main` would fire on docs-only edits and unreleased work-in-progress.
Before any shell command that reads files from this skill, resolve `SKILL_DIR` to the directory containing `SKILL.md`.
If your agent exposes a built-in skill directory variable such as `${CLAUDE_SKILL_DIR}`, you may map it to `SKILL_DIR`.

```bash
SKILL_DIR="${SKILL_DIR:-${CLAUDE_SKILL_DIR}}"
STAMP="${SKILL_DIR}/.last_update_check"
NOW=$(date +%s)
LAST=$(cat "$STAMP" 2>/dev/null || echo 0)
if [ ! -d "${SKILL_DIR}/.git" ]; then
  echo "MANUAL_INSTALL"
elif [ $((NOW - LAST)) -le 86400 ]; then
  echo "SKIPPED_RECENT_CHECK"
else
  echo "$NOW" > "$STAMP"
  CURRENT=$(awk '/^version:/ {print $2; exit}' "${SKILL_DIR}/SKILL.md" | tr -d '"')
  LATEST=$(timeout 5 git -C "${SKILL_DIR}" ls-remote --tags origin 'v*' 2>/dev/null \
    | awk '{print $2}' | sed 's|refs/tags/||' | sort -V | tail -1 | sed 's/^v//')
  if [ -z "$CURRENT" ] || [ -z "$LATEST" ] || [ "$CURRENT" = "$LATEST" ]; then
    echo "UP_TO_DATE"
  elif [ "$(printf '%s\n%s\n' "$CURRENT" "$LATEST" | sort -V | tail -1)" = "$LATEST" ]; then
    echo "UPDATE_AVAILABLE v${CURRENT} -> v${LATEST}"
  else
    echo "UP_TO_DATE"
  fi
fi
```

- **Update available**: Tell the user the version delta (e.g. `v2.0.0 → v2.1.0`) and ask whether to pull. Yes → `git -C "${SKILL_DIR}" pull --ff-only`. No → continue. Notify-only by design — never `git pull` without consent (the skill directory belongs to the user, not the agent).
- **Up to date / Skipped**: Continue silently.
- **Manual install** (no `.git` directory — skill was installed via tarball/zip/cp): Continue silently. Auto-update is disabled; the user must reinstall manually to update.

---

## Prerequisites Check

**Agent behavior:** Run the pre-flight check below before Step 1. `SKILL_DIR` must already be resolved (see Auto Update Check section above for resolution rules).

```bash
SKILL_DIR="${SKILL_DIR:-${CLAUDE_SKILL_DIR}}"
python3 "${SKILL_DIR}/scripts/check_prereqs.py"
```

**If MISSING reported**, see README.md for full setup instructions (install commands, API key setup, Remotion project init). The check is backend-aware: backend is resolved as `TTS_BACKEND` env var → `user_prefs.json` (`global.tts.backend`) → `edge` default, then only env vars required by that backend are validated.

---

## Overview

Automated pipeline for professional **Bilibili horizontal knowledge videos** from a topic.

> **Target: Bilibili horizontal video (16:9)**
> - Resolution: 3840×2160 (4K) or 1920×1080 (1080p)
> - Style: Clean white (default)

**Tech stack:** Coding agent + TTS backend + Remotion + FFmpeg

### Output Specs

| Parameter | Horizontal (16:9) | Vertical (9:16) |
|-----------|-------------------|-----------------|
| **Resolution** | 3840×2160 (4K) | 2160×3840 (4K) |
| **Frame rate** | 30 fps | 30 fps |
| **Encoding** | H.264, 16Mbps | H.264, 16Mbps |
| **Audio** | AAC, 192kbps | AAC, 192kbps |
| **Duration** | 1-15 min | 60-90s (highlight) |

---

## Execution Modes

**Agent behavior:** Detect user intent at workflow start:

- "Make a video about..." / no special instructions → **Auto Mode**
- "I want to control each step" / mentions interactive → **Interactive Mode**
- Default: **Auto Mode**

### Auto Mode (Default)

Full pipeline with sensible defaults. **Mandatory stop at Step 9:**

1. **Step 9**: Launch Remotion Studio — user reviews in real-time, requests changes until satisfied
2. **Step 10**: Only triggered when user explicitly says "render 4K" / "render final version"

| Step | Decision | Auto Default |
|------|----------|-------------|
| 3 | Title position | top-center |
| 5 | Media assets | Skip (text-only animations) |
| 7 | Thumbnail method | Remotion-generated (16:9 + 4:3) |
| 9 | Outro animation | Pre-made MP4 (white/black by theme) |
| 9 | Preview method | Remotion Studio (mandatory) |
| 12 | Subtitles | Skip |
| 14 | Cleanup | Auto-clean temp files |

Users can override any default in their initial request:
- "make a video about AI, burn subtitles" → auto + subtitles on
- "use dark theme, AI thumbnails" → auto + dark + imagen
- "need screenshots" → auto + media collection enabled

### Interactive Mode

Prompts at each decision point. Activated by:
- "interactive mode" / "I want to choose each option"
- User explicitly requests control

---

## Technical Rules

Hard constraints for video production. Visual design remains the agent's creative freedom within these rules:

| Rule | Requirement |
|------|-------------|
| **Single Project** | All videos under `videos/{name}/` in user's Remotion project. NEVER create a new project per video. |
| **4K Output** | 3840×2160, use `scale(2)` wrapper over 1920×1080 design space |
| **Content Width** | ≥85% of screen width |
| **Bottom Safe Zone** | Bottom 100px reserved for subtitles |
| **Audio Sync** | All animations driven by `timing.json` timestamps |
| **Thumbnail** | MUST generate 16:9 (1920×1080) AND 4:3 (1200×900). Centered layout, title ≥120px, icons ≥120px, fill most of canvas. See design-guide.md. |
| **Font** | PingFang SC / Noto Sans SC for Chinese text |
| **Studio Before Render** | MUST launch `remotion studio` for user review. NEVER render 4K until user explicitly confirms ("render 4K", "render final"). |

---

## Additional Resources

Load these files on demand — **do NOT load all at once**:

- **[references/workflow-steps.md](references/workflow-steps.md)**: Index of the 15-step workflow split across three phase files. Load at workflow start to locate which phase file to pull:
  - **[workflow-script.md](references/workflow-script.md)** — Pre-workflow + Startup + Steps 1-4 (scripting)
  - **[workflow-production.md](references/workflow-production.md)** — Steps 5-11 (media, TTS, Remotion, render, BGM)
  - **[workflow-publish.md](references/workflow-publish.md)** — Steps 12-15 (subtitles, publish, cleanup, shorts)
- **[references/design-guide.md](references/design-guide.md)**: Visual minimums, typography, layout patterns, checklists, **animation safety rules**. **MUST load before Step 9.**
- **[references/design-learning.md](references/design-learning.md)**: Extracting visual patterns from reference videos/images, style profiles. Load only when the user provides a reference or manages profiles.
- **[references/azure-tts-pitfalls.md](references/azure-tts-pitfalls.md)**: Voice selection guide, Multilingual gotchas, SSML pitfalls, style support matrix. **Load when choosing Azure voice/style or debugging hoarse/missing/glitchy audio.**
- **[references/troubleshooting.md](references/troubleshooting.md)**: Error fixes, BGM options, preference commands, preference learning. Load on error or user request.
- **[templates/presets/kinetic-typography/](templates/presets/kinetic-typography/)**: Bold type-driven preset (black BG + mint/yellow accents + character-pop animations). Use for opinion / argument / declaration videos. Load README first.
- **[examples/](examples/)**: Real production video projects. The agent may reference these for composition structure and `timing.json` format.

### Script suite dispatcher (optional)

All scripts in `${SKILL_DIR}/scripts/` are reachable through one hierarchical entry point:

```bash
python3 ${SKILL_DIR}/scripts/cli.py --help                 # list resources
python3 ${SKILL_DIR}/scripts/cli.py <resource> --help      # list actions
python3 ${SKILL_DIR}/scripts/cli.py <resource> <action> --help  # forwards to underlying script
python3 ${SKILL_DIR}/scripts/cli.py schema [<method>]      # JSON parameter schema
```

Routes (all forward to the existing scripts; direct invocations keep working):
`tts run|validate`, `verify`, `audit beats`, `shorts gen`, `design list|show|delete|add`, `prereqs`, `prefs get|migrate|backend|bgm-path`, `schema [<method>]`.

The dispatcher is optional — every snippet in this file uses the direct script path for back-compat. Agents that prefer one entry point with discoverable help should prefer `cli.py`.

### Pre-render audit (recommended)

Before launching Studio for Step 9 review:
```bash
python3 ${SKILL_DIR}/scripts/audit_beat_sync.py <Video.tsx> <timing.json>
```
Prints a beat-vs-narration alignment table and flags drift > 1.5s. Especially important for kinetic-typography style where each beat must hit a specific narration moment.

### End-of-pipeline acceptance gate (MANDATORY)

After Step 13, before declaring the video done:
```bash
python3 ${SKILL_DIR}/scripts/verify_output.py videos/{name}/
```
Auto-fixes common omissions (creates `final_video.mp4` if missing; disable with `--no-fix`), validates resolution/codec/duration, checks audio-timing drift, sanity-checks publish_info.md. Exit 0 = green light to publish; exit 2 = warnings only, still publishable. For machine-readable output add `--format json` (auto when piped). Full flag reference in `references/workflow-publish.md`.

---

## Directory Structure

```
project-root/                           # Remotion project root
├── src/remotion/                       # Remotion source
│   ├── compositions/                   # Video composition definitions
│   ├── Root.tsx                        # Remotion entry
│   └── index.ts                        # Exports
│
├── public/                             # Remotion default (unused — use --public-dir videos/{name}/)
│
├── videos/{video-name}/                # Video project assets
│   ├── topic_definition.md             # Step 1
│   ├── topic_research.md               # Step 2
│   ├── podcast.txt                     # Step 4: narration script
│   ├── podcast_audio.wav               # Step 8: TTS audio
│   ├── podcast_audio.srt               # Step 8: subtitles
│   ├── timing.json                     # Step 8: timeline
│   ├── thumbnail_*.png                 # Step 7
│   ├── output.mp4                      # Step 10
│   ├── video_with_bgm.mp4             # Step 11
│   ├── final_video.mp4                 # Step 12: final output
│   └── bgm.mp3                         # Background music
│
└── remotion.config.ts
```

> **Important**: Always use `--public-dir` and full output path for Remotion render:
> ```bash
> npx remotion render src/remotion/index.ts CompositionId videos/{name}/output.mp4 --public-dir videos/{name}/
> ```

### Naming Rules

**Video name `{video-name}`**: lowercase English, hyphen-separated (e.g., `reference-manager-comparison`)

**Section name `{section}`**: lowercase English, underscore-separated, matches `[SECTION:xxx]`

**Thumbnail naming** (16:9 AND 4:3 both required):
| Type | 16:9 | 4:3 |
|------|------|-----|
| Remotion | `thumbnail_remotion_16x9.png` | `thumbnail_remotion_4x3.png` |
| AI | `thumbnail_ai_16x9.png` | `thumbnail_ai_4x3.png` |

### Public Directory

Use `--public-dir videos/{name}/` for all Remotion commands. Each video's assets (timing.json, podcast_audio.wav, bgm.mp3) stay in its own directory — no copying to `public/` needed. This enables parallel renders of different videos.

```bash
# All render/studio/still commands use --public-dir
npx remotion studio src/remotion/index.ts --public-dir videos/{name}/
npx remotion render src/remotion/index.ts CompositionId videos/{name}/output.mp4 --public-dir videos/{name}/ --video-bitrate 16M
npx remotion still src/remotion/index.ts Thumbnail16x9 videos/{name}/thumbnail.png --public-dir videos/{name}/
```

---

## Workflow

### Progress Tracking

At Step 1 start, use your agent's task tracker (Claude Code `TaskCreate` / Codex todo list / equivalent) to create one task per step. Mark `in_progress` on start, `completed` on finish. Files in `videos/{name}/` (e.g. `podcast.txt`, `timing.json`, `output.mp4`) act as the durable record of what completed — if a session is interrupted, inspect the directory to determine where to resume.

```
 1. Define topic direction → topic_definition.md
 2. Research topic → topic_research.md
 3. Design video sections (5-7 chapters)
 4. Write narration script → podcast.txt
 4.5. Pronunciation pre-flight (zh-CN only) → videos/{name}/phonemes.json
 5. Collect media assets → media_manifest.json
 6. Generate publish info (Part 1) → publish_info.md
 7. Generate thumbnails (16:9 + 4:3) → thumbnail_*.png
 8. Generate TTS audio → podcast_audio.wav, timing.json
 9. Create Remotion composition + Studio preview (mandatory stop)
10. Render 4K video (only on user request) → output.mp4
11. Mix background music → video_with_bgm.mp4
12. Add subtitles (optional) → final_video.mp4
13. Complete publish info (Part 2) → chapter timestamps
14. Verify output & cleanup
15. Generate vertical shorts (optional) → shorts/
```

### Validation Checkpoints

**After Step 8 (TTS)**:
- [ ] `podcast_audio.wav` exists and plays correctly
- [ ] `timing.json` has all sections with correct timestamps
- [ ] `podcast_audio.srt` encoding is UTF-8

**After Step 10 (Render)**:
- [ ] `output.mp4` resolution is 3840x2160
- [ ] Audio-video sync verified
- [ ] No black frames

---

## Key Commands Reference

See **CLAUDE.md** for the full command reference (TTS, Remotion, FFmpeg, shorts generation).

---

## User Preference System

Skill learns and applies preferences automatically. See [references/troubleshooting.md](references/troubleshooting.md) for commands and learning details.

### Storage Files

| File | Purpose |
|------|---------|
| `user_prefs.json` | Learned preferences (auto-created from template) |
| `user_prefs.template.json` | Default values |
| `prefs_schema.json` | JSON schema definition |

### Priority

```
Final = merge(Root.tsx defaults < global < topic_patterns[type] < current instructions)
```

### User Commands

| Command | Effect |
|---------|--------|
| "show preferences" | Show current preferences |
| "reset preferences" | Reset to defaults |
| "save as X default" | Save to topic_patterns |

---

## Troubleshooting & Preferences

> **Full reference:** Read [references/troubleshooting.md](references/troubleshooting.md) on errors, preference questions, or BGM options.
