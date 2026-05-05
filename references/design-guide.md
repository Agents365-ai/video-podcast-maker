# Video Podcast Maker — Design Guide

> **When to load:** Load this file when working on Step 9 (Remotion composition) or when the user asks about visual design.

## Contents

- [Visual Design Minimums (MUST follow)](#visual-design-minimums-must-follow) — text sizes, spacing, space utilization, visual richness
- [Design Philosophy](#design-philosophy)
- [Animation Safety (MUST follow)](#animation-safety-must-follow)
- [Quality Checklists (MUST follow)](#quality-checklists-must-follow)
- [Visual Design Reference (recommended)](#visual-design-reference-recommended)
- [Animated Backgrounds (SHOULD use)](#animated-backgrounds-should-use)
- [Section Layout Presets (SHOULD use)](#section-layout-presets-should-use)
- [Animation Best Practices (SHOULD follow)](#animation-best-practices-should-follow)

---

## Visual Design Minimums (MUST follow)

Hard constraints for 1080p design space — prevents small text and empty layouts:

| Constraint | Minimum |
|------------|---------|
| **Any text** | ≥ 24px |
| **Hero title** | ≥ 84px |
| **Section title** | ≥ 72px |
| **Card title** | ≥ 40px |
| **Card / body text** | ≥ 32px |
| **Icon size** | ≥ 56px |
| **Section padding** | ≥ 40px |
| **Card padding** | ≥ 40px 48px |
| **Card border-radius** | ≥ 24px |
| **Grid gap** | ≥ 28px |

### Space Utilization

| Rule | Requirement |
|------|-------------|
| **Content width** | Cards/grids must occupy ≥85% available width (maxWidth: 1500-1700px) |
| **Vertical centering** | All sections must use `justifyContent: 'center'` |
| **Grid vs Flex** | Prefer `grid` over `flex wrap` for multi-card layouts |
| **Card fill** | Cards should fill available space, no large blank areas |

### Visual Richness

| Element | Requirement |
|---------|-------------|
| **Card borders** | Colored border (≥3px) or colored left border (≥6px) |
| **Shadows** | `boxShadow: '0 8px 24px rgba(color, 0.15)'` |
| **Color coding** | Parallel elements use different theme colors |
| **Gradients** | Prefer gradient over solid color for card backgrounds |
| **Icons** | Each card/point needs an icon, size ≥56px |

---

## Design Philosophy

Templates (`templates/`) are **starting points, not blueprints**. The agent SHOULD customize visual design per video topic:

- **Color palette**: match the subject (tech → cool blues/grays, food → warm tones, finance → dark/gold)
- **Section layouts**: create new component arrangements, don't repeat the same layout
- **Visual variety**: vary backgrounds, card styles, emphasis techniques across sections
- **Typography**: adjust sizes and weights for clear visual hierarchy per content density
- **Animations**: use entrance animations and transitions that fit the video's energy

**Keep consistent**: Technical Rules (4K, safe zones, min sizes), component imports, `timing.json`-driven timing.

**Vary freely**: colors, gradients, backgrounds, layout composition, card styles, icon choices, spacing, animation timing, section visual identity.

### Theme-based background rules

When `user_prefs.visual.theme` is `"light"`:
- **All section backgrounds MUST be white (`#ffffff`)**. Do NOT use dark backgrounds, colored backgrounds, or alternate grays.
- Use subtle radial/linear gradients over white (`${color}06`-`${color}10`) for visual variety between sections.
- All text must use dark colors (`#1a1a1a` or theme colors). Never use white/light text.
- Tech cards, stat cards, etc. should use tinted backgrounds (`${color}08`) instead of dark card backgrounds.

When `user_prefs.visual.theme` is `"dark"`:
- Section backgrounds use dark colors (`#0f172a`, `#1a1a2e`, etc.)
- Text uses white/light colors.

---

## Animation Safety (MUST follow)

Hard limits to prevent strobing, flicker, and visual fatigue. These apply to every composition regardless of style.

| Rule | Requirement |
|------|-------------|
| **Full-screen brightness change** | `opacity` of any full-bleed white/black overlay must NOT exceed `0.30` |
| **Snap duration** | No light↔dark snap may complete in fewer than `10` frames (~0.33s @ 30fps) |
| **Section transition flash** | Forbidden by default. Use color pulse (≤0.15 opacity) or simple cut instead. |
| **Per-beat reveal flash** | If used (e.g. "kinetic flash" effect), peak opacity ≤ `0.15` and decay ≥ `12` frames |
| **Strobe-frequency animation** | Forbidden. Any flicker faster than 3Hz risks accessibility issues (photosensitive viewers) |
| **Background pulse** | Color/glow pulses on background layers ≤ `0.15` opacity, period ≥ `2s` |
| **Text colour inversion** | Don't invert text colour on a flash beat — it disappears against the dark BG once flash decays |

**Why**: full-screen flashes (even at 0.85 opacity for 6 frames) feel like camera-flash strobes when watched repeatedly during edit/preview. Most kinetic-typography references use *type motion* for punch, not background strobes. The visual energy should come from character pop / marker reveal / scale animations, not from the canvas blinking.

## Quality Checklists (MUST follow)

### Per-Section Checklist

| # | Check | Requirement |
|---|-------|-------------|
| 1 | **Space utilization** | Content ≥85% available width, no large blank areas |
| 2 | **Visual depth** | Shadow + colored border/gradient, at least 2 visual layers |
| 3 | **Color coding** | Parallel cards use different theme colors (border, title, icon) |
| 4 | **Typography scale** | Title ≥72px, card title ≥40px, body ≥32px, icon ≥56px |
| 5 | **Complete animation** | All elements have entrance animation, list items have stagger delay |
| 6 | **Vertical centering** | Use `justifyContent: 'center'` |

### Video-Level Checklist (before render)

| # | Check | Requirement |
|---|-------|-------------|
| 1 | **Layout variety** | ≥3 different layout types (centered, grid, split, timeline, etc.) |
| 2 | **Background alternation** | No 2 consecutive sections share the same background |
| 3 | **Unified color scheme** | Primary/secondary/accent used consistently |
| 4 | **Thumbnail readability** | Title ≥120px, centered, legible at ~300px thumbnail width |
| 5 | **Hero impact** | Large text + decorative elements or gradient |

### Remotion Thumbnail Design

Thumbnails render at ~300px in feeds. Only bold, oversized elements survive at that scale.

**Hard rules (MUST follow):**

| Rule | Requirement |
|------|-------------|
| **Layout** | Content centered both horizontally and vertically |
| **Title** | ≥120px bold. The dominant visual element — as large as the text length allows |
| **Icons** | ≥120px. Serve as visual anchors alongside text |
| **Coverage** | Text + icons should fill most of the canvas. Minimize empty space. |
| **Readability** | Must be legible at 300px width — use text-stroke, text-shadow, or contrasting overlay as needed |

**Design guidance (adapt per topic):**
- Prefer 2-3 lines of text (title + subtitle or hook) over a single line — more text = more information density
- Use high-saturation colors that pop in feeds; avoid muted tones
- Consider a short hook phrase ("Why It Matters", "Top 5") to boost curiosity — as badge, subtitle, or integrated into the title
- Background should support the text, not compete with it (gradient, blurred image, solid color all work)
- When in doubt, scale text and icons up rather than down

### TTS Quality Guidance

| Technique | How |
|-----------|-----|
| **Section pauses** | Empty line before each `[SECTION:xxx]` for natural breathing room |
| **Pacing variation** | Slower intro/outro (TTS_RATE="+0%"), normal middle (TTS_RATE="+5%") |
| **Key sentence emphasis** | SSML `<emphasis>` tags on important sentences (Azure supports this) |

---

## Visual Design Reference (recommended)

Production-verified sizes as recommended reference. The agent may adjust freely but MUST NOT go below Minimums.

### Typography Scale (1080p design space)

| Element | Recommended Size | Weight | When to Use |
|---------|-----------------|--------|-------------|
| **Hero Title** | 84-96px | 800 | Opening section, brand moment |
| **Section Title** | 72-80px | 700-800 | Each section's main heading |
| **Large Emphasis** | 48-72px | 600-700 | Key statements, conclusions, quotes |
| **Subtitle / Description** | 36-44px | 500-600 | Under section titles, subheadings |
| **Card Title** | 40-48px | 700 | Feature cards, list group headers |
| **Body Text** | 32-40px | 500-600 | Paragraphs, list items, descriptions |
| **Tags / Pills** | 28-36px | 600 | Labels, badges, categories |
| **Icons** | 56-80px | — | Card icons, decorative elements |

### Icon Selection Guide

The full [Lucide icon library](https://lucide.dev/icons/) (1500+ icons) is available. Use kebab-case names (e.g., `"shield-check"`, `"brain-circuit"`). Browse https://lucide.dev/icons/ to find the best match.

**Semantic mapping — pick icons by concept, not by guessing:**

| Concept | Recommended Icon | Alternatives |
|---------|-----------------|--------------|
| AI / Intelligence | `brain` | `brain-circuit`, `sparkles`, `bot` |
| Speed / Performance | `zap` | `gauge`, `rocket`, `timer` |
| Security / Privacy | `shield` | `shield-check`, `lock`, `key-round` |
| Data / Analytics | `bar-chart-3` | `pie-chart`, `trending-up`, `chart-line` |
| Money / Cost | `dollar-sign` | `wallet`, `coins`, `banknote` |
| Team / Collaboration | `users` | `users-round`, `handshake`, `message-circle` |
| Cloud / Infra | `cloud` | `server`, `database`, `hard-drive` |
| Code / Dev | `code` | `terminal`, `file-code`, `braces` |
| Success / Complete | `check-circle` | `circle-check`, `badge-check`, `trophy` |
| Warning / Risk | `alert-triangle` | `shield-alert`, `alert-circle`, `ban` |
| Innovation / New | `lightbulb` | `sparkles`, `wand`, `lamp` |
| Growth / Increase | `trending-up` | `arrow-up-right`, `chart-no-axes-combined`, `sprout` |
| Time / Schedule | `clock` | `calendar`, `timer`, `hourglass` |
| Global / World | `globe` | `earth`, `map`, `languages` |
| Settings / Config | `settings` | `sliders-horizontal`, `wrench`, `cog` |
| Communication | `message-circle` | `mail`, `phone`, `megaphone` |
| Education / Learn | `graduation-cap` | `book-open`, `school`, `notebook-pen` |
| Health / Medical | `heart-pulse` | `activity`, `stethoscope`, `pill` |
| Mobile / App | `smartphone` | `tablet`, `app-window`, `monitor` |
| Integration / Connect | `plug` | `cable`, `link`, `puzzle` |
| Search / Discover | `search` | `scan`, `radar`, `compass` |
| Storage / Save | `database` | `hard-drive`, `archive`, `save` |
| Automation / Workflow | `workflow` | `repeat`, `git-branch`, `route` |
| Creative / Design | `palette` | `brush`, `pen-tool`, `figma` |
| Video / Media | `video` | `play-circle`, `clapperboard`, `film` |

**Rules:**
- Always use semantic names from this table when the concept matches
- For concepts not listed, browse https://lucide.dev/icons/ and pick the closest match
- Prefer specific icons over generic ones (e.g., `shield-check` over `check` for "security verified")
- Each card/section in a group should use a **different** icon — never repeat icons in parallel items

### Brand Logos for AI / LLM Topics

When the video topic involves specific AI companies, LLM models, or developer tools, use `@lobehub/icons` for **official brand logos** (OpenAI, Anthropic, Google, Meta, Mistral, Cohere, Hugging Face, LangChain, etc.). Lucide covers generic concepts; lobehub covers the brand mark itself.

**Install (in the Remotion project root, not in `videos/{name}/`):**

```bash
npm i @lobehub/icons
```

**Upstream agent guidance:** read https://lobehub.com/icons/skill.md for the current import pattern and component API. The package evolves independently — always check the upstream skill doc rather than relying on cached examples here.

**When to use which:**
- Concept icon (shield, brain, zap) → Lucide
- Brand mark (the OpenAI logo, the Claude logo) → lobehub
- Never use both redundantly for the same item (e.g., a card titled "OpenAI" needs only the lobehub OpenAI mark, not lobehub + Lucide `sparkles`)

### Layout Patterns (recommended)

| Pattern | Recommended |
|---------|-------------|
| **Card** | `borderRadius: 24-32px`, `padding: 48px 56px`, colored border (3px) + shadow |
| **Section Padding** | `40px 60px` content, `40px 80px` hero |
| **Grid Gap** | `28-40px` |
| **Content Max Width** | `1500-1700px` for grids, `1400px` for centered blocks |
| **Hero / Impact** | Full viewport centered with decorative icon |
| **2-column cards** | `display: grid; gridTemplateColumns: 1fr 1fr` with gap 36-56px |
| **4+ items** | `display: grid; gridTemplateColumns: repeat(4, 1fr)` or `repeat(2, 1fr)` |
| **Workflow/Steps** | Unique color per step, circular number badge, colored border |

### Color Coding Examples

| Scenario | Approach |
|----------|----------|
| **Feature cards (4)** | Green/purple/orange/pink — different theme color per card |
| **Workflow steps** | Blue→purple→green→orange→pink→cyan — gradient sequence |
| **Intro cards (2)** | Green vs purple — contrasting palettes |
| **Outro buttons** | Red/orange/yellow/pink — unique color per action |

> **Principle:** Fill space, enlarge elements, enrich colors — no large blank areas.

---

## Animated Backgrounds (SHOULD use)

Every section SHOULD include at least one animated background layer for depth. Available layers from `AnimatedBackground.tsx`:

| Component | Effect | Best For |
|-----------|--------|----------|
| `MovingGradient` | Slowly rotating gradient overlay | Any section — adds subtle motion |
| `FloatingShapes` | Drifting circles/rings | Hero, feature sections — adds depth |
| `GridPattern` | Dot/line/cross grid overlay | Data sections, technical content |
| `GlowOrb` | Pulsing color orb with blur | Hero, stat highlight — focal point |
| `AccentLine` | Animated expanding line | Section dividers, emphasis |

**Rules:**
- Use 1-2 background layers per section (not all at once)
- Alternate between background styles across sections
- Keep opacity low (0.03-0.08) — backgrounds should be felt, not seen
- `FloatingShapes` count: 3-5 shapes, more than 6 looks cluttered

---

## Section Layout Presets (SHOULD use)

Pre-built layouts from `SectionLayouts.tsx` — the agent SHOULD pick from these before creating custom layouts. Each includes animated backgrounds, proper spacing, and theme integration.

| Layout | Visual | Best For |
|--------|--------|----------|
| `SplitLayout` | Content left + visual right (or reversed) | Feature highlight, explanation + diagram |
| `StatHighlight` | Full-bleed big number with glow orb | Key metric, percentage, impact statement |
| `ZigzagCards` | Alternating left/right cards with colored borders | Feature list, pros/cons, step-by-step |
| `CenteredShowcase` | Centered content with dual glow orbs + accent lines | Key quote, thesis, conclusion |
| `MetricsRow` | Dashboard-style stat cards in grid | Comparison numbers, KPIs, benchmarks |
| `StepProgress` | Numbered steps with active highlight | Workflow, tutorial steps, process |

Plus existing components: `ComparisonCard`, `Timeline`, `CodeBlock`, `QuoteBlock`, `FeatureGrid`, `DataBar`, `StatCounter`, `FlowChart`, `IconCard`, `MediaSection`, `DiagramReveal`

### SVG Draw-On Animations

`FlowChart` and `Timeline` now use animated SVG paths with draw-on effects via `@remotion/paths`. The `DiagramReveal` component provides general-purpose node+edge diagram animation.

| Component | Draw-On Feature | Use Case |
|-----------|----------------|----------|
| `FlowChart` | Arrow connectors draw progressively between step cards | Process flows, pipelines |
| `Timeline` | Node circles and vertical connectors draw on in sequence | History, milestones |
| `DiagramReveal` | Arbitrary node+edge graphs with curve/elbow/straight edges | Architecture diagrams, mind maps, network graphs |

**Animation hooks** (`animations.tsx`):
- `useDrawOn(path, enabled, delay, duration, preset)` — animate a single SVG path
- `useStaggeredDrawOn(paths, enabled, delay, durationPerPath, interval, preset)` — animate multiple paths sequentially

**DiagramReveal props**:
- `nodes`: `{ id, label, x, y, icon?, width?, height? }[]` — positioned boxes in SVG viewBox
- `edges`: `{ from, to, label?, style? }[]` — connections between nodes (`"curve"` | `"straight"` | `"elbow"`)

### Audio Waveform Visualization

`AudioWaveform` renders a real-time frequency visualization synced to the TTS narration audio. Makes the video feel alive rather than a slideshow with voiceover.

| Prop | Default | Description |
|------|---------|-------------|
| `mode` | `"bars"` | `"bars"` (spectrum bars), `"wave"` (filled waveform), `"dots"` (pulsing dots) |
| `position` | `"bottom"` | `"bottom"`, `"top"` (absolute positioned), or `"inline"` (flow layout) |
| `barCount` | `32` | Number of frequency bars/samples |
| `height` | `60` | Height in pixels (design space) |
| `opacity` | `0.4` | Overall opacity — keep subtle (0.2-0.5) to avoid distraction |

**Recommended usage**: Add `<AudioWaveform props={props} position="bottom" opacity={0.3} height={40} />` inside `Video.tsx` as a persistent overlay across all sections, or per-section for selective visibility.

### Lottie Animations (After Effects)

`LottieAnimation` loads and plays After Effects animations exported as Lottie JSON. Unlocks the [LottieFiles](https://lottiefiles.com/) ecosystem (100,000+ free animations).

| Prop | Default | Description |
|------|---------|-------------|
| `src` | — | Path to JSON in `--public-dir` (via `staticFile`) or full CORS-enabled URL |
| `animationData` | — | Pre-loaded JSON data (takes precedence over `src`) |
| `loop` | `false` | Whether to loop the animation |
| `direction` | `"forward"` | `"forward"` or `"backward"` |
| `playbackRate` | `1` | Speed multiplier |
| `enableEntrance` | `false` | Wrap in entrance fade-in animation |

**Recommended usage**: Download Lottie JSON files to `videos/{name}/animations/`, then reference with `<LottieAnimation src="animations/brain.json" width={200} height={200} loop />` (resolved via `--public-dir`). Use for concept icons, character animations, decorative elements, or section transitions.

### Layout Sequencing Rules (MUST follow)

The agent MUST vary layouts across sections. Follow these rules to prevent visual monotony:

| Rule | Requirement |
|------|-------------|
| **No repeat** | Never use the same layout preset for consecutive sections |
| **Alternate density** | Follow a high-density section (grid/cards) with a low-density one (showcase/stat) |
| **Background variety** | Consecutive sections must use different background layers |
| **Hero → Impact → Detail → Breathe** | Recommended rhythm: start bold, add detail, give a visual break, repeat |

**Recommended sequencing for 7-section video:**

```
1. Hero          → CenteredShowcase or custom hero (high impact)
2. Overview      → ZigzagCards or FeatureGrid (structured content)
3. Core concept  → SplitLayout (explanation + visual)
4. Data/metrics  → MetricsRow or StatHighlight (visual break with numbers)
5. Deep dive     → StepProgress or Timeline (sequential content)
6. Summary       → CenteredShowcase (return to high impact)
7. Outro         → Custom outro with icons
```

---

## Animation Best Practices (SHOULD follow)

### Use continuous animations for visual life

Every section should have at least subtle continuous motion:
- Background: `MovingGradient` or `FloatingShapes` (always present)
- Decorative: `GlowOrb` with `usePulse` (for emphasis sections)
- Content: stagger entrance delays (6-10 frames between items)

### Text reveal for key statements

Use `useTextReveal` or `useCharReveal` for:
- Hero title (character reveal, 2 frames/char)
- Key statistics or conclusions (word reveal, 4 frames/word)
- NOT for body text or descriptions (too slow, use regular entrance)

### Animation timing guidelines

| Element | Entrance | Stagger | Exit |
|---------|----------|---------|------|
| Title | 0 delay, "snappy" preset | — | — |
| Subtitle | 8 frame delay | — | — |
| Cards/items | 6-10 frame stagger | `staggerDelay(i, 8)` | — |
| Decorative | 15+ frame delay | — | — |
| Background | Continuous (no entrance) | — | — |
