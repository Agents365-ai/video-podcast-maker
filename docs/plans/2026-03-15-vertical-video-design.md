# Vertical Video (9:16) Support Design

## Goal

Add 9:16 vertical video support as a "highlight clip" companion to the main 16:9 horizontal video. Used for B站竖屏模式 to drive traffic to the full-length version.

## Scope

- Vertical = 60-90 second highlight clips, not full podcast
- Reuses existing audio/timing infrastructure
- Shares component library with horizontal templates

## Changes

### 1. Root.tsx — Add orientation prop + vertical Composition

- Add `orientation` to Zod schema: `z.enum(["horizontal", "vertical"])`
- Register new `<Composition id="MyVideoVertical">` at 2160x3840
- Default orientation = "horizontal" for existing composition

### 2. layouts.tsx — Scale4K supports vertical

- Scale4K accepts orientation prop
- Horizontal: 1920x1080 design → scale(2) → 3840x2160
- Vertical: 1080x1920 design → scale(2) → 2160x3840

### 3. Video.tsx — Orientation-aware sections

- SectionComponent layouts adapt: vertical uses larger font, centered layout, less content per screen
- Vertical hero: title 96px, vertically centered with more whitespace
- Vertical content: single column, stacked layout, body 32px
- Pass orientation to all section components via props

### 4. ChapterProgressBar — Hide in vertical mode

- Short clips don't need chapter progress
- Controlled by existing `showProgressBar` prop (default false for vertical)

### 5. Thumbnail.tsx — 9:16 support

- Add "9:16" to aspectRatio type
- Register `<Still id="Thumbnail9x16">` at 1080x1920

### 6. Component library adaptation

- Components already use flex/percentage widths — will auto-adapt
- FeatureGrid: vertical forces columns=1
- ComparisonCard: vertical stacks vertically instead of side-by-side
- DataBar: no change needed (already full-width)

### 7. SKILL.md — Optional vertical step

- Add optional step after main render for generating vertical highlight clips
- Claude selects 2-3 key sections, renders vertical version
