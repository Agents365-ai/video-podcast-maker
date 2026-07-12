# Hyperframes Overlays (type `overlay`)

**Load when**: a section needs a data-driven or bespoke animation that the
Remotion component library can't express well — animated charts with many
moving parts, animated infographics/maps, kinetic interludes, one-off
transitions — and `cli.py capabilities` reports `hyperframes` as usable.

[Hyperframes](https://github.com/heygen-com/hyperframes) (HeyGen, Apache-2.0)
renders HTML/CSS/GSAP to video via headless Chrome + FFmpeg. Here it is a
**sub-renderer producing transparent overlay assets** composited by Remotion —
it never replaces the main composition.

## Format contract (why WebM, not ProRes)

| Property | Required value |
|---|---|
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

## Workflow

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

## When NOT to use Hyperframes

- Simple counters, bars, card entrances — the Remotion component library
  already does these with zero extra tooling.
- Anything needing the narration-driven `useTiming()` beats *inside* the
  animation — Remotion components can read `timing.json`; a baked overlay
  cannot react to it beyond its start/duration.
- When Node < 22 or the render is flaky — degrade to Remotion-native.

## Troubleshooting

- **Overlay black in Studio** — the file is ProRes or alpha was lost
  (`pix_fmt` not `yuva420p`). Re-render as WebM VP9.
- **Overlay drifts against narration** — duration doesn't match the section
  window; recompute from `timing.json` and re-render (never stretch in
  Remotion).
- **Slow 4K render** — `transparent` extraction is per-frame PNG; keep
  overlays to the sections that need them.
