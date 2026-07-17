# Video Podcast Maker — AGENTS.md

> Cross-agent portability layer. Read natively by Codex, Copilot, Cursor, Windsurf, Aider, Zed, Amp, JetBrains Junie, and others. Claude Code reads this too alongside `SKILL.md`.

This is a coding-agent skill for automated video podcast creation via Remotion. The primary instruction file is [`SKILL.md`](SKILL.md).

## Quick Start

1. Read [`SKILL.md`](SKILL.md) for the full workflow
2. Run the bootstrap check: `python3 scripts/check_prereqs.py`
3. The 15-step pipeline produces 4K MP4 from a topic: research → script → TTS → Remotion → render → BGM

## Directory Layout

```
SKILL.md            — Primary agent instructions (Claude Code / OpenClaw native format)
AGENTS.md           — This file (cross-agent standard)
references/         — Load-on-demand phase files (workflow-*.md, design-guide.md, etc.)
scripts/            — Python automation (TTS, verification, assets, etc.)
templates/          — Remotion starter files (Video.tsx, components, presets)
assets/             — BGM tracks, outro animations
```

## Key Commands

```bash
python3 scripts/cli.py --help              # Discover all scripts
python3 scripts/check_prereqs.py           # Validate environment
python3 scripts/generate_tts.py --input podcast.txt --output-dir videos/{name}/
python3 scripts/verify_output.py videos/{name}/
```

## Dependencies

- Node 18+, Python 3.8+, FFmpeg
- Remotion (`npm install` in project root)
- ttsCN component skill (required for TTS)
- remotion-best-practices skill (required for Remotion guidance)
