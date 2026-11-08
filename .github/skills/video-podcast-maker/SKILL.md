---
name: video-podcast-maker
description: Create or regenerate a topic-driven narrated explainer or video podcast using this repository's research, script, TTS, asset, Remotion, and 4K rendering workflow. Use for topic-to-video requests and revisions to videos made with this workflow. Do not use for generic video editing, trimming, conversion, or color grading.
---

# Video Podcast Maker

Use this repository's full workflow as the source of truth. Before starting or changing a video, read [`skills/video-podcast-maker/SKILL.md`](../../../skills/video-podcast-maker/SKILL.md) and load the relevant phase references linked there. Do not replace its pipeline with unsupported tools, backends, or assumptions.

## Workflow

- Locate and reuse the user's existing Remotion project; do not create a new project if one is available. If working from this repository root, run `python3 skills/video-podcast-maker/scripts/check_prereqs.py` before production work.
- For a new video, follow the canonical workflow from topic definition and research through script, asset planning, TTS, composition, preview, render, and output verification. Keep each video's files together in `videos/{name}/`.
- For an existing video, reuse its `videos/{name}/` directory and rerun only the stages invalidated by the requested change, as described in the canonical skill. Regenerate TTS timing after script changes; never hand-edit timing to compensate.
- Use only the TTS backends and production tools supported by the canonical workflow. Resolve prerequisites and configuration from its bootstrap instructions; report missing requirements rather than claiming they are installed.

## Render and delivery safeguards

- Preview the composition in Remotion Studio before a final render. Do not render the final video until the user explicitly confirms after reviewing the current version; each round of visual changes requires fresh confirmation.
- Keep generated video and related output in the per-video directory, using `--public-dir videos/{name}/` for Remotion commands.
- Run the repository's output verification script before declaring production complete. Do not upload or publish anything externally unless the user explicitly asks.
