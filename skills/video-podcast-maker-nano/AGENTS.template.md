# Video Production — project policy

This file pins the tool choices and oversight level for this video project.
The pipeline logic (steps, checkpoints, invariants) lives in the
video-podcast-maker-nano skill — do NOT duplicate it here; only the values
below are project-specific. Fork this template and fill in your own values.

## Tool bindings

- TTS backend: Azure Speech (key/region in env `AZURE_SPEECH_KEY` / `AZURE_SPEECH_REGION`)
- Voice defaults: `zh-CN-XiaoxiaoNeural`, rate `-4%`
- Pronunciation: global dicts `~/.video-podcast-maker/aliases.json` + `phonemes.json`; per-video overrides in `videos/{name}/`
- Video tool: Remotion, project at `/absolute/path/to/remotion-project` (one project hosts all videos)
- Subtitle conventions: cues ≤ 30 chars, phrase-first packing, bottom-center above progress bar
- BGM: Pixabay (random pick), mix volume `0.08` + `loudnorm I=-16:TP=-1.5:LRA=11`
- Render: 3840x2160; final duration must match narration audio within ±0.5s

## Oversight policy

- Checkpoint 1 (script): agent
- Checkpoint 2 (audio): agent
- Checkpoint 3 (preview): agent

To require human review at any checkpoint, change `agent` to `human`.
Publishing is always done by a human; the pipeline only writes files.
