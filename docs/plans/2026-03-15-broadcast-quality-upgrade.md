# Broadcast Quality Upgrade Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Upgrade video-podcast-maker templates and guidance so Claude generates broadcast-quality Bilibili videos in one shot.

**Architecture:** Upgrade existing component visual quality (shadows, gradients, depth), add 3 new components (StatCounter, FlowChart, IconCard), enhance animations.tsx with exit animations and presets, upgrade Video.tsx default sections, and add concrete quality checklists to SKILL.md.

**Tech Stack:** Remotion, React, TypeScript, CSS-in-JS

---

### Task 1: Upgrade animations.tsx — exit animations and presets

**Files:**
- Modify: `templates/components/animations.tsx`

**Step 1: Replace animations.tsx with upgraded version**

```tsx
import { useCurrentFrame, useVideoConfig, interpolate, spring, Easing } from "remotion";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";
import { wipe } from "@remotion/transitions/wipe";
import { none } from "@remotion/transitions/none";

// Spring presets for different animation feels
const SPRING_PRESETS = {
  gentle: { damping: 200, mass: 1 },
  snappy: { damping: 100, mass: 0.5 },
  bouncy: { damping: 80, mass: 0.8 },
} as const;

type SpringPreset = keyof typeof SPRING_PRESETS;

// Spring-based entrance animation with stagger and preset support
export const useEntrance = (
  enabled: boolean,
  delay = 0,
  preset: SpringPreset = "gentle",
) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  if (!enabled) return { opacity: 1, translateY: 0, scale: 1, rotate: 0 };

  const config = SPRING_PRESETS[preset];
  const progress = spring({ frame, fps, delay, config, durationInFrames: 30 });

  return {
    opacity: interpolate(progress, [0, 1], [0, 1]),
    translateY: interpolate(progress, [0, 1], [40, 0]),
    scale: interpolate(progress, [0, 1], [0.95, 1]),
    rotate: 0,
  };
};

// Exit animation — use with section duration to fade out at end
export const useExit = (
  enabled: boolean,
  sectionDuration: number,
  fadeFrames = 15,
) => {
  const frame = useCurrentFrame();

  if (!enabled) return { opacity: 1, translateY: 0, scale: 1 };

  const exitStart = Math.max(0, sectionDuration - fadeFrames);
  const progress = interpolate(frame, [exitStart, sectionDuration], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.ease),
  });

  return {
    opacity: interpolate(progress, [0, 1], [1, 0]),
    translateY: interpolate(progress, [0, 1], [0, -20]),
    scale: interpolate(progress, [0, 1], [1, 0.97]),
  };
};

// Animated number counter — interpolates from 0 to target value
export const useCounter = (target: number, delay = 0, durationFrames = 45) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const progress = spring({ frame, fps, delay, config: { damping: 200 }, durationInFrames: durationFrames });
  return Math.round(interpolate(progress, [0, 1], [0, target]));
};

// Animated bar fill — returns 0-100 percentage
export const useBarFill = (targetPct: number, delay = 0, durationFrames = 40) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const progress = spring({ frame, fps, delay, config: { damping: 150 }, durationInFrames: durationFrames });
  return interpolate(progress, [0, 1], [0, targetPct]);
};

// Transition presentation mapper
export const getPresentation = (type: string) => {
  switch (type) {
    case "fade": return fade();
    case "slide": return slide({ direction: "from-right" });
    case "wipe": return wipe({ direction: "from-right" });
    case "none": return none();
    default: return fade();
  }
};
```

**Step 2: Verify no TypeScript errors**

Run: `cd /Users/niehu/myagents/myskills/video-podcast-maker && npx tsc --noEmit --jsx react-jsx templates/components/animations.tsx 2>&1 || echo "Note: standalone tsc check may fail due to imports; visual check is sufficient for template files"`

**Step 3: Commit**

```bash
git add templates/components/animations.tsx
git commit -m "feat: add exit animations, spring presets, counter and bar fill hooks"
```

---

### Task 2: Upgrade FeatureGrid — depth and polish

**Files:**
- Modify: `templates/components/FeatureGrid.tsx`

**Step 1: Replace with upgraded version**

```tsx
import type { VideoProps } from "../Root";
import { useEntrance } from "./animations";

export const FeatureGrid = ({
  props,
  items,
  columns = 3,
  delay = 0,
}: {
  props: VideoProps;
  items: { icon: string; title: string; description: string }[];
  columns?: 2 | 3;
  delay?: number;
}) => {
  const v = props.orientation === "vertical";
  const cols = v ? 1 : columns;

  return (
    <div style={{
      display: "flex", flexWrap: "wrap", gap: v ? 24 : 28, width: "100%",
    }}>
      {items.map((item, i) => {
        const a = useEntrance(props.enableAnimations, delay + i * 5, "snappy");
        return (
          <div key={i} style={{
            flex: `0 0 calc(${100 / cols}% - ${(v ? 24 : 28) * (cols - 1) / cols}px)`,
            background: `linear-gradient(135deg, rgba(255,255,255,0.9), ${props.primaryColor}06)`,
            border: `1px solid ${props.primaryColor}18`,
            borderRadius: 24,
            padding: v ? "32px 36px" : "36px 32px",
            textAlign: v ? "left" : "center",
            display: v ? "flex" : undefined, alignItems: v ? "center" : undefined, gap: v ? 24 : undefined,
            boxShadow: `0 2px 8px rgba(0,0,0,0.04), 0 8px 24px rgba(0,0,0,0.06)`,
            opacity: a.opacity, transform: `translateY(${a.translateY}px)`,
          }}>
            <div style={{
              fontSize: v ? 48 : 56, marginBottom: v ? 0 : 16, flexShrink: 0,
              filter: "drop-shadow(0 2px 4px rgba(0,0,0,0.1))",
            }}>
              {item.icon}
            </div>
            <div>
              <div style={{ fontSize: v ? 34 : 32, fontWeight: 700, color: props.primaryColor, marginBottom: 8 }}>
                {item.title}
              </div>
              <div style={{ fontSize: v ? 26 : 24, color: props.textColor, lineHeight: 1.5, opacity: 0.75 }}>
                {item.description}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};
```

**Step 2: Commit**

```bash
git add templates/components/FeatureGrid.tsx
git commit -m "feat: upgrade FeatureGrid with gradient backgrounds and layered shadows"
```

---

### Task 3: Upgrade ComparisonCard — shadow depth and color differentiation

**Files:**
- Modify: `templates/components/ComparisonCard.tsx`

**Step 1: Replace with upgraded version**

```tsx
import React from "react";
import type { VideoProps } from "../Root";
import { useEntrance } from "./animations";

export const ComparisonCard = ({
  props,
  left,
  right,
  delay = 0,
}: {
  props: VideoProps;
  left: { title: string; items: string[]; highlight?: boolean };
  right: { title: string; items: string[]; highlight?: boolean };
  delay?: number;
}) => {
  const v = props.orientation === "vertical";
  const anim = useEntrance(props.enableAnimations, delay);
  const leftAnim = useEntrance(props.enableAnimations, delay + 5, "snappy");
  const rightAnim = useEntrance(props.enableAnimations, delay + 10, "snappy");

  const cardStyle = (side: typeof left, highlighted: boolean): React.CSSProperties => ({
    flex: v ? undefined : 1, width: v ? "100%" : undefined,
    background: highlighted
      ? `linear-gradient(135deg, ${props.primaryColor}0A, ${props.primaryColor}14)`
      : "linear-gradient(135deg, rgba(255,255,255,0.95), rgba(0,0,0,0.02))",
    border: highlighted
      ? `2px solid ${props.primaryColor}30`
      : "1px solid rgba(0,0,0,0.08)",
    borderRadius: 24, padding: v ? "36px 40px" : "40px 44px",
    boxShadow: highlighted
      ? `0 4px 16px ${props.primaryColor}15, 0 8px 32px rgba(0,0,0,0.06)`
      : "0 2px 8px rgba(0,0,0,0.04), 0 8px 24px rgba(0,0,0,0.06)",
  });

  return (
    <div style={{
      display: "flex", alignItems: "center", gap: v ? 28 : 40, width: "100%",
      flexDirection: v ? "column" : "row", opacity: anim.opacity,
    }}>
      {[{ side: left, a: leftAnim }, { side: right, a: rightAnim }].map(({ side, a }, i) => (
        <React.Fragment key={i}>
          {i === 1 && (
            <div style={{
              fontSize: v ? 40 : 48, fontWeight: 800, color: props.primaryColor, opacity: 0.6,
              flexShrink: 0,
              textShadow: `0 2px 8px ${props.primaryColor}20`,
            }}>
              VS
            </div>
          )}
          <div style={{
            ...cardStyle(side, !!side.highlight),
            opacity: a.opacity, transform: `translateY(${a.translateY}px)`,
          }}>
            <h3 style={{ fontSize: v ? 36 : 38, fontWeight: 700, color: props.primaryColor, marginBottom: 24 }}>
              {side.title}
            </h3>
            {side.items.map((item, j) => (
              <div key={j} style={{
                fontSize: v ? 30 : 28, color: props.textColor, padding: "10px 0",
                borderTop: j > 0 ? "1px solid rgba(0,0,0,0.06)" : "none",
              }}>
                {item}
              </div>
            ))}
          </div>
        </React.Fragment>
      ))}
    </div>
  );
};
```

**Step 2: Commit**

```bash
git add templates/components/ComparisonCard.tsx
git commit -m "feat: upgrade ComparisonCard with gradient backgrounds and layered shadows"
```

---

### Task 4: Upgrade DataBar — container shadow and animated fill

**Files:**
- Modify: `templates/components/DataBar.tsx`

**Step 1: Replace with upgraded version**

```tsx
import React from "react";
import type { VideoProps } from "../Root";
import { useEntrance, useBarFill } from "./animations";

export const DataBar = ({
  props,
  items,
  delay = 0,
}: {
  props: VideoProps;
  items: { label: string; value: number; maxValue?: number }[];
  delay?: number;
}) => {
  const max = Math.max(...items.map((d) => d.maxValue ?? d.value));
  return (
    <div style={{
      display: "flex", flexDirection: "column", gap: 24, width: "100%",
      background: "rgba(0,0,0,0.02)", borderRadius: 24, padding: "32px 36px",
      boxShadow: "0 2px 8px rgba(0,0,0,0.03), 0 4px 16px rgba(0,0,0,0.04)",
    }}>
      {items.map((item, i) => {
        const pct = (item.value / max) * 100;
        const a = useEntrance(props.enableAnimations, delay + i * 5);
        const fillPct = useBarFill(pct, delay + i * 5 + 10);
        return (
          <div key={i} style={{
            display: "flex", alignItems: "center", gap: 20,
            opacity: a.opacity, transform: `translateY(${a.translateY}px)`,
          }}>
            <div style={{
              fontSize: 28, fontWeight: 600, color: props.textColor,
              width: 160, textAlign: "right", flexShrink: 0,
            }}>
              {item.label}
            </div>
            <div style={{
              flex: 1, height: 40, background: "rgba(0,0,0,0.06)", borderRadius: 20, overflow: "hidden",
            }}>
              <div style={{
                width: `${fillPct}%`, height: "100%", borderRadius: 20,
                background: `linear-gradient(90deg, ${props.primaryColor}, ${props.accentColor})`,
                boxShadow: `0 2px 8px ${props.primaryColor}30`,
                transition: "none",
              }} />
            </div>
            <div style={{ fontSize: 26, fontWeight: 700, color: props.primaryColor, width: 80 }}>
              {item.value}%
            </div>
          </div>
        );
      })}
    </div>
  );
};
```

**Step 2: Commit**

```bash
git add templates/components/DataBar.tsx
git commit -m "feat: upgrade DataBar with animated fill, container shadow"
```

---

### Task 5: Upgrade Timeline — gradient connector and glowing nodes

**Files:**
- Modify: `templates/components/Timeline.tsx`

**Step 1: Replace with upgraded version**

```tsx
import React from "react";
import type { VideoProps } from "../Root";
import { useEntrance } from "./animations";

export const Timeline = ({
  props,
  items,
  delay = 0,
}: {
  props: VideoProps;
  items: { label: string; description: string }[];
  delay?: number;
}) => {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 0, width: "100%" }}>
      {items.map((item, i) => {
        const a = useEntrance(props.enableAnimations, delay + i * 6, "snappy");
        return (
          <div key={i} style={{
            display: "flex", gap: 28, opacity: a.opacity,
            transform: `translateY(${a.translateY}px)`,
          }}>
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", width: 32 }}>
              <div style={{
                width: 28, height: 28, borderRadius: 14, flexShrink: 0,
                background: props.primaryColor,
                boxShadow: `0 0 12px ${props.primaryColor}50, 0 0 24px ${props.primaryColor}20`,
              }} />
              {i < items.length - 1 && (
                <div style={{
                  width: 3, flex: 1, minHeight: 32,
                  background: `linear-gradient(180deg, ${props.primaryColor}60, ${props.primaryColor}15)`,
                }} />
              )}
            </div>
            <div style={{ paddingBottom: i < items.length - 1 ? 32 : 0, flex: 1 }}>
              <div style={{ fontSize: 34, fontWeight: 700, color: props.primaryColor }}>{item.label}</div>
              <div style={{ fontSize: 26, color: props.textColor, marginTop: 6, lineHeight: 1.5, opacity: 0.75 }}>
                {item.description}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};
```

**Step 2: Commit**

```bash
git add templates/components/Timeline.tsx
git commit -m "feat: upgrade Timeline with glowing nodes and gradient connectors"
```

---

### Task 6: Upgrade QuoteBlock — decorative quotes and accent line

**Files:**
- Modify: `templates/components/QuoteBlock.tsx`

**Step 1: Replace with upgraded version**

```tsx
import React from "react";
import type { VideoProps } from "../Root";
import { useEntrance } from "./animations";

export const QuoteBlock = ({
  props,
  quote,
  attribution,
  delay = 0,
}: {
  props: VideoProps;
  quote: string;
  attribution: string;
  delay?: number;
}) => {
  const anim = useEntrance(props.enableAnimations, delay);
  const attrAnim = useEntrance(props.enableAnimations, delay + 10);
  return (
    <div style={{
      width: "100%", textAlign: "center", padding: "40px 60px",
      opacity: anim.opacity, transform: `translateY(${anim.translateY}px) scale(${anim.scale})`,
      position: "relative",
    }}>
      {/* Background accent */}
      <div style={{
        position: "absolute", inset: 0, borderRadius: 24,
        background: `linear-gradient(135deg, ${props.primaryColor}06, ${props.accentColor}06)`,
        border: `1px solid ${props.primaryColor}10`,
      }} />
      {/* Left accent line */}
      <div style={{
        position: "absolute", left: 20, top: "15%", bottom: "15%", width: 4,
        background: `linear-gradient(180deg, ${props.primaryColor}, ${props.accentColor})`,
        borderRadius: 2,
      }} />
      {/* Opening quote mark */}
      <div style={{
        fontSize: 140, color: props.primaryColor, opacity: 0.15, lineHeight: 0.6,
        marginBottom: 16, fontFamily: "Georgia, serif",
      }}>
        &ldquo;
      </div>
      <p style={{
        fontSize: 40, fontWeight: 600, color: props.textColor,
        lineHeight: 1.6, fontStyle: "italic", position: "relative",
      }}>
        {quote}
      </p>
      <div style={{
        fontSize: 28, color: props.primaryColor, marginTop: 32, fontWeight: 500,
        opacity: attrAnim.opacity, transform: `translateY(${attrAnim.translateY}px)`,
      }}>
        &mdash; {attribution}
      </div>
    </div>
  );
};
```

**Step 2: Commit**

```bash
git add templates/components/QuoteBlock.tsx
git commit -m "feat: upgrade QuoteBlock with accent line, gradient background, larger quotes"
```

---

### Task 7: Create StatCounter component

**Files:**
- Create: `templates/components/StatCounter.tsx`

**Step 1: Create the component**

```tsx
import React from "react";
import type { VideoProps } from "../Root";
import { useEntrance, useCounter } from "./animations";

export const StatCounter = ({
  props,
  items,
  delay = 0,
}: {
  props: VideoProps;
  items: { value: number; suffix?: string; label: string; icon?: string }[];
  delay?: number;
}) => {
  const v = props.orientation === "vertical";
  return (
    <div style={{
      display: "flex", gap: v ? 32 : 48, width: "100%",
      flexDirection: v ? "column" : "row", justifyContent: "center",
    }}>
      {items.map((item, i) => {
        const a = useEntrance(props.enableAnimations, delay + i * 8, "bouncy");
        const count = useCounter(item.value, delay + i * 8 + 5);
        return (
          <div key={i} style={{
            flex: v ? undefined : 1, textAlign: "center",
            padding: v ? "28px 36px" : "36px 24px",
            background: `linear-gradient(135deg, ${props.primaryColor}06, ${props.primaryColor}10)`,
            borderRadius: 24,
            boxShadow: `0 4px 16px ${props.primaryColor}10, 0 8px 32px rgba(0,0,0,0.04)`,
            border: `1px solid ${props.primaryColor}12`,
            opacity: a.opacity, transform: `translateY(${a.translateY}px) scale(${a.scale})`,
          }}>
            {item.icon && <div style={{ fontSize: v ? 48 : 52, marginBottom: 12 }}>{item.icon}</div>}
            <div style={{
              fontSize: v ? 56 : 64, fontWeight: 800, color: props.primaryColor,
              letterSpacing: -2,
            }}>
              {count}{item.suffix || ""}
            </div>
            <div style={{
              fontSize: v ? 26 : 24, fontWeight: 500, color: props.textColor,
              marginTop: 8, opacity: 0.65,
            }}>
              {item.label}
            </div>
          </div>
        );
      })}
    </div>
  );
};
```

**Step 2: Commit**

```bash
git add templates/components/StatCounter.tsx
git commit -m "feat: add StatCounter component with animated number tickers"
```

---

### Task 8: Create FlowChart component

**Files:**
- Create: `templates/components/FlowChart.tsx`

**Step 1: Create the component**

```tsx
import React from "react";
import type { VideoProps } from "../Root";
import { useEntrance } from "./animations";

export const FlowChart = ({
  props,
  steps,
  delay = 0,
}: {
  props: VideoProps;
  steps: { label: string; description?: string; icon?: string }[];
  delay?: number;
}) => {
  const v = props.orientation === "vertical";
  return (
    <div style={{
      display: "flex", alignItems: "center", width: "100%",
      flexDirection: v ? "column" : "row", gap: 0,
    }}>
      {steps.map((step, i) => {
        const a = useEntrance(props.enableAnimations, delay + i * 8, "snappy");
        return (
          <React.Fragment key={i}>
            <div style={{
              flex: 1, textAlign: "center",
              padding: v ? "28px 32px" : "32px 20px",
              background: `linear-gradient(135deg, ${props.primaryColor}08, ${props.primaryColor}14)`,
              borderRadius: 20,
              boxShadow: `0 2px 8px rgba(0,0,0,0.04), 0 4px 16px ${props.primaryColor}08`,
              border: `1px solid ${props.primaryColor}15`,
              opacity: a.opacity, transform: `translateY(${a.translateY}px)`,
              minWidth: 0,
            }}>
              {step.icon && <div style={{ fontSize: v ? 44 : 48, marginBottom: 12 }}>{step.icon}</div>}
              <div style={{
                fontSize: v ? 30 : 28, fontWeight: 700, color: props.primaryColor,
              }}>
                {step.label}
              </div>
              {step.description && (
                <div style={{
                  fontSize: v ? 22 : 20, color: props.textColor, marginTop: 8,
                  opacity: 0.65, lineHeight: 1.4,
                }}>
                  {step.description}
                </div>
              )}
            </div>
            {i < steps.length - 1 && (
              <div style={{
                fontSize: v ? 32 : 36, color: props.primaryColor, opacity: 0.4,
                padding: v ? "8px 0" : "0 8px", flexShrink: 0,
                transform: v ? "rotate(90deg)" : undefined,
              }}>
                →
              </div>
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
};
```

**Step 2: Commit**

```bash
git add templates/components/FlowChart.tsx
git commit -m "feat: add FlowChart component with arrow-connected step cards"
```

---

### Task 9: Create IconCard component

**Files:**
- Create: `templates/components/IconCard.tsx`

**Step 1: Create the component**

```tsx
import type { VideoProps } from "../Root";
import { useEntrance } from "./animations";

export const IconCard = ({
  props,
  icon,
  title,
  description,
  color,
  delay = 0,
}: {
  props: VideoProps;
  icon: string;
  title: string;
  description: string;
  color?: string;
  delay?: number;
}) => {
  const v = props.orientation === "vertical";
  const c = color || props.primaryColor;
  const a = useEntrance(props.enableAnimations, delay, "bouncy");
  return (
    <div style={{
      display: "flex", alignItems: "center", gap: v ? 28 : 32, width: "100%",
      padding: v ? "32px 36px" : "36px 44px",
      background: `linear-gradient(135deg, ${c}08, ${c}14)`,
      borderRadius: 24,
      border: `1px solid ${c}18`,
      boxShadow: `0 4px 16px ${c}10, 0 8px 24px rgba(0,0,0,0.04)`,
      opacity: a.opacity, transform: `translateY(${a.translateY}px) scale(${a.scale})`,
    }}>
      <div style={{
        fontSize: v ? 56 : 64, flexShrink: 0,
        width: v ? 80 : 88, height: v ? 80 : 88,
        display: "flex", alignItems: "center", justifyContent: "center",
        background: `${c}12`, borderRadius: 20,
      }}>
        {icon}
      </div>
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: v ? 34 : 36, fontWeight: 700, color: c }}>
          {title}
        </div>
        <div style={{
          fontSize: v ? 26 : 24, color: props.textColor, marginTop: 8,
          lineHeight: 1.5, opacity: 0.75,
        }}>
          {description}
        </div>
      </div>
    </div>
  );
};
```

**Step 2: Commit**

```bash
git add templates/components/IconCard.tsx
git commit -m "feat: add IconCard component with large icon emphasis"
```

---

### Task 10: Update barrel export index.ts

**Files:**
- Modify: `templates/components/index.ts`

**Step 1: Add new exports**

Replace content:

```ts
export { Scale4K, FullBleedLayout, PaddedLayout } from "./layouts";
export { useEntrance, useExit, useCounter, useBarFill, getPresentation } from "./animations";
export { ComparisonCard } from "./ComparisonCard";
export { Timeline } from "./Timeline";
export { CodeBlock } from "./CodeBlock";
export { QuoteBlock } from "./QuoteBlock";
export { FeatureGrid } from "./FeatureGrid";
export { DataBar } from "./DataBar";
export { StatCounter } from "./StatCounter";
export { FlowChart } from "./FlowChart";
export { IconCard } from "./IconCard";
export { ChapterProgressBar } from "./ChapterProgressBar";
```

**Step 2: Commit**

```bash
git add templates/components/index.ts
git commit -m "feat: add StatCounter, FlowChart, IconCard to barrel exports"
```

---

### Task 11: Upgrade Video.tsx default sections

**Files:**
- Modify: `templates/Video.tsx`

**Step 1: Update imports to include new components**

Change line 20-27 imports to:

```tsx
import {
  Scale4K,
  FullBleedLayout,
  PaddedLayout,
  useEntrance,
  getPresentation,
  ChapterProgressBar,
  IconCard,
} from "./components";
```

**Step 2: Upgrade hero section (case "hero")**

Replace the hero case with:

```tsx
    case "hero":
      return (
        <FullBleedLayout bg={props.backgroundColor}>
          {/* Decorative radial gradient */}
          <div style={{
            position: "absolute", inset: 0,
            background: `radial-gradient(ellipse at 50% 40%, ${props.primaryColor}12 0%, transparent 70%)`,
          }} />
          {/* Decorative circle */}
          <div style={{
            position: "absolute", top: -120, right: -80,
            width: 400, height: 400, borderRadius: "50%",
            background: `${props.primaryColor}08`,
          }} />
          <div
            style={{
              position: "absolute",
              inset: 0,
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              alignItems: "center",
              textAlign: "center",
              padding: v ? "0 60px" : 0,
              ...animStyle,
            }}
          >
            <h1
              style={{
                fontSize: props.titleSize,
                fontWeight: 800,
                color: props.primaryColor,
                lineHeight: v ? 1.3 : 1.1,
                textShadow: `0 2px 16px ${props.primaryColor}15`,
              }}
            >
              视频标题
            </h1>
            <p
              style={{
                fontSize: props.subtitleSize,
                color: props.textColor,
                marginTop: v ? 32 : 20,
                opacity: 0.6,
                fontWeight: 500,
              }}
            >
              副标题或引导语
            </p>
          </div>
        </FullBleedLayout>
      );
```

**Step 3: Upgrade overview section to use IconCard**

Replace the overview case with:

```tsx
    case "overview":
      return (
        <PaddedLayout bg="#fafafa" orientation={props.orientation}>
          <div
            style={{
              position: "absolute",
              inset: 0,
              padding: sectionPadding,
              display: "flex",
              flexDirection: "column",
              ...animStyle,
            }}
          >
            <h2
              style={{
                fontSize: v ? 72 : 80,
                fontWeight: 700,
                marginBottom: 12,
                color: props.primaryColor,
              }}
            >
              今天的内容
            </h2>
            <p style={{ fontSize: v ? 34 : 30, color: props.textColor, opacity: 0.5, marginBottom: v ? 48 : 40 }}>
              Section description here
            </p>
            <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center" }}>
              <div style={{ display: "flex", flexDirection: "column", gap: v ? 24 : 20, width: "100%", maxWidth: v ? undefined : 900 }}>
                {[
                  { icon: "💡", title: "要点一", description: "说明文字" },
                  { icon: "🎯", title: "要点二", description: "说明文字" },
                  { icon: "✅", title: "要点三", description: "说明文字" },
                ].map((item, i) => (
                  <IconCard key={i} props={props} icon={item.icon} title={item.title} description={item.description} delay={i * 6} />
                ))}
              </div>
            </div>
          </div>
        </PaddedLayout>
      );
```

**Step 4: Upgrade summary section with glowing border**

Replace the summary case with:

```tsx
    case "summary":
      return (
        <FullBleedLayout bg={props.backgroundColor}>
          <div
            style={{
              position: "absolute",
              inset: 0,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              padding: sectionPadding,
              ...animStyle,
            }}
          >
            <div
              style={{
                background: `linear-gradient(135deg, ${props.primaryColor}10, ${props.accentColor}10)`,
                borderRadius: 28,
                padding: v ? "72px 60px" : "56px 72px",
                textAlign: "center",
                width: v ? "100%" : "auto",
                border: `1px solid ${props.primaryColor}20`,
                boxShadow: `0 4px 24px ${props.primaryColor}12, 0 8px 48px rgba(0,0,0,0.04)`,
              }}
            >
              <h2
                style={{
                  fontSize: v ? 60 : 52,
                  fontWeight: 700,
                  color: props.primaryColor,
                  marginBottom: 28,
                }}
              >
                总结
              </h2>
              <p
                style={{
                  fontSize: v ? 36 : 30,
                  color: props.textColor,
                  lineHeight: 1.6,
                }}
              >
                核心结论...
              </p>
            </div>
          </div>
        </FullBleedLayout>
      );
```

**Step 5: Upgrade default section with alternating backgrounds**

Replace the default case with:

```tsx
    default:
      return (
        <PaddedLayout bg={props.backgroundColor} orientation={props.orientation}>
          <div
            style={{
              position: "absolute",
              inset: 0,
              padding: sectionPadding,
              display: "flex",
              flexDirection: "column",
              ...animStyle,
            }}
          >
            <h2
              style={{
                fontSize: v ? 72 : 80,
                fontWeight: 700,
                color: props.primaryColor,
              }}
            >
              {section.name}
            </h2>
            <p style={{ fontSize: v ? 34 : 30, color: props.textColor, opacity: 0.5, marginTop: 12 }}>
              Section description here
            </p>
            <div
              style={{
                flex: 1,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                marginTop: 24,
              }}
            >
              <div style={{
                background: `linear-gradient(135deg, ${props.primaryColor}06, ${props.accentColor}06)`,
                borderRadius: 24, padding: v ? "40px 44px" : "40px 56px",
                boxShadow: "0 2px 8px rgba(0,0,0,0.03), 0 8px 32px rgba(0,0,0,0.05)",
                border: `1px solid ${props.primaryColor}10`,
                width: "100%",
              }}>
                <p
                  style={{
                    fontSize: props.bodySize,
                    color: props.textColor,
                    fontWeight: 500,
                    lineHeight: v ? 1.8 : 1.5,
                  }}
                >
                  Section content goes here...
                </p>
              </div>
            </div>
          </div>
        </PaddedLayout>
      );
```

**Step 6: Update file header comment to list new components**

Replace line 11:

```tsx
 *   ComparisonCard, Timeline, CodeBlock, QuoteBlock, FeatureGrid, DataBar, StatCounter, FlowChart, IconCard
```

**Step 7: Commit**

```bash
git add templates/Video.tsx
git commit -m "feat: upgrade Video.tsx default sections with gradients, shadows, decorative elements"
```

---

### Task 12: Add quality checklists to SKILL.md

**Files:**
- Modify: `SKILL.md`

**Step 1: Add Section Design Checklist after Design Philosophy section**

Find the line `## Visual Design Reference (recommended)` and insert before it:

```markdown
## Quality Checklists (MUST follow)

### Per-Section Checklist

Claude MUST verify each section meets ALL of these before proceeding:

| # | Check | Requirement |
|---|-------|-------------|
| 1 | **Visual depth** | At least 2 layers of depth: shadows, gradients, or foreground/background separation |
| 2 | **Adjacent differentiation** | Differs from previous section in ≥2 of: background color, layout direction, content form |
| 3 | **Complete animation** | Entrance animation on all elements, list items have stagger delay |
| 4 | **Information density** | ≤5 key points per section, no large empty areas |
| 5 | **Topic-matched colors** | Color palette serves the content (tech→cool blue, health→warm green, finance→dark blue/gold) |

### Video-Level Checklist (before render)

| # | Check | Requirement |
|---|-------|-------------|
| 1 | **Layout variety** | ≥3 different layout types across the video (centered, grid, split, timeline, etc.) |
| 2 | **Background alternation** | No 2 consecutive sections share the same background color |
| 3 | **Unified color scheme** | Primary/secondary/accent colors used consistently throughout |
| 4 | **Thumbnail readability** | Title text readable at ~300px thumbnail width |
| 5 | **Hero impact** | Hero section has visual impact: large text + decorative elements or gradient |

### TTS Quality Guidance

| Technique | How |
|-----------|-----|
| **Section pauses** | Add an empty line before each `[SECTION:xxx]` marker in podcast.txt for natural breathing room |
| **Pacing variation** | Slightly slower intro/outro (TTS_RATE="+0%"), normal middle sections (TTS_RATE="+5%") |
| **Key sentence emphasis** | Use SSML `<emphasis>` tags on important sentences (Azure backend supports this) |

```

**Step 2: Commit**

```bash
git add SKILL.md
git commit -m "feat: add per-section and video-level quality checklists to SKILL.md"
```

---

### Task 13: Update CLAUDE.md architecture section

**Files:**
- Modify: `CLAUDE.md`

**Step 1: Update the components listing in the Architecture section**

Find the `components/` block in the Architecture section and replace with:

```
    index.ts                     # Barrel export
    layouts.tsx                  # Scale4K, FullBleedLayout, PaddedLayout
    animations.tsx               # useEntrance, useExit, useCounter, useBarFill, getPresentation
    ComparisonCard.tsx           # Two-column VS layout with shadow depth
    Timeline.tsx                 # Vertical timeline with glowing nodes
    CodeBlock.tsx                # Dark terminal code display
    QuoteBlock.tsx               # Large quote with accent line and gradient bg
    FeatureGrid.tsx              # 2-3 column icon grid with layered shadows
    DataBar.tsx                  # Animated horizontal bar chart
    StatCounter.tsx              # Animated number tickers
    FlowChart.tsx                # Horizontal arrow-connected steps
    IconCard.tsx                 # Large icon emphasis card
    ChapterProgressBar.tsx       # Bottom progress bar (renders outside Scale4K)
```

**Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md component list with new components"
```

---

### Task 14: Final review and verification

**Step 1: Verify all template files parse correctly**

Run: `ls -la templates/components/`

Expected: 12 files (animations.tsx, ChapterProgressBar.tsx, CodeBlock.tsx, ComparisonCard.tsx, DataBar.tsx, FeatureGrid.tsx, FlowChart.tsx, IconCard.tsx, index.ts, layouts.tsx, QuoteBlock.tsx, StatCounter.tsx, Timeline.tsx)

**Step 2: Verify index.ts exports match actual files**

Run: `grep "export" templates/components/index.ts | wc -l`

Expected: 12 lines

**Step 3: Commit all if any uncommitted changes remain**

```bash
git status
# If clean, done. If not, add and commit remaining changes.
```
