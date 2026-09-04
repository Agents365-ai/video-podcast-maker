---
name: video-podcast-maker-lite
description: Minimal personal narrated-video pipeline — a topic becomes a talking-head-free explainer MP4 (1080p or 4K) via script → Azure TTS (SSML) → Remotion. Use when the user wants a quick narrated video from a topic without the full video-podcast-maker machinery (no extra skills, no thumbnails/shorts/publish matrix). Do NOT trigger for heavy production needs — use video-podcast-maker for those.
argument-hint: "[topic]"
author: Agents365-ai
category: Content Creation
version: 1.1.0
---

# Video Podcast Maker Lite

A single-purpose pipeline for personal use: **topic → narration script → Azure TTS (SSML) → Remotion → 1080p/4K MP4**. No external skills, no config files, no bundled templates — the Remotion composition is generated once against the [contract below](#composition-contract), then reused across videos.

## Prerequisites

```bash
pip3 install azure-cognitiveservices-speech   # the only Python dependency
export AZURE_SPEECH_KEY="..."      # Azure Speech resource key
export AZURE_SPEECH_REGION="..."   # e.g. eastasia
# ffmpeg + node 18+ required; one Remotion project with npm install done
# Playwright MCP (session browser) needed only for Step 5 BGM fetching
```

## Project discovery (run before Step 1)

1. **Locate the Remotion project** — the directory containing both `src/remotion/index.ts` and `node_modules/remotion/`. Check the current working directory first; if it is not there, ask the user for the project path. Do NOT scan the filesystem, and do NOT create a new project if one exists elsewhere.
2. **Inventory existing videos** — `ls videos/` and `ls src/remotion/*Video.tsx`. The most recent `*Video.tsx` is the component to copy in Step 3; `videos/` shows which videos already exist.
3. **Existing `videos/{name}/`?** Then this is an iteration on that video, not a new one — reuse the directory and re-run only what changed (see [Iterating](#iterating)).
4. **No project anywhere** (first run only) → scaffold once in the working directory: `npm init -y && npm i remotion @remotion/cli @remotion/transitions react react-dom`, create `src/remotion/`, and warn the user about the one-time ~2 GB install. All later videos skip this.

## Workflow (6 steps)

Run all commands from the project root. All artifacts for one video live in `videos/{name}/` inside the project. `{name}` is lowercase English, hyphen-separated.

### Step 1 — Write the script: `videos/{name}/podcast.txt`

One `[SECTION:xxx]` marker per video segment; section names are lowercase English (`hero`, `content-1`, `outro`). An optional display title goes after a `|` — `[SECTION:outro|thanks]` — it labels the progress-bar pill and default layout (without it, the label derives from the first sentence, which can be awkward). Lines starting with `#` are ignored (and may safely mention markers). Spoken text only — no markdown — and follow the [script style rules](#script-style-anti-ai-flavor-zh-cn) below. Example:

```text
# comment lines are not spoken
[SECTION:hero|intro]
欢迎来到本期视频！今天我们要聊一个大家都关心的话题。

[SECTION:content-1|point 1]
首先，我们来看第一个要点。这里有几个关键信息需要你知道。

[SECTION:outro|thanks]
好了，今天的内容就到这里。如果觉得有帮助，欢迎点赞关注，我们下期再见！
```

### Script style (anti-AI-flavor, zh-CN)

Apply while writing, then self-check before TTS. Goal: everyday spoken Chinese, not written prose with commas. (Distilled from the full skill's `natural-narration.md` + `script-polish.md`.)

**Connector swap** (written → spoken): 此外→还有 · 然而→但是 · 因此→所以 · 与此同时→这时候 · 总的来说/综上所述→删掉 · 首先/其次/最后→直接讲下一件事。

**Kill list** (rewrite or delete): 赋能、打造、深入探讨、值得一提/值得注意的是、众所周知、至关重要、革命性、颠覆、天花板、无缝、闭环、抓手、里程碑、标志着、未来可期、让我们拭目以待。

**Structural tells** — the fix patterns:

| Pattern | Fix |
| ------ | ------ |
| Verb-noun shells: 进行优化/实现增长/做出选择 | concrete action + result: "把审批从三步改成一步" |
| Negation contrast: 不是 X,而是 Y | state Y directly |
| Three-part parallelism: 既是…又是…更是… | keep the most informative item; two beat three |
| Empty intensifiers: 显著/大幅/非常 | a number or a perceivable consequence |
| Vague attribution: 业内普遍认为/有专家指出 | named source + date, else delete the sentence |
| Slogan endings: 未来可期/注入新的活力 | land on a concrete fact: number, date, next action |

**Write for the ear**: one idea per sentence, subject first, vary sentence length, no nested clauses, no — or · as connectives (they don't get spoken and clutter subtitles). A light first person is fine ("我实测下来").

**Subtitles are the script, verbatim** — so write numbers the way they should LOOK on screen: Arabic digits (`3.8`, `63K`, `98.8%`, `128G`), never Chinese numerals (`六十五点一` / `三百九十七`). The same digit rule applies to on-screen text in the Remotion components (cards, headlines). Do NOT write the spoken form into the script to fix pronunciation — it leaks into subtitles. `tts.py` derives the spoken layer itself: every number-bearing token (`86.1`, `9B`, `5600`, `Qwen3.5`) is converted to its Chinese reading (`八十六点一`, `九B`, `五千六百`, `千问三点五`) before synthesis, then word boundaries are mapped back so subtitles keep the display text. (Multilingual voices like `zh-CN-XiaoxiaoMultilingualNeural` read bare digits in English in mixed context — that is exactly what this layer prevents. SSML `<sub alias>` was tried and abandoned: Azure's word-boundary events for `<sub>` are buggy and corrupt the SRT.)

**Numbers must be traceable** — a precise number without a source is fabricated; drop it or attribute it.

**Self-check before Step 2**: no kill-list words? no "不是…而是…"? no slogan ending? Read each section aloud — if you stumble, split the sentence.

**STOP — script review gate (mandatory)**: when `podcast.txt` is written, halt the pipeline and hand the script to the user for review. Do NOT run TTS (Step 2) until the user explicitly approves the script. This gate comes before everything else downstream — audio, timings, and visual entrances all derive from the script, so a late script change costs a full re-run.

### Step 2 — TTS

```bash
python3 "${SKILL_DIR}/scripts/tts.py" videos/{name}/podcast.txt videos/{name}/
```

Run `--check` first (lint-only, no synthesis, free) to catch polyphone and alias gaps before paying for synthesis.

Produces `podcast_audio.wav` + `podcast_audio.srt` + `timing.json` + `cues.json` (per-cue text, global frame, and `section_frame` — use it to align visual entrances in the component instead of hand-parsing the srt). Each section is synthesized separately via SSML and concatenated, so section timings are exact by construction. Subtitle cues are phrase-first: a sentence within 30 visible chars is shown whole; longer sentences are packed from comma/semicolon clauses (~22 per cue); an over-long clause is cut at the word boundary nearest its middle, never mid-word; tiny trailing cues merge into the previous one **within the same section only** (a short first sentence of the next section must never bleed into the previous section's last cue). Re-running over an existing `timing.json` prints a per-section duration diff; any section that moved >0.3s means the component's hardcoded entrance delays need re-aligning from the new `cues.json`.

Knobs: `--voice` (default `zh-CN-XiaoxiaoNeural`), `--style` (`mstts:express-as`, e.g. `gentle` / `cheerful` — stick to these two; others can sound strained), `--rate` (prosody, e.g. `-4%`), `--phonemes` (whole-word pinyin dict for polyphones like 命令行/同行; by default `~/.video-podcast-maker/phonemes.json` and `phonemes.json` next to the input are merged — per-video entries win), `--aliases` (pronunciation aliases display→spoken, e.g. `"Ornith-1.5": "Ornith 一点五"`; same merge order with `aliases.json`). Env fallbacks: `TTS_VOICE` / `TTS_STYLE` / `TTS_RATE`. For a consistent channel voice across videos, set them once in your shell profile (e.g. `TTS_VOICE=zh-CN-XiaoxiaoMultilingualNeural TTS_RATE=+5%`) instead of passing flags every time.

**Pronunciation**: polyphone pre-flight, known misreading shapes, alias-dict mechanics, and built-in spoken-layer behaviors are documented in [`references/pronunciation.md`](references/pronunciation.md) — read it before the first TTS run of a new topic.

### Step 3 — Compose visuals

- **First video ever**: generate the composition (`index.ts` + `Root.tsx` + `Video.tsx` under `src/remotion/`) against the [composition contract](#composition-contract).
- **Every later video**: copy the previous video's component and edit — never start from the contract again.

One Remotion project hosts all videos; a new video adds exactly one component file and one `<Composition>` registration:

```text
project-root/                    # ONE project, npm install once
├── src/remotion/
│   ├── index.ts                 # registerRoot — shared, never changes
│   ├── Root.tsx                 # one <Composition id="…"> per video
│   ├── DemoVideo.tsx            # per-video component (copy of the last one, edited)
│   └── NextTopicVideo.tsx
└── videos/{name}/               # per-video artifacts: podcast.txt, wav, srt, timing.json, mp4
```

Per video: pick a unique PascalCase component/composition id (e.g. `ReferenceManagerComparison`), set title / colors, and give each section name a layout (a `switch (section.name)` over `hero` / `content-N` / `outro` works well).

**Visual richness (default style — plain text-in-a-box is not the target look)**: every info card, flow box, pill and stat tile carries ONE leading emoji (or an `@lobehub/icons` brand component when it depicts a real product); at most one per element, and never inside a MONO value line (emoji break monospace alignment — put it on the label/title instead). Keep the mapping one concept = one emoji consistent across the whole video and pick it tastefully for the topic (dates/parameters/speed/cost each get an obvious match; the agent chooses). Every section also gets at least one visual anchor (an illustration): official material first (product banner, spec card, screenshot), else a free illustration or icon set (unDraw SVG, Pixabay/Pexels images, OpenMoji / Microsoft Fluent Emoji / Google Noto Emoji, `@lobehub/icons` for brand logos) — note the source + license in the publish_info asset-sources section (attribution-required sets like Flaticon's free tier must be credited in the video description). Emoji decorate the UI cards, illustrations anchor the section; neither replaces the other.

### Step 4 — Preview (mandatory human gate)

```bash
npx remotion studio src/remotion/index.ts --public-dir videos/{name}/
```

MUST launch Studio and wait for the user to review in person. NEVER render until the user explicitly confirms ("渲染" / "render"). An adjustment request is not confirmation — apply the change, let Studio hot-reload, and ask again. Every round of visual changes needs its own fresh confirmation; confirmation never carries over to Step 5.

### Step 5 — Render + BGM

Render:

```bash
npx remotion render src/remotion/index.ts MyVideo videos/{name}/output.mp4 --public-dir videos/{name}/
```

**BGM (default; skip only if the user says no music)**: fetch one **random track from Pixabay Music** and mix it at low volume (narration stays dominant). Pixabay License: royalty-free, commercial use OK, no attribution required — still log title/author into the publish_info asset-sources section.

How to fetch (verified 2026-08-25): Pixabay's search/list pages are client-rendered and Cloudflare-gated for non-browser clients, but a single-track page opened in a real browser embeds the full-track download URL in its JSON-LD, and that `cdn.pixabay.com` URL then downloads fine with plain curl.

1. With the session's browser (Playwright MCP), open a search page — `https://pixabay.com/music/search/cinematic/` (or `relaxing` / `ambient` if a calmer bed is wanted).
2. Collect result links matching `/music/<slug>-<id>/` (exclude `/music/search/` and locale-prefixed ones like `/de/music/...`), pick one at random, open it.
3. Read the track's JSON-LD (`script[type=application/ld+json"]` → the `AudioObject`): `contentUrl` (full track MP3), `name`, `creator.name`, `duration`. Prefer ~1.5–8 min; if out of range, open another link. If the page's JSON-LD has no `contentUrl` (layout changed), stop retrying — ask the user to pick a track and provide the download URL.
4. Download with curl (browser UA + `Referer: https://pixabay.com/` — verified to work):
   ```bash
   curl -sL -A "<browser UA>" -H "Referer: https://pixabay.com/" "<contentUrl>" -o videos/{name}/bgm.mp3
   ```

Mix (bgm low; the loudnorm stage is required — without it the mix lands ≈ -32 dB mean, ~10 dB too quiet):

```bash
ffmpeg -y -i videos/{name}/output.mp4 -i videos/{name}/bgm.mp3 -filter_complex "[1:a]volume=0.08[bg];[0:a][bg]amix=inputs=2:duration=first[a];[a]loudnorm=I=-16:TP=-1.5:LRA=11[out]" -map 0:v -map "[out]" -c:v copy -shortest videos/{name}/final_video.mp4
```

Stop the Studio server once the render is confirmed — a leftover Studio holds its port and keeps watching files.

### Step 6 — Delivery extras (only when the user's pipeline includes them)

Rendered after Step 5, in this order:

- **Cover stills**: 16x9 + 4x3 Thumbnail stills via `npx remotion still` — delete the old PNG first, stills skip existing files.
- **BGM loudness check**: `ffmpeg -i final_video.mp4 -af volumedetect -f null -`, mean ≈ -19 to -22 dB, max ≈ -1.5 dB.
- **`publish_info.md`**: title / description / tags / chapter timestamps (chapters derive from `timing.json`).
- **`assets/manifest.json`**: asset provenance.
- **Repo-level bookkeeping**: index/theme generators (e.g. a `VIDEO_INDEX.md` builder) typically key off `publish_info.md` titles, and classification scripts may refuse to run until the new video dir is added to their assignment map — run them after the publishing artifacts are in place.

## Composition contract

The composition consumes three files from `--public-dir videos/{name}/` via `staticFile()`: `podcast_audio.wav`, `podcast_audio.srt`, and `timing.json`:

```json
{
  "total_duration": 32.1,
  "fps": 30,
  "total_frames": 964,
  "sections": [{ "name": "hero", "label": "…", "start_time": 0, "duration": 11.8, "start_frame": 0, "duration_frames": 355 }]
}
```

Non-negotiables when generating a composition (each one is a real failure mode if missed):

1. **Audio is the master clock** — `calculateMetadata` returns `durationInFrames = timing.total_frames`, loaded at runtime. Never hardcode a duration. Resolution per project convention: 1920×1080 @ 30fps, or 4K (3840×2160) via a wrapper that scales a 1920×1080 design ×2 (keep the inner design at 1080p coordinates).
2. **Async assets gate rendering** — load `timing.json`/SRT with `fetch(staticFile(...))` wrapped in `delayRender`/`continueRender`, or the first frames render without data/subtitles. When copying an existing component that instead bundles `timing.json` via a direct `import`, that convention is equally valid (the JSON is inlined at bundle time) — follow the copied component.
3. **Compensate TransitionSeries overlap** — rendered length is `sum(sections) − (N−1)×transitionFrames`. Scale every section proportionally so the total lands exactly on `total_frames` (absorb rounding on the last section); do not pad the first section.
4. **Subtitles** — parse the SRT, show the cue active at the current frame, positioned bottom-center *above the progress bar* (bottom ≈ 70px). Body text ≥ 32px, titles ≥ 64px.
5. **Fail loud** — `cancelRender` with the real error if `timing.json` fails to load; a silent hang costs a render-timeout to diagnose.
6. **Props type must be a `type` alias, not an `interface`** — Remotion constrains props to `Record<string, unknown>`, which interfaces fail (no implicit index signature). `type VideoProps = { ... }` passes.
7. **Chapter progress bar** — pinned to the very bottom (height ~55px at 1080p): one pill per section with `flex` proportional to `duration_frames` and the section `label` as text (~24px); the active pill is filled with `primaryColor` and gets a translucent white overlay whose width is the intra-chapter progress, past pills gray, future pills outlined; plus a ~3px global progress line along the bottom edge. Section layouts keep the bottom ~200px clear in total (bar + subtitle zone).

## Iterating

- Script changed → re-run Step 2 (timestamps all shift — never hand-edit `timing.json`), then re-render.
- Audio re-synthesized (same script, different voice/rate) → re-run Step 2, then visuals may stay if timings didn't shift; re-enter the Step 4 gate before rendering.
- Visuals only → edit the video's component, re-render (audio untouched). This re-enters the Step 4 gate: fresh in-person confirmation required before rendering.
- Reuse the same `videos/{name}/` directory; never start a new project per video.

## Rules

1. **Studio before render.** Never render without a fresh, explicit in-person confirmation in the current Studio session (see Step 4).
2. After rendering, `output.mp4` duration must match `podcast_audio.wav` within ±0.5s (`ffprobe` both). If not, the composition contract (items 1/3) is violated — fix the composition, not the timing file.
3. **Always `--public-dir videos/{name}/`** on every Remotion command — it is how the composition finds `timing.json`, the WAV, and the SRT.
4. One Remotion project for all videos (see the layout in Step 3); only `videos/{name}/` and the per-video component change.

## Troubleshooting

- `Azure Speech SDK is not installed` → `pip3 install azure-cognitiveservices-speech`.
- `Set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION first` → export both env vars (see Prerequisites).
- TTS network/auth failure → the script retries once per section; persistent `CancellationReason.Error` usually means a bad key/region or an unsupported voice/style combo.
- `ffmpeg: command not found` → `brew install ffmpeg`.
- Video/audio duration mismatch > 0.5s → re-run Step 2; if it persists, the composition is violating contract item 1 or 3.
- `timing.json` not found in Studio/render → missing `--public-dir videos/{name}/`.