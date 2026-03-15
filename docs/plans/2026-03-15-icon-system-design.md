# Icon System Design

## Overview

Replace emoji-based icons with a unified icon system using Lucide React, while maintaining backward compatibility with emoji strings.

## Goals

1. **Replace emoji with SVG** — Professional, consistent rendering at 4K
2. **Backward compatible** — Emoji strings still work
3. **Animated icons** — Entrance/pulse/bounce animations
4. **Semantic lookup** — Claude writes "rocket", system resolves to `LuRocket`

## Architecture

### Icon Resolution Chain

```
name="rocket"     → Lucide LuRocket (SVG)
name="💡"         → Direct emoji render
name="unknown"    → Fallback placeholder or warning
```

### Core Component: `<Icon>`

```typescript
<Icon
  name="rocket"              // Semantic name or emoji
  size={56}                  // Default 56px (SKILL.md minimum)
  color={props.primaryColor} // Theme color
  animate="entrance"         // "none" | "entrance" | "pulse" | "bounce"
  delay={0}                  // Animation delay frames
/>
```

### Animation Types

| Animation | Effect |
|-----------|--------|
| `entrance` | fadeIn + scaleUp (default) |
| `pulse` | Continuous breathing effect |
| `bounce` | Bouncy entrance |
| `none` | No animation |

### Semantic Mapping (`iconMap.ts`)

~80 commonly used icons organized by category:

| Category | Examples |
|----------|----------|
| Actions | rocket, play, pause, check, x, plus, minus |
| Objects | lightbulb, target, star, heart, flag, trophy |
| Tech | code, terminal, database, server, cloud, cpu |
| Media | video, music, image, mic, camera |
| Finance | dollar, chart, trending-up, wallet |
| Communication | message, mail, bell, share |

### User Preference System

New props in `Root.tsx` VideoProps schema:

```typescript
iconStyle: "lucide" | "emoji" | "mixed"  // Default: "lucide"
iconAnimation: "entrance" | "none"       // Default: "entrance"
```

Priority chain:
```
Component props > Root.tsx config > Default (Lucide + entrance)
```

### Emoji Detection

```typescript
const isEmoji = (s: string) => /\p{Emoji}/u.test(s) && s.length <= 2
```

## File Structure

```
templates/components/
├── Icon.tsx          # Core component
├── iconMap.ts        # Semantic → Lucide mapping
├── index.ts          # Updated barrel export
├── IconCard.tsx      # Updated to use <Icon>
├── FeatureGrid.tsx   # Updated to use <Icon>
├── FlowChart.tsx     # Updated to use <Icon>
├── StatCounter.tsx   # Updated to use <Icon>
```

## Dependencies

```bash
npm install lucide-react
```

## Backward Compatibility

Existing code continues to work:

```typescript
// Both valid:
{ icon: "lightbulb", title: "Feature" }  // Semantic → Lucide
{ icon: "💡", title: "Feature" }          // Emoji → direct render
```

## Usage Examples

### Claude generates content:
```typescript
items: [
  { icon: "rocket", title: "Launch" },
  { icon: "check", title: "Complete" },
]
```

### User forces emoji globally:
```typescript
// In Root.tsx props
iconStyle: "emoji"
```
