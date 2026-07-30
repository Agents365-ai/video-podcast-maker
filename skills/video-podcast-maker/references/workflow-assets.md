# Step 5: Asset Plan & Resolve

**Load when**: entering Step 5, or whenever the user supplies images/clips
("use this screenshot", "@xx.png"), asks for stock footage/BGM, or wants
richer visuals than text animations.

The asset layer sits between the script phase and the Remotion composition.
Its single source of truth is the per-video manifest:

```
videos/{name}/assets/manifest.json     # created by: cli.py assets init
videos/{name}/assets/*.png|mp4|mov|…   # the asset files themselves
```

Every asset is registered with `scripts/assets.py` (or `cli.py assets …`) and
consumed in Remotion through `useAssets()` / `<AssetImage>` / `<AssetVideo>`
(the manifest is served via `--public-dir videos/{name}/`).

## Contents

- [5a. Plan](#5a-plan) — decide role + source per section
- [5b. Resolve](#5b-resolve) — user files, assetseeker stock, generated (P2/P3)
- [5c. Validate & consume](#5c-validate--consume)
- [Hard rules](#hard-rules)

---

## 5a. Plan

For each `[SECTION:xxx]`, decide what assets (if any) improve it. Record the
plan directly as manifest entries.

| Role | Meaning | Typical type | Remotion component |
| ------ | --------- | -------------- | -------------------- |
| `background` | Full-bleed section backdrop (scrim added for legibility) | image, video | `<AssetImage role="background">` / `<AssetVideo role="background">` |
| `inline` | Framed content media inside the layout | image, icon | `<AssetImage role="inline">` (delegates to `MediaSection`) |
| `broll` | Atmosphere clip | video | `<AssetVideo>` |
| `overlay` | Transparent animation layer (Hyperframes, P3) | overlay | `OverlayLayer` (P3) |
| `bgm` / `sfx` | Music / sound effects (Step 11) | audio | FFmpeg mix, not Remotion |

**Auto mode policy** (replaces the old "skip media" default):

1. Assets the user explicitly supplied or requested → always plan them.
2. Free sources (user files, assetseeker stock, Iconify icons) → plan and
   resolve without asking. 2–4 well-placed assets beat wall-to-wall media;
   text-only sections remain perfectly valid.
3. Paid generation (imagencn / videogencn) → register as `planned` /
   `pending_confirmation` with a `--cost-estimate`; present the cost sheet and
   generate **only after the user confirms** (P2).
4. No component skill installed, no user files → proceed text-only. The
   pipeline must never fail because the asset layer is empty.

**Interactive mode**: ask per-section (skip / user file / stock search /
AI generation), then register the answers the same way.

## 5b. Resolve

Before resolving, probe which producers are actually available:

```bash
python3 ${SKILL_DIR}/scripts/cli.py capabilities
# JSON: data.usable = ["assetseeker", ...]; per-component entry paths + hints
```

Components are discovered via `<NAME>_HOME` env vars, `VPM_COMPONENT_ROOTS`
(colon-separated parent dirs), then `~/.claude/skills/<name>`. Use the
reported `entry` path for every invocation below. A component that is missing
or lacks keys is simply skipped — tell the user what installing it would
unlock, don't fail.

### User-supplied files (the `@xx.png` flow)

When the user references a local file for a scene, copy + register it in one
command — never leave it unregistered:

```bash
python3 ${SKILL_DIR}/scripts/cli.py assets init videos/{name}/
python3 ${SKILL_DIR}/scripts/cli.py assets add videos/{name}/ \
  --id hero_bg --section hero --type image --role background \
  --file /path/the/user/gave/screenshot.png
# → copies to videos/{name}/assets/hero_bg.png, status=resolved, license=user-owned
```

Choose the role deliberately: a screenshot the narration talks about is
`inline`; a mood photo behind a title is `background`.

### Stock assets via assetseeker (free, license-vetted)

If the assetseeker skill is installed (look for its `scripts/seek_assets.py`
under the agent's skill directories, e.g. `~/.claude/skills/assetseeker/`),
use it for photos / clips / icons; results carry license + attribution:

```bash
SEEK=~/.claude/skills/assetseeker/scripts/seek_assets.py
python3 "$SEEK" sources --type photo            # which providers have keys
python3 "$SEEK" search photo "city skyline dusk" --orientation landscape --max 5
python3 "$SEEK" download "<download_url>" --output videos/{name}/assets/city.jpg
python3 ${SKILL_DIR}/scripts/cli.py assets add videos/{name}/ \
  --id city --section intro --type image --role background \
  --path assets/city.jpg \
  --license "<license from result>" --credit "<url from result>"
```

Notes: Iconify icons need no API key; Pexels allows 200 req/hr — batch your
searches. If assetseeker is missing or has no keys, skip stock assets
silently.

### AI stills via imagencn (paid — confirm before generating)

Use for scene illustrations and backgrounds that stock search can't provide
(specific concepts, consistent style, Chinese typography). Cost is low
(~0.02–0.22 RMB/image) but it is still paid generation — follow the gate:

1. Write the full detailed prompt yourself (subject, style, composition,
   colors matching `props.primaryColor`, "no text" unless text is wanted).
   Skip imagencn's interactive 3-variant refinement — that is for standalone
   use.
2. Register the plan, present the cost sheet, wait for user confirmation:

```bash
python3 ${SKILL_DIR}/scripts/cli.py assets add videos/{name}/ \
  --id hero_art --section hero --type image --role background \
  --source imagen --prompt "<detailed prompt>" --cost-estimate "~0.2 RMB"
```

1. After the user confirms, generate and flip the entry to resolved:

```bash
IMAGEN=<entry path from capabilities>   # .../imagencn/scripts/generate_image.py
python3 "$IMAGEN" "<detailed prompt>" videos/{name}/assets/hero_art.png --size 16:9
python3 ${SKILL_DIR}/scripts/cli.py assets add videos/{name}/ \
  --id hero_art --section hero --type image --role background \
  --source imagen --prompt "<detailed prompt>" --replace \
  --path assets/hero_art.png --license "AI-generated (<platform>/<model>)"
```

Default model (`qwen-image-2.0-pro`) renders 16:9 at 2688×1536 — fine for
`background`/`inline` roles (Remotion scales). Record the actual model from
the JSON envelope (`data.model`) in the license string.

### AI B-roll via videogencn (most expensive — hard gate)

Per-second billing. The `--dry-run` quote is MANDATORY before asking:

```bash
VIDEOGEN=<entry path from capabilities>   # .../videogencn/scripts/generate_video.py
python3 "$VIDEOGEN" "<中文提示词>" videos/{name}/assets/city_broll.mp4 \
  -d 5 -r 1080P --ratio 16:9 --dry-run          # prints request + cost estimate
python3 ${SKILL_DIR}/scripts/cli.py assets add videos/{name}/ \
  --id city_broll --section intro --type video --role broll \
  --source videogen --prompt "<提示词>" --cost-estimate "<from dry-run>"
```

Only after explicit user confirmation, drop `--dry-run` and run the real
generation (it blocks through submit → poll → download; result URLs expire in
24h so never defer the download). Then re-register with `--replace --path
assets/city_broll.mp4 --duration-s <n> --license "AI-generated (<model>)"`.

- Prompts are Chinese; pass detailed prompts (>80 chars) to skip the
  component's interactive refinement.
- If the process is interrupted mid-task, resume with
  `--task-id <id> videos/{name}/assets/x.mp4` instead of paying again.
- **i2v chain**: generate a keyframe with imagencn first, then animate it —
  `python3 "$VIDEOGEN" "<动作描述>" out.mp4 --image videos/{name}/assets/hero_art.png`.
  Both default platforms share `DASHSCOPE_API_KEY`.
- Keep clips 5–15s and let narration length drive how many you need; B-roll
  is seasoning, not the meal.

### Transparent overlays via Hyperframes (free, needs Node 22+)

[Hyperframes](https://github.com/heygen-com/hyperframes) (HeyGen, Apache-2.0)
renders HTML/CSS/GSAP to video via headless Chrome + FFmpeg. Here it is a
**sub-renderer producing transparent overlay assets** composited by Remotion —
it never replaces the main composition.

**Format contract (why WebM, not ProRes):**

| Property | Required value |
| --- | --- |
| Container/codec | **WebM VP9 with alpha** (`yuva420p`) |
| Resolution | 3840×2160 (full-frame 4K, transparent where empty) |
| Frame rate | **30 fps** (must match the composition) |
| Duration | Exactly the target section window from `timing.json` |

WebM VP9 is the primary format because Remotion Studio previews
`<OffthreadVideo>` as a browser `<video>` element — Chrome plays WebM alpha
natively but **cannot decode ProRes**, so a ProRes overlay would look broken
at the mandatory Step 9 review even though it renders correctly. During the
real render, the `transparent` prop extracts alpha frames via FFmpeg.
Export ProRes 4444 additionally only if the user wants the overlay for
external editing software. PNG sequence is the lossless fallback.

`verify_output.py` enforces this contract (alpha pix_fmt + 30 fps = errors;
duration/resolution deviations = warnings).

**Workflow:**

1. **Preflight** — `cli.py capabilities` must show `hyperframes.usable: true`
   (Node 22+). If not, fall back to Remotion-native animation components
   (`DataBar`, `StatCounter`, `FlowChart`, `DiagramReveal`); never block the
   pipeline on Hyperframes.
2. **Compute the window** — the overlay covers one section (or a sub-range):
   `duration_s = section.end_time - section.start_time` from `timing.json`.
   At 30 fps that is `duration_frames = round(duration_s * 30)`.
3. **Author** — scaffold with `npx hyperframes init`, then write the
   composition. Rules that make renders frame-accurate:
   - The project is plain HTML (`index.html`); size the root to 3840×2160
     with `data-width` / `data-height`, keep the page background transparent
     (no `body` background color).
   - Clips carry `data-start` / `data-duration` (in seconds) — total must
     equal the window from step 2.
   - GSAP timelines must be **paused and seekable**:
     `gsap.timeline({ paused: true })` registered on `window.__timelines`;
     never drive animation from raw `requestAnimationFrame` or wall-clock
     time (that de-syncs frame extraction).
   - Respect the video's design language: pull colors from the composition
     props (`primaryColor` etc.) and the visual minimums in
     [design-guide.md](design-guide.md).
4. **Preview & render** —

   ```bash
   npx hyperframes preview                       # browser hot-reload
   npx hyperframes render --output growth_chart.webm   # format from extension
   ```

   Check `npx hyperframes render --help` for the current flag set (the tool
   is young and its CLI moves fast); confirm the output probe shows
   `yuva420p` and 30 fps before registering.
5. **Register** —

   ```bash
   mv growth_chart.webm videos/{name}/assets/
   python3 ${SKILL_DIR}/scripts/cli.py assets add videos/{name}/ \
     --id growth_chart --section features --type overlay --role overlay \
     --source hyperframes --path assets/growth_chart.webm \
     --alpha --fps 30 --duration-s <window> \
     --license "self-rendered (Hyperframes)"
   ```

6. **Composite** — inside the section's `Sequence` in the per-video
   composition:

   ```tsx
   import { OverlayLayer } from "./components";
   <OverlayLayer id="growth_chart" />
   ```

   The layer is absolute-fill, muted, `pointer-events: none`, and renders
   nothing while the asset is unresolved.

**When NOT to use Hyperframes:**

- Simple counters, bars, card entrances — the Remotion component library
  already does these with zero extra tooling.
- Anything needing the narration-driven `useTiming()` beats *inside* the
  animation — Remotion components can read `timing.json`; a baked overlay
  cannot react to it beyond its start/duration.
- When Node < 22 or the render is flaky — degrade to Remotion-native.

**Troubleshooting:**

- **Overlay black in Studio** — the file is ProRes or alpha was lost
  (`pix_fmt` not `yuva420p`). Re-render as WebM VP9.
- **Overlay drifts against narration** — duration doesn't match the section
  window; recompute from `timing.json` and re-render (never stretch in
  Remotion).
- **Slow 4K render** — `transparent` extraction is per-frame PNG; keep
  overlays to the sections that need them.

If `capabilities` reports Hyperframes unusable, fall back to Remotion-native
animation components.

## 5c. Validate & consume

```bash
python3 ${SKILL_DIR}/scripts/cli.py assets validate videos/{name}/
```

Errors (bad schema, missing files, path escapes) must be fixed before Step 9;
license warnings should be resolved before publishing. `verify_output.py`
(Step 14) re-runs this check.

In the per-video composition:

```tsx
import { AssetImage, AssetVideo, useAssets, getSectionAssets } from "./components";

// Fixed usage — you know the id you registered:
<AssetImage props={props} id="hero_bg" role="background" />
<AssetImage props={props} id="app_shot" role="inline" caption="App overview" />
<AssetVideo props={props} id="city_broll" role="background" />

// Data-driven usage — render whatever the manifest has for a section:
const inline = getSectionAssets(useAssets(), "features", "inline");
```

Both components render `null` for missing/unresolved ids, so compositions are
safe to write before all assets land. Design rules (content width, safe
zones, text-over-image contrast) in [design-guide.md](design-guide.md) still
apply — `background` role adds a scrim automatically; keep `dim` ≥ 0.3 when
text sits on top.

## Hard rules

1. **Manifest or it doesn't exist** — every file used by the composition is
   registered; nothing is referenced ad-hoc from outside `videos/{name}/`.
2. **License is part of the asset** — stock results must carry their license
   string and credit URL into the manifest; `user-owned` covers user files.
3. **No silent spending** — paid generation never runs without a cost
   estimate surfaced and explicit user confirmation.
4. **Graceful degradation** — zero installed producers still yields a valid
   text-only video.
