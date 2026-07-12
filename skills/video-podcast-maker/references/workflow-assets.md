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

### Generated assets (registered now, produced in later phases)

imagenCN stills, videogenCN clips, and Hyperframes overlays are P2/P3
producers. Until those phases land, you may still register the *plan* so the
manifest documents intent:

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
