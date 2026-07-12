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
- [5b. Resolve](#5b-resolve) — user files, assetSeeker stock, generated (P2/P3)
- [5c. Validate & consume](#5c-validate--consume)
- [Hard rules](#hard-rules)

---

## 5a. Plan

For each `[SECTION:xxx]`, decide what assets (if any) improve it. Record the
plan directly as manifest entries.

| Role | Meaning | Typical type | Remotion component |
|------|---------|--------------|--------------------|
| `background` | Full-bleed section backdrop (scrim added for legibility) | image, video | `<AssetImage role="background">` / `<AssetVideo role="background">` |
| `inline` | Framed content media inside the layout | image, icon | `<AssetImage role="inline">` (delegates to `MediaSection`) |
| `broll` | Atmosphere clip | video | `<AssetVideo>` |
| `overlay` | Transparent animation layer (Hyperframes, P3) | overlay | `OverlayLayer` (P3) |
| `bgm` / `sfx` | Music / sound effects (Step 11) | audio | FFmpeg mix, not Remotion |

**Auto mode policy** (replaces the old "skip media" default):

1. Assets the user explicitly supplied or requested → always plan them.
2. Free sources (user files, assetSeeker stock, Iconify icons) → plan and
   resolve without asking. 2–4 well-placed assets beat wall-to-wall media;
   text-only sections remain perfectly valid.
3. Paid generation (imagenCN / videogenCN) → register as `planned` /
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
# JSON: data.usable = ["assetSeeker", ...]; per-component entry paths + hints
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

### Stock assets via assetSeeker (free, license-vetted)

If the assetSeeker skill is installed (look for its `scripts/seek_assets.py`
under the agent's skill directories, e.g. `~/.claude/skills/assetSeeker/`),
use it for photos / clips / icons; results carry license + attribution:

```bash
SEEK=~/.claude/skills/assetSeeker/scripts/seek_assets.py
python3 "$SEEK" sources --type photo            # which providers have keys
python3 "$SEEK" search photo "city skyline dusk" --orientation landscape --max 5
python3 "$SEEK" download "<download_url>" --output videos/{name}/assets/city.jpg
python3 ${SKILL_DIR}/scripts/cli.py assets add videos/{name}/ \
  --id city --section intro --type image --role background \
  --path assets/city.jpg \
  --license "<license from result>" --credit "<url from result>"
```

Notes: Iconify icons need no API key; Pexels allows 200 req/hr — batch your
searches. If assetSeeker is missing or has no keys, skip stock assets
silently.

### AI stills via imagenCN (paid — confirm before generating)

Use for scene illustrations and backgrounds that stock search can't provide
(specific concepts, consistent style, Chinese typography). Cost is low
(~0.02–0.22 RMB/image) but it is still paid generation — follow the gate:

1. Write the full detailed prompt yourself (subject, style, composition,
   colors matching `props.primaryColor`, "no text" unless text is wanted).
   Skip imagenCN's interactive 3-variant refinement — that is for standalone
   use.
2. Register the plan, present the cost sheet, wait for user confirmation:

```bash
python3 ${SKILL_DIR}/scripts/cli.py assets add videos/{name}/ \
  --id hero_art --section hero --type image --role background \
  --source imagen --prompt "<detailed prompt>" --cost-estimate "~0.2 RMB"
```

3. After the user confirms, generate and flip the entry to resolved:

```bash
IMAGEN=<entry path from capabilities>   # .../imagenCN/scripts/generate_image.py
python3 "$IMAGEN" "<detailed prompt>" videos/{name}/assets/hero_art.png --size 16:9
python3 ${SKILL_DIR}/scripts/cli.py assets add videos/{name}/ \
  --id hero_art --section hero --type image --role background \
  --source imagen --prompt "<detailed prompt>" --replace \
  --path assets/hero_art.png --license "AI-generated (<platform>/<model>)"
```

Default model (`qwen-image-2.0-pro`) renders 16:9 at 2688×1536 — fine for
`background`/`inline` roles (Remotion scales). Record the actual model from
the JSON envelope (`data.model`) in the license string.

### AI B-roll via videogenCN (most expensive — hard gate)

Per-second billing. The `--dry-run` quote is MANDATORY before asking:

```bash
VIDEOGEN=<entry path from capabilities>   # .../videogenCN/scripts/generate_video.py
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
- **i2v chain**: generate a keyframe with imagenCN first, then animate it —
  `python3 "$VIDEOGEN" "<动作描述>" out.mp4 --image videos/{name}/assets/hero_art.png`.
  Both default platforms share `DASHSCOPE_API_KEY`.
- Keep clips 5–15s and let narration length drive how many you need; B-roll
  is seasoning, not the meal.

### Hyperframes overlays (P3 — plan only for now)

Transparent animation overlays land in P3. You may still register the plan so
the manifest documents intent:

```bash
python3 ${SKILL_DIR}/scripts/cli.py assets add videos/{name}/ \
  --id growth_chart --section features --type overlay --role overlay \
  --source hyperframes --prompt "animated bar chart of star growth"
# status=planned — composition ignores it until resolved
```

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
