---
name: video-podcast-maker-nano
description: Smallest personal narrated-explainer-video pipeline (spoken narration over visuals, not an audio podcast), fully tool-agnostic and autonomous by default — topic → research ∥ asset collection → script → TTS → video → 4K render ∥ publish info + cover. The skill defines the pipeline logic and self-verified checkpoints; any TTS backend and any video tool (Remotion, HyperFrames, CapCut, ...) work, and how much human oversight to apply is set by the working project's AGENTS.md/CLAUDE.md, not here. Use when the user wants a quick personal narrated video with minimal steps, whether or not they name the tool stack. Do NOT trigger for audio-only podcasts, written episodic content, or heavy multi-format production.
argument-hint: "[topic] or videos/{name}/"
author: Agents365-ai
category: Content Creation
version: 1.0.0
---

# Video Podcast Maker Nano

A 7-step pipeline for personal use: **research ∥ materials → script → TTS → audio checkpoint → video → preview checkpoint → 4K render ∥ publish kit**. No bundled scripts, no hardcoded backends, no templates. The skill owns the *logic* and runs autonomously by default; the TTS backend and video tool are chosen per video (see [Tool selection](#tool-selection-per-video)).

What makes this work regardless of tool choice — the three invariants:

1. **Checkpoints are never skipped — but who checks is policy.** Three checkpoints exist: script (after Step 2), audio (after Step 3), preview (before render). Default checker is the agent itself (self-verification, defined per checkpoint); a project's AGENTS.md/CLAUDE.md may upgrade any checkpoint to a human gate — see [Oversight policy](#oversight-policy).
2. **Audio is the master clock.** The final video's duration must match the narration audio within ±0.5s (`ffprobe` both). Visuals are cut to the audio, never the reverse.
3. **A script change invalidates everything downstream.** Edit the script → re-run the script checkpoint, then TTS → audio checkpoint → visuals → preview checkpoint → render. Never hand-patch timings.

## Oversight policy

Default mode is **autonomous**: the pipeline runs end to end, with the agent performing every checkpoint's self-verification. A working project's AGENTS.md/CLAUDE.md can override per checkpoint with one line each:

- `Checkpoint 1 (script): human` — halt after Step 2 until the user approves the script. Worth it: a late script change costs a full re-run.
- `Checkpoint 2 (audio): human` — the user listens to the full audio before visuals. Worth it when TTS misreadings are costly to catch later.
- `Checkpoint 3 (preview): human` — the user reviews the draft before render. Worth it for style-sensitive channels.

Unmentioned checkpoints stay agent-verified. Project policy files start from `AGENTS.template.md` (next to this SKILL.md): copy it into the video project root as `AGENTS.md` (plus a `CLAUDE.md` copy for Claude Code) and fill in the tool bindings. The skill never uploads or publishes anything anywhere — the publish kit is files on disk; publishing is always a human act outside this pipeline.

## Tool selection (per video)

Decide the TTS backend and the video tool once, before Step 3, in this priority order:

1. **Project bindings win.** A filled `AGENTS.md`/`CLAUDE.md` in the working project (see Oversight policy) IS the user's standing specification — use it, no scanning, no second-guessing. If the user names a tool in-session, that overrides the file. If the policy file is missing or still contains template placeholders (`/absolute/path/to/...`), resolve the bindings via rules 2–3, then write the resolved values back into the project policy file so the next run starts bound.
2. **Auto-detect installed skills.** Scan the session's available skills for anything that can do the job — video: skills wrapping an authoring tool (Remotion, HyperFrames, CapCut, ...); TTS: any skill wrapping a TTS engine. **Exclude end-to-end pipeline skills** (e.g. other video-podcast-maker variants, if installed): they are pipelines like this one, not backends — invoking them here would nest workflows and double the checkpoints. One fit → use it; several → pick the best match for the project's language and output needs. Record the choice in `research.md`; surface it in the final summary. Never block waiting for a tool confirmation.
3. **Nothing found.** Fall back to plain CLIs the user already has (ffmpeg + any TTS CLI) and say so — never install a new tool unprompted. If a TTS CLI cannot emit subtitle timing, derive cues by splitting the script evenly across the audio duration and flag the approximation at Checkpoint 2. If a user-specified tool is missing or cannot meet the capability floor, say so and drop to rule 2 instead of improvising.

Capability floor (applies to rules 1–3): the TTS choice must produce narration audio plus subtitle timing; the video choice must export a draft video file (for Checkpoint 3 verification) and 4K. Live preview is a bonus, never a substitute for the draft export. Auxiliary jobs need no selection: research uses the built-in web search, stills/cover the video tool's still export or any image tool, duration checks `ffprobe`. If `ffmpeg`/`ffprobe` are absent, report it and stop — the ±0.5s invariant is non-negotiable and is not skipped to keep a run alive.

## Working layout

All artifacts for one video live in `videos/{name}/` (`{name}` = lowercase English, hyphen-separated). File names for audio/timing adapt to the chosen backend; the set is what matters:

```text
videos/{name}/
├── research.md          # Step 1 — facts + sources
├── podcast.txt          # Step 2 — narration script
├── podcast_audio.wav    # Step 3 — narration audio   (name per backend)
├── podcast_audio.srt    # Step 3 — subtitle timing  (or the backend's equivalent)
├── assets/              # Step 1 — images/BGM + sources.md (source + license per asset)
├── video-project/       # Step 5 — whatever the video tool produces
├── final_4k.mp4         # Step 7 — 3840×2160 render
├── cover.png            # Step 7 — video cover
└── publish_info.md      # Step 7 — title / description / tags / chapters
```

## Workflow

**Entry point check (before Step 1).** Look for `videos/{name}/` at the project root (or the directory the user names). If it already contains artifacts from an earlier session, this is an iteration — resume from the earliest step affected (see Iterating), do not re-run Step 1. Only start at Step 1 when no artifacts exist.

### Step 1 — Research ∥ collect materials

Two parallel outputs from one investigation pass (facts and assets come from the same sources):

**Research** → `research.md`. Investigate the topic (web search, papers, the user's pointers). Distill into `research.md`: facts, numbers, and their sources. Every number the script will claim must trace back here — a precise number without a source is fabricated; drop it or attribute it.

**Materials** → `assets/`. Collect everything the visuals and cover will consume into `videos/{name}/assets/`: per-section images/illustrations/screenshots, brand logos, BGM. Two sources, in priority order:

1. **User-provided** — files the user hands over or points at; copy into `assets/`, never reference them in place.
2. **Auto-collect** — official material first (product banner, spec card, screenshot), else free/licensed sets (unDraw SVG, Pixabay/Pexels, OpenMoji / Microsoft Fluent Emoji / Google Noto Emoji, `@lobehub/icons` for brand logos).

Record each asset's source URL + license in `assets/sources.md` at collection time (attribution-required sets must be credited in the video description at Step 7). No suitable asset exists for a section? Do not fabricate a screenshot — fall back to a text-only layout for that section (or a generic free-license illustration), record the decision in `assets/sources.md`, and move on; asking the user is optional in human mode. Missing assets can be added any time before Step 5.

### Step 2 — Script → `podcast.txt`, then **Checkpoint 1**

Spoken text only, no markdown. Split the script into segments with `[SECTION:xxx|display-label]` markers (lowercase English names, e.g. `[SECTION:hero|intro]`) — one section per video segment. This marker convention is the portable contract between script, TTS chunking, and visual layout; any TTS/video tool can consume it. Markers are structural metadata: never spoken, never shown as subtitle text — TTS and subtitles consume the text between markers only.

Style rules (language-agnostic): see [Script style](#script-style-language-agnostic).

**Checkpoint 1 — script self-review (mandatory).** Verify the script against every Script style rule, then reconcile its sections against `assets/`: list sections with no matching asset, collect or fall back per the no-asset rule above, and note what goes without. In human mode (project policy), halt instead and hand the script over — do NOT run TTS until the user explicitly approves. Audio, timings, and visual entrances all derive from the script; a late script change costs a full re-run.

### Step 3 — TTS

Run the chosen TTS backend (Azure, Edge, fish, minimax, ... — whatever the session picked). Produce:

- narration audio (WAV/MP3)
- subtitle timing (SRT or equivalent, cue text = script verbatim)

Pronunciation hygiene before synthesizing, in any narration language: brand/term readings that can't be derived mechanically (`Qwen` read as its Chinese brand name, `MoE` spelled letter-by-letter) go into an alias/phoneme list per the backend's mechanism — never into the script text (it would leak into subtitles).

### Step 4 — Audio check — **Checkpoint 2**

Agent self-verification (autonomous mode): `ffprobe` the audio duration against a rough estimate from the script (per-language speaking rate; use it only to catch gross errors like a silent or truncated file); verify every brand/term token in the script has an alias/phoneme entry (a coverage check — actual pronunciation is exactly what human-mode Checkpoint 2 is for); check for silent or clipped segments (`silencedetect`/`volumedetect`) that suggest synthesis failures. Fix alias-list gaps and re-synthesize if found. In human mode, the user listens to the full audio instead; misreadings → fix the alias list (not the script), re-synthesize, re-check.

### Step 5 — Make the video

Cut the visuals with the chosen tool (Remotion, HyperFrames, CapCut, ...) to the narration audio, using `assets/` as the material pool. Section markers from `podcast.txt` drive the layout; subtitle cues drive text entrances. Keep the draft files in `videos/{name}/`.

### Step 6 — Preview check — **Checkpoint 3**

Agent self-verification (autonomous mode): inspect the draft export (a seekable video file — the capability floor guarantees one): extract one frame per section (`ffmpeg -ss <mid-section-time> -i draft.mp4 -frames:v 1`) and view each for layout overflow, missing subtitles, broken asset references; verify draft duration matches the narration audio within ±0.5s. Fix and re-verify after every change. In human mode, the user reviews the draft in person (live preview if the tool has one, else the draft export); render only on explicit confirmation ("render"), and every round of changes needs fresh confirmation.

### Step 7 — Render 4K ∥ publish kit

Run in parallel (the render is the long blocking job; the publish kit doesn't depend on it):

- **Render** at 3840×2160 → `final_4k.mp4`. Verify duration vs narration audio within ±0.5s before calling it done.
- **Publish kit** → `publish_info.md` (title / description / tags / chapter timestamps — each chapter starts at the SRT time of its section's first cue) and `cover.png` (generate from the video tool's still frame if available, else any image tool; may reuse `assets/` material). The asset-sources section of `publish_info.md` copies from `assets/sources.md`.

## Script style (language-agnostic)

The narration language is whatever the user's script is — this pipeline defaults to Chinese but the rules below apply in any language's spoken register. These rules are enforced at Checkpoint 1; read each section aloud — if you stumble, split the sentence.

- **Everyday spoken prose, not written prose.** One idea per sentence, subject first, no nested clauses, no — or · as connectives. Vary sentence length; a light first person is fine.
- **Connector swap.** Replace bookish connectives (furthermore / however / therefore / in summary) with the everyday equivalent, or delete. Drop enumerative openers (firstly / secondly / lastly) and just move to the next point.
- **Kill list.** Delete formulaic filler: corporate buzzwords, "it is worth noting", "as everyone knows", "revolutionary", "game-changing", "seamless", "let's wait and see" — and their equivalents in the narration language.
- **Structural tells.** Verb-noun shells ("perform an optimization") → concrete action + result ("cut approval from three steps to one"). "Not X but Y" → state Y. Three-part parallelism ("both A and B and C") → keep only the most informative item; two are better than three. Vague intensifiers ("significantly") → a number or a perceivable consequence. Vague attribution ("experts say") → named source + date, else delete the sentence. Slogan endings ("the future is bright") → end on a concrete fact, number, or next action.
- **Numbers are Arabic digits** (`86.1`, `1.5G`, `9B`) — subtitles are the script verbatim, so write what should LOOK on screen. Never write the TTS spoken form into the script to fix a misreading; use the backend's alias/phoneme layer.
- **Numbers must be traceable** to `research.md` — a precise number without a source is fabricated; drop it or attribute it.

## Iterating

- Script changed → re-run Checkpoint 1 (human in human mode), then from Step 3 (TTS) through Checkpoints 2 and 3 to render. Never hand-edit timings.
- Audio re-synthesized (same script, different voice/rate) → re-run Checkpoint 2; visuals may stay if timings didn't shift; re-run Checkpoint 3 before rendering.
- Visuals only → edit and re-run Checkpoint 3.
- Reuse the same `videos/{name}/` directory.
