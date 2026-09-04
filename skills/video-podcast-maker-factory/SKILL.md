---
name: video-podcast-maker-factory
description: Use when the user wants to create their own custom narrated-video pipeline skill — a personal video-podcast-maker-xxx variant with their own TTS backend, visual style, and review gates. Forks the lite reference implementation. Do NOT trigger for making an actual video (use the user's existing variant) or for full production needs (use video-podcast-maker).
argument-hint: "[variant-name]"
author: Agents365-ai
category: Content Creation
version: 1.0.0
---

# Video Podcast Maker Factory

Create a personal `video-podcast-maker-xxx` skill by forking the reference implementation `skills/video-podcast-maker-lite/` (SKILL.md + scripts/tts.py, ~460 lines — read it first).

**Philosophy: fork and edit, never parameterize.** A personal pipeline stays simple because its choices are baked in, not configurable. If the user wants configurability or many features (thumbnails, shorts, publish matrix, multiple TTS backends), they are describing the full `video-podcast-maker` — point them there instead of building a heavy variant.

## Step 1 — Interview

Ask the user these axes; the lite defaults ship when the user has no preference:

| Axis | lite default |
| ------ | -------------- |
| Variant name | `video-podcast-maker-{xxx}` — lowercase suffix |
| TTS backend (must report word boundaries, or accept approximate SRT) | Azure Speech SSML |
| Voice / style / rate | `zh-CN-XiaoxiaoNeural` / `gentle` / none |
| Resolution & orientation | 1920×1080 @ 30fps horizontal |
| Visual furniture | chapter progress bar + SRT subtitle bar |
| Preview gate | mandatory in-person Studio confirmation before render |
| BGM | optional post-render ffmpeg mix |

## Step 2 — Fork

1. Copy `skills/video-podcast-maker-lite/` → `skills/video-podcast-maker-{xxx}/`.
2. Copy `tests/test_lite_tts.py` → `tests/test_{xxx}_tts.py` and fix the module path inside it.
3. Frontmatter: set `name: video-podcast-maker-{xxx}` and rewrite `description` so hosts trigger the right variant — mention what makes this one different (backend, style, owner).

## Step 3 — Apply the interview deltas

- **Different TTS backend** → replace ONLY `synthesize_section()` in `tts.py`. Keep `parse_sections` / `merge_boundaries` / `build_cues` / `build_timing` and the CLI shape untouched — they are backend-agnostic and tested. The replacement must honor the boundary contract: word-boundary events with 100ns-tick offsets + a 48 kHz mono WAV part file. Backend without word boundaries? Estimate per-character over the measured part duration, and document that SRT timing becomes approximate.
- **Different visuals** → edit the numbered items in the SKILL.md "Composition contract" (progress bar, subtitle position, sizes, colors). Items 1-3 (master clock, delayRender gating, transition-overlap compensation) and 5-6 (fail loud, props `type` alias) are load-bearing — do not soften them.
- **Different review gate** → Step 4 and Rules.
- **Different script format** (e.g. drop `|label`) → `parse_sections()` plus its tests.

## Step 4 — Invariants (never change)

1. The three-file contract: `podcast_audio.wav` + `podcast_audio.srt` + `timing.json`, consumed via `--public-dir videos/{name}/`.
2. Per-section synthesis + ffmpeg concat — that is what makes section timings exact.
3. Audio is the master clock: composition length = `timing.total_frames`; post-render duration check within ±0.5s.
4. Pure functions stay separated from IO in `tts.py` — that is what keeps it testable without network.
5. SKILL.md stays a single file. If any section grows past ~30 lines, the variant is drifting toward the full skill — stop and reconsider.

## Where preferences live (never in the variant)

Taste that emerges during use — default voice, BGM file, project path, publish platform — goes into the Remotion project's `AGENTS.md` (or host memory) as plain factual lines the agent reads every session. When the user says "from now on use voice X", append a line there. Never rebuild a `user_prefs.json`-style settings system inside a variant: a preference file the agent reads natively needs zero code. Keep it to taste, though — load-bearing correctness (the invariants above) stays in the skill, because preference files are soft constraints.

## Step 5 — Validation (mandatory before declaring done)

1. `pytest -q` green, including the variant's own test file.
2. E2E TTS on a 3-section demo script: WAV plays, SRT is UTF-8, `timing.json` has zero drift vs the WAV (`ffprobe` both).
3. One real Remotion render at the variant's resolution; output duration matches audio within ±0.5s.
4. Extract 2-3 frames with ffmpeg and actually look at them (layout, subtitle, progress bar).
5. Add the variant to the repo-root `AGENTS.md` structure paragraph.
