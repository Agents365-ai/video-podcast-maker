# Transition & Animation Enhancement Design

## Goal

Replace hard-cuts between chapters with smooth transitions using `@remotion/transitions`, and upgrade element entrance animations from simple opacity+translateY to a spring-based system with stagger support.

## Changes

### 1. Video.tsx: Sequence → TransitionSeries

Replace the `sections.map(s => <Sequence>)` loop with `<TransitionSeries>`:

- Each section becomes `<TransitionSeries.Sequence durationInFrames={...}>`
- Between sections, insert `<TransitionSeries.Transition presentation={...} timing={...} />`
- No transition after the last section
- Transition type and duration driven by Studio props

Transition mapping function:

```typescript
const getPresentation = (type: string) => {
  switch (type) {
    case "fade": return fade();
    case "slide": return slide({ direction: "from-right" });
    case "wipe": return wipe({ direction: "from-right" });
    case "none": return none();
    default: return fade();
  }
};
```

### 2. Audio Sync Compensation

TransitionSeries total duration = sum of sections - (N-1) * transitionDuration.

To keep audio in sync (Audio components are outside TransitionSeries), add the lost frames back to the first section:

```
compensatedFirstDuration = firstSection.duration_frames + (sectionCount - 1) * transitionDuration
```

This ensures TransitionSeries total matches timing.total_frames.

### 3. Root.tsx: New Props

Add to Zod schema:

```typescript
transitionType: z.enum(["fade", "slide", "wipe", "none"]).describe("Chapter transition effect")
transitionDuration: z.number().min(0).max(30).describe("Transition duration (frames)")
```

Defaults: `transitionType: "fade"`, `transitionDuration: 15`

### 4. Entrance Animation Upgrade

Replace current `useEntrance`:

```typescript
// Before: only opacity + translateY
const useEntrance = (enabled: boolean) => { ... }

// After: spring-based with delay for stagger
const useEntrance = (enabled: boolean, delay = 0) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (!enabled) return { opacity: 1, translateY: 0, scale: 1 };

  const progress = spring({ frame, fps, delay, config: { damping: 200 }, durationInFrames: 30 });
  return {
    opacity: interpolate(progress, [0, 1], [0, 1]),
    translateY: interpolate(progress, [0, 1], [40, 0]),
    scale: interpolate(progress, [0, 1], [0.95, 1]),
  };
};
```

Stagger usage in list items: `useEntrance(enabled, i * 5)` where i is item index.

### 5. Package.json

Add dependency: `"@remotion/transitions": "^4.0.0"`

### 6. SKILL.md

Update Step 9 documentation to mention transition options and Studio UI controls.

## File List

| File | Change |
|------|--------|
| `templates/Video.tsx` | Sequence → TransitionSeries, transition mapping, useEntrance upgrade |
| `templates/Root.tsx` | Schema + defaults for transitionType, transitionDuration |
| `package.json` | Add @remotion/transitions |
| `SKILL.md` | Step 9 transition docs |
