# Visual Taste — Design Decision Framework

> **When to load:** Load alongside [design-guide.md](design-guide.md) at Step 9 (Remotion composition), *before* choosing colors, fonts, or layouts. design-guide.md owns the hard floors (px minimums, animation safety, checklists); this file owns the judgment calls above those floors. Where the two conflict, design-guide.md wins.

## Contents

- [The Three Dials](#the-three-dials) — VARIANCE / MOTION / DENSITY + per-topic presets
- [Anti-Default Discipline](#anti-default-discipline) — color, typography, cards, copy
- [Visual Mode Presets](#visual-mode-presets) — five aesthetic families
- [Section Rhythm Rules](#section-rhythm-rules) — whole-video composition shape
- [Pre-Render Taste Check](#pre-render-taste-check)

---

## The Three Dials

Before writing any section component, state one "design read" line: *"Reading this as: {topic type} for {platform audience}, {mode} — VARIANCE {n} / MOTION {n} / DENSITY {n}."* Every layout and animation decision below is gated by these three values (scale 1-10).

| Dial | 1-3 | 4-7 | 8-10 |
| ------ | ----- | ----- | ------ |
| **VARIANCE** — layout asymmetry | Everything centered and symmetric; equal grids | Mixed: left-aligned section titles over centered grids, `2fr 1fr` splits, reversed `SplitLayout` | Asymmetric grids, oversized offset numbers, deliberate large negative-space zones |
| **MOTION** — animation energy | `gentle` entrances, no continuous decor motion | `snappy` presets, staggered reveals, draw-on diagrams | `bouncy`/kinetic typography, char reveals, scale pops |
| **DENSITY** — info per section | `spacious`: one idea per screen, one big stat | `balanced`: 3-4 cards or points | `dense`: MetricsRow, timelines, comparison tables |

**Baseline: 6 / 5 / 4.** Use it only when the topic gives no signal.

- **VARIANCE** governs *where things sit*, not sizes — the design-guide minimums and ≥85% width rule always hold. Thumbnails ignore VARIANCE: always centered (design-guide hard rule).
- **MOTION** maps directly to the `animation_feel` pref (`gentle` ≈ 1-3, `snappy` ≈ 4-7, `bouncy` ≈ 8-10) and is **capped** by design-guide's Animation Safety table. Energy comes from type and element motion (char reveal, scale, draw-on), never from brightness flashes or background strobes.
- **DENSITY** maps to the `density` pref (`spacious`/`balanced`/`dense`). High density never buys smaller text — body stays ≥32px; if content doesn't fit, split the section.

### Topic presets (keys match `user_prefs.json` `topic_patterns`)

| Topic | VARIANCE | MOTION | DENSITY | Rationale |
| ------- | ---------- | -------- | --------- | ----------- |
| `tech` | 6 | 6 | 5 | Dark Tech mode fits; mono digits; diagram-friendly |
| `finance` | 4 | 4 | 6 | Data-forward: charts and metrics over decoration; restrained motion reads as trustworthy |
| `education` | 4 | 4 | 4 | Clarity over flair; step/sequence layouts carry the load |
| `lifestyle` | 7 | 6 | 3 | Image-led, airy, playful; few words per screen |
| `news` | 3 | 3 | 5 | Trust-first: symmetric, minimal motion, dense facts |

Override from user vibe words ("cool一点", "像 Apple 发布会", "轻松活泼") — but never silently fall back to baseline when the topic clearly matches a preset.

---

## Anti-Default Discipline

The LLM defaults that make videos look templated. Reach past them deliberately.

### Color

- **Max 1 accent color**, saturation <80% for backgrounds and cards. The single exception is the thumbnail, where design-guide *requires* high-saturation feed-pop colors.
- **Palette lock**: choose primary + accent + the 3-5 coding colors for parallel items **once, up front**, then reuse only those. Design-guide's "parallel cards use different theme colors" means *drawing from the locked set*, not inventing a new hue per section. A blue-accent video does not grow a teal stat card in section 5. No warm-gray/cool-gray mixing.
- **No AI-purple glow** as default. No automatic violet gradients or neon button glows. Neutral base (slate/zinc/stone family) + one high-contrast accent (emerald, electric blue, deep rose, burnt orange). Purple is fine only when the topic genuinely calls for it — then execute it with a consistent palette, not gradient slop.
- **Lifestyle/premium topics**: the warm beige + brass/clay + espresso "artisan" palette is banned as the default reach. Rotate real families instead: cold luxury (silver/chrome/smoke), forest (deep green + bone + amber), black + tan, cobalt + cream, terracotta + slate, or monochrome + one saturated pop.

### Typography

- **Two families max**: one display + one body. A mono third is allowed for numbers/code in tech and finance videos (`font-mono` digits at DENSITY ≥ 6).
- **Inter/system-default sans discouraged as display.** Prefer a distinctive grotesk. For zh-CN videos, prefer MiSans, HarmonyOS Sans, or Source Han Sans (思源黑体) over browser-default Noto rendering; weight contrast (800 titles / 500 body) does the hierarchy work.
- **Serif only when genuinely editorial** — history, literature, humanities, heritage topics. "Creative topic = serif" is the #1 AI tell; a modern sans display is the correct default for tech, business, lifestyle, and science. zh-CN editorial → Source Han Serif (思源宋体).
- **Emphasis inside a headline** = weight, italic, or accent color of the *same* family. Never inject a second family for one word.

### Cards & surfaces

- **Tint shadows to the card's own color** — design-guide's `rgba(color, 0.15)` pattern. Never pure-black shadows on a light theme.
- **One corner-radius system per video** (floor is 24px per design-guide). Pick a scale (e.g. cards 28px, pills full-round, badges 12px) and apply it everywhere — no sharp cards next to pill cards.
- **Card only when elevation means hierarchy.** A key stat or quote often lands harder in open layout (`StatHighlight`, `CenteredShowcase`) than inside yet another bordered box. At DENSITY ≥ 7, prefer hairline-separated rows over stacked card chrome.
- **Theme stays as design-guide defines it**: light theme keeps pure `#ffffff` section backgrounds (that rule wins over web-style "no pure white" advice); dark theme uses off-blacks like `#0f172a`, never `#000000`.

### On-screen copy

- No em-dash (—) as a visual flourish in on-screen text.
- No fake-precise numbers. Every on-screen stat traces to Step 2 research (`topic_research.md`) or it doesn't appear.
- No filler verbs in section titles ("赋能", "revolutionize", "unleash", "elevate") — concrete verbs only.
- No decorative micro-labels: version tags, `01 / 05` counters, fake status dots.

---

## Visual Mode Presets

Pick **one** mode per video from the design read (topic preset + user vibe words), declare it alongside the dials, and lock it for all sections. Record it as a `style_profiles` entry if the user wants reuse.

| Mode | Theme | Type direction | Preferred backgrounds | Dial tilt |
| ------ | ------- | ---------------- | ---------------------- | ----------- |
| **Minimalist / Clean** | light | neutral grotesk, tight tracking, weight-driven hierarchy | `clean`, faint gradient (≤0.05 opacity) | V5 M4 D3 |
| **Dark Tech** | dark | sans display + mono numerals, terminal motifs | `grid`, glow orb | V6 M6 D5 |
| **Editorial** | light | serif display + sans body, generous whitespace | accent lines, `clean` | V6 M4 D3 |
| **Playful / Agency** | either | bold rounded sans, oversized scale jumps | `shapes`, kinetic-typography preset | V8 M8 D3 |
| **Premium Consumer** | either | refined sans display, controlled spacing | subtle `gradient` | V7 M5 D3 |
| **Soft / Premium** | light | variable serif display (optical sizing, tight tracking) + soft grotesk body | `gradient` ≤0.04, diffuse glow orb | V6 M4 D2 |
| **Industrial Brutalist** | either | heavy sans structural headers at extreme scale contrast + mono telemetry rows | `grid` (lines/crosses), accent lines | V7 M5 D8 |

**Mode palettes** — the two new modes carry a locked palette as part of their identity; the Color rules above still apply on top.

- **Soft / Premium** — warm creams + espresso, editorial luxury. This is the one sanctioned use of the cream/espresso family: it is banned as an *unthinking* default reach, not as a declared mode. Cards use double-bezel / nested depth with ultra-soft diffuse shadows (large blur, low alpha, tinted per the Cards rules); massive whitespace and cinematic spatial rhythm carry the pacing.
- **Industrial Brutalist** — monochrome + a single hazard-red accent, visible hairline dividers instead of card chrome, raw mechanical precision in every transition. CRT scanlines / dithering / halftone are **static texture overlays only** (≤0.08 opacity, no flicker or scroll) — animated scanlines violate design-guide's Animation Safety table.

**Theme lock**: sections never flip light↔dark mid-video. Variety comes from tint shifts and background-layer changes *within* the theme family (design-guide theme rules), never from inverting a section.

---

## Section Rhythm Rules

Extends design-guide's Layout Sequencing Rules from "no consecutive repeats" to whole-video shape. Layout **families**: centered-showcase, split (SplitLayout/zigzag), card-grid, stat/metric, sequence (StepProgress/Timeline/FlowChart), media-led.

1. **Family repetition cap** — adjacent sections come from different families (design-guide rule), *and* no family appears more than twice in one video. A 7-section video uses ≥4 families.
2. **Zigzag cap** — max 2 consecutive split/alternating-card sections. Break the third with a full-bleed stat, centered showcase, or media-led section.
3. **Density wave** — follow every high-density section with a low-density one; never 3 dense sections in a row. The recommended arc stays *Hero → Impact → Detail → Breathe → repeat*.
4. **Eyebrow restraint** — the small uppercase kicker label above a section title: max 1 per 3 sections, hero counts as one. When cut, the title alone carries the section; its position in the video already categorizes it.
5. **Hero stack discipline** — max 4 text elements in the hero: (kicker OR logo mark), title (≤2 lines), subtitle (≤20 words / ~25 chars zh), and at most one meta strip. No feature bullets, no stat teasers — those get their own sections.
6. **Marquee/ticker max once** — a scrolling text band is a one-per-video device; a second one reads as filler.
7. **Background vocabulary lock** — consecutive sections use different background layers (design-guide), but the whole video draws from the same 1-2 layer vocabulary chosen by the mode. Don't introduce a sixth background style in section 6.

---

## Pre-Render Taste Check

Run after design-guide's Video-Level Checklist, before Studio review:

- [ ] Design read declared: mode + dials, matched to (or deliberately overriding) the topic preset?
- [ ] One accent + locked coding colors, used identically across all sections?
- [ ] ≤2 font families (+ optional mono); serif only with genuine editorial justification?
- [ ] One corner-radius system; shadows tinted, never pure black?
- [ ] No default AI-purple; no beige+brass default on a lifestyle topic?
- [ ] ≥4 layout families; no family >2×; ≤2 consecutive zigzag/split sections?
- [ ] Eyebrow count ≤ ceil(sections / 3); hero ≤4 text elements?
- [ ] Density alternates — no 3 dense sections in a row?
- [ ] All motion energy from type/element animation, inside design-guide's Animation Safety caps?
- [ ] Every on-screen number traceable to research; no em-dash flourishes or filler verbs?

If any box fails, fix the composition before rendering — these are cheaper to fix in Studio than after a 4K render.
