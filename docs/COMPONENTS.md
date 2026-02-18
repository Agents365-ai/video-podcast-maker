# Remotion Components Reference

Pre-built components for video-podcast-maker. All components enforce the "fill the screen" design principle.

## Quick Start

```tsx
import {
  // Layout
  FullBleed, ContentArea, CoverMedia, DualLayerMedia,
  // Animation
  FadeIn, SpringPop, AnimatedCounter,
  // Typography
  Title, DataDisplay,
  // Tokens
  tokens, darkTokens, gradientTokens, font,
  // Debug
  DebugOverlay,
} from './FullBleedLayout'
```

---

## 1. Layout Components

### FullBleed

Root container with hard constraints. **Every section MUST use this.**

```tsx
import { FullBleed } from './FullBleedLayout'
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `children` | ReactNode | required | Content |
| `background` | string | `tokens.colors.bg` | Background color/gradient |
| `style` | CSSProperties | - | Additional styles |

**Constraints enforced:**
- `position: absolute; inset: 0`
- `overflow: hidden`
- `padding: 0; margin: 0`

**Usage:**
```tsx
const HeroSection = () => (
  <FullBleed background="#fff">
    <ContentArea>
      <Title>Hero Title</Title>
    </ContentArea>
  </FullBleed>
)

// With gradient background
<FullBleed background="linear-gradient(135deg, #667eea 0%, #764ba2 100%)">
  ...
</FullBleed>
```

**Visual:** Full-screen container, content fills entire frame with no margins.

---

### ContentArea

Content wrapper with controlled width. Ensures content fills 85-95% of screen width.

```tsx
import { ContentArea } from './FullBleedLayout'
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `children` | ReactNode | required | Content |
| `minWidth` | number | `0.85` | Min width (0-1 = % of screen) |
| `maxWidth` | number | `0.95` | Max width (0-1 = % of screen) |
| `padding` | number | `40` | Inner padding (px) |
| `verticalAlign` | `'top' \| 'center' \| 'bottom'` | `'center'` | Vertical alignment |
| `style` | CSSProperties | - | Additional styles |

**Constraints enforced:**
- Width: 85%-95% of screen
- Bottom padding: auto-adds 100px for subtitle safe area
- Horizontally centered

**Usage:**
```tsx
// Default: centered, 85-95% width
<ContentArea>
  <Title>Content Here</Title>
</ContentArea>

// Top-aligned, custom width
<ContentArea verticalAlign="top" minWidth={0.9} maxWidth={0.98}>
  <Title>Full-width Content</Title>
</ContentArea>
```

**Visual:** Content block that fills most of the screen horizontally, with small margins.

---

### CoverMedia

Full-screen media (image or video) with object-fit: cover.

```tsx
import { CoverMedia } from './FullBleedLayout'
import { staticFile } from 'remotion'
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `src` | string | required | Media source URL |
| `type` | `'image' \| 'video'` | `'image'` | Media type |
| `style` | CSSProperties | - | Additional styles |

**Constraints enforced:**
- `width: 100%; height: 100%`
- `objectFit: cover` (crops to fill)
- `position: absolute; inset: 0`

**Usage:**
```tsx
// Full-screen image
<FullBleed>
  <CoverMedia src={staticFile('media/project/hero_1.png')} />
  <ContentArea>
    <Title style={{ color: '#fff' }}>Overlay Text</Title>
  </ContentArea>
</FullBleed>

// Full-screen video (muted)
<FullBleed>
  <CoverMedia src={staticFile('media/project/demo_1.mp4')} type="video" />
</FullBleed>
```

**Visual:** Image/video fills entire frame, cropped if aspect ratio doesn't match.

---

### DualLayerMedia

For non-16:9 content (screenshots, portraits, square images). Uses blurred background + clear foreground.

```tsx
import { DualLayerMedia } from './FullBleedLayout'
import { staticFile } from 'remotion'
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `src` | string | required | Media source URL |
| `type` | `'image' \| 'video'` | `'image'` | Media type |
| `foregroundFit` | `'contain' \| 'cover'` | `'contain'` | Foreground fit mode |
| `blurAmount` | number | `30` | Background blur (px) |
| `overlayOpacity` | number | `0.3` | Overlay darkness (0-1) |

**Structure:**
1. Background: Media scaled 140% + blurred (cover)
2. Overlay: Semi-transparent white for readability
3. Foreground: Clear media (contain)

**Usage:**
```tsx
// Screenshot (non-16:9)
<DualLayerMedia
  src={staticFile('media/project/demo_screenshot.png')}
  foregroundFit="contain"
  blurAmount={30}
/>

// Portrait image
<DualLayerMedia
  src={staticFile('media/project/portrait.jpg')}
  overlayOpacity={0.4}
/>
```

**Visual:** No black bars. Blurred version of image fills background, crisp image centered on top.

```
+--------------------------------------------------+
|  [Blurred background - fills entire frame]       |
|    +----------------------------------------+    |
|    |  [Clear foreground - actual content]   |    |
|    |                                        |    |
|    |          Portrait/Screenshot           |    |
|    |                                        |    |
|    +----------------------------------------+    |
+--------------------------------------------------+
```

---

### KenBurnsMedia

Media with slow zoom animation (Ken Burns effect). Makes static images feel alive.

```tsx
import { KenBurnsMedia } from './FullBleedLayout'
import { staticFile } from 'remotion'
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `src` | string | required | Media source URL |
| `type` | `'image' \| 'video'` | `'image'` | Media type |
| `config.startScale` | number | `1.0` | Starting scale |
| `config.endScale` | number | `1.15` | Ending scale |
| `config.focus` | string | `'center'` | Zoom focus point |

**Focus options:** `'center'`, `'top'`, `'bottom'`, `'left'`, `'right'`

**Usage:**
```tsx
// Default: zoom from 1.0x to 1.15x, center focus
<KenBurnsMedia src={staticFile('media/project/landscape.jpg')} />

// Zoom into top of image
<KenBurnsMedia
  src={staticFile('media/project/cityscape.jpg')}
  config={{ startScale: 1.0, endScale: 1.3, focus: 'top' }}
/>

// Slow zoom out
<KenBurnsMedia
  src={staticFile('media/project/product.jpg')}
  config={{ startScale: 1.2, endScale: 1.0, focus: 'center' }}
/>
```

**Visual:** Image slowly zooms in (or out) over the duration of the sequence, adding subtle motion to static content.

---

## 2. Animation Components

### FadeIn

Fade + slide up animation.

```tsx
import { FadeIn } from './FullBleedLayout'
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `children` | ReactNode | required | Content to animate |
| `delay` | number | `0` | Delay in frames |
| `duration` | number | `25` | Animation duration in frames |
| `y` | number | `30` | Initial Y offset (px) |

**Usage:**
```tsx
// Basic fade in
<FadeIn>
  <Title>Hello World</Title>
</FadeIn>

// Staggered elements
<FadeIn delay={0}><Title>First</Title></FadeIn>
<FadeIn delay={15}><Title size="medium">Second</Title></FadeIn>
<FadeIn delay={30}><Title size="medium">Third</Title></FadeIn>
```

**Visual:** Element fades from transparent to opaque while sliding up 30px.

---

### SpringPop

Elastic bounce-in animation (scale from 0 to 1).

```tsx
import { SpringPop } from './FullBleedLayout'
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `children` | ReactNode | required | Content to animate |
| `delay` | number | `0` | Delay in frames |

**Usage:**
```tsx
// Pop in an icon or data point
<SpringPop>
  <div style={{ fontSize: 120 }}>42%</div>
</SpringPop>

// Delayed pop
<SpringPop delay={20}>
  <DataDisplay value="1,234" label="Users" />
</SpringPop>
```

**Visual:** Element scales from 0 to 1 with elastic overshoot (bouncy entrance).

---

### AnimatedCounter

Number counting animation (animates from 0 to target value).

```tsx
import { AnimatedCounter } from './FullBleedLayout'
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `value` | number | required | Target number |
| `delay` | number | `0` | Delay in frames |
| `duration` | number | `30` | Animation duration in frames |
| `prefix` | string | `''` | Text before number |
| `suffix` | string | `''` | Text after number |
| `style` | CSSProperties | - | Text styling |

**Usage:**
```tsx
// Basic counter
<AnimatedCounter value={1000} />
// Output: 0 → 1,000 (with comma formatting)

// With prefix/suffix
<AnimatedCounter
  value={99.9}
  prefix="$"
  suffix="M"
  style={{ fontSize: 80, fontWeight: 800, color: '#059669' }}
/>
// Output: $0 → $99M

// Delayed counter
<AnimatedCounter value={42} delay={15} suffix="%" />
```

**Visual:** Number counts up from 0 to the target value with easing.

---

### StaggerChildren (Pattern)

Sequential child animations (not a component, but a pattern using FadeIn with delays).

```tsx
// Stagger pattern: increment delay by 10-15 frames per item
const items = ['Feature 1', 'Feature 2', 'Feature 3', 'Feature 4']

{items.map((item, i) => (
  <FadeIn key={i} delay={i * 12}>
    <div style={{ fontSize: 40 }}>{item}</div>
  </FadeIn>
))}
```

**Visual:** Each item fades in sequentially, creating a cascade effect.

---

### SlideIn (Pattern)

Directional slide animation (pattern using FadeIn with custom y or transform).

```tsx
// Slide from left (using transform)
const SlideInLeft = ({ children, delay = 0 }) => {
  const frame = useCurrentFrame()
  const progress = interpolate(frame - delay, [0, 25], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  })
  return (
    <div style={{
      opacity: progress,
      transform: `translateX(${interpolate(progress, [0, 1], [-100, 0])}px)`,
    }}>
      {children}
    </div>
  )
}

// Slide from right
const SlideInRight = ({ children, delay = 0 }) => {
  const frame = useCurrentFrame()
  const progress = interpolate(frame - delay, [0, 25], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  })
  return (
    <div style={{
      opacity: progress,
      transform: `translateX(${interpolate(progress, [0, 1], [100, 0])}px)`,
    }}>
      {children}
    </div>
  )
}
```

---

## 3. Typography Components

### Title

Pre-styled title with size variants.

```tsx
import { Title, tokens } from './FullBleedLayout'
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `children` | ReactNode | required | Title text |
| `size` | `'hero' \| 'large' \| 'medium'` | `'large'` | Size variant |
| `color` | string | `tokens.colors.text` | Text color |
| `style` | CSSProperties | - | Additional styles |

**Size mapping:**
| Size | Font Size | Use Case |
|------|-----------|----------|
| `hero` | 100px | Opening screen, single big statement |
| `large` | 80px | Section titles |
| `medium` | 56px | Subtitles, secondary headings |

**Usage:**
```tsx
// Hero title
<Title size="hero">The Future of AI</Title>

// Section title with accent color
<Title color={tokens.colors.accent}>Key Features</Title>

// Subtitle
<Title size="medium" color={tokens.colors.textMuted}>
  Everything you need to know
</Title>
```

**Visual:** Bold, centered text with tight letter-spacing for impact.

---

### DataDisplay

Large numbers with optional label.

```tsx
import { DataDisplay, tokens } from './FullBleedLayout'
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `value` | string \| number | required | The number/data to display |
| `label` | string | - | Description below the number |
| `color` | string | `tokens.colors.accent` | Number color |
| `size` | `'large' \| 'medium'` | `'large'` | Size variant |

**Size mapping:**
| Size | Font Size |
|------|-----------|
| `large` | 120px |
| `medium` | 72px |

**Usage:**
```tsx
// Basic data display
<DataDisplay value="42%" label="Efficiency Gain" />

// Positive metric (green)
<DataDisplay
  value="+156%"
  label="Year over Year"
  color={tokens.colors.positive}
/>

// Negative metric (red)
<DataDisplay
  value="-23%"
  label="Cost Reduction"
  color={tokens.colors.negative}
/>

// Multiple data points in a row
<div style={{ display: 'flex', gap: 100, justifyContent: 'center' }}>
  <DataDisplay value="1.2M" label="Users" color={tokens.colors.accent} />
  <DataDisplay value="99.9%" label="Uptime" color={tokens.colors.positive} />
  <DataDisplay value="<50ms" label="Latency" color={tokens.colors.orange} />
</div>
```

**Visual:** Large, bold number (accent color) with small gray label underneath.

---

## 4. Section Templates

### HeroSection (Pattern)

Opening section template.

```tsx
const HeroSection = () => (
  <FullBleed background={tokens.colors.bg}>
    <ContentArea>
      <FadeIn>
        <Title size="hero">Main Title Here</Title>
      </FadeIn>
      <FadeIn delay={15}>
        <Title size="medium" color={tokens.colors.textMuted}>
          Subtitle or tagline
        </Title>
      </FadeIn>
    </ContentArea>
  </FullBleed>
)
```

**Visual:** Clean white background, large centered title with subtitle fading in.

---

### OutroSection (Pattern)

Bilibili ending with call-to-action.

```tsx
const OutroSection = () => (
  <FullBleed background={tokens.colors.bg}>
    <ContentArea>
      <FadeIn>
        <Title size="large">Thanks for Watching!</Title>
      </FadeIn>
      <FadeIn delay={15}>
        <div style={{
          display: 'flex',
          gap: 80,
          marginTop: 60,
          fontSize: 64,
        }}>
          <SpringPop delay={25}>
            <div style={{ textAlign: 'center' }}>
              <div>Like</div>
              <div style={{ fontSize: 32, color: tokens.colors.textMuted }}>Like</div>
            </div>
          </SpringPop>
          <SpringPop delay={35}>
            <div style={{ textAlign: 'center' }}>
              <div>Coin</div>
              <div style={{ fontSize: 32, color: tokens.colors.textMuted }}>Coin</div>
            </div>
          </SpringPop>
          <SpringPop delay={45}>
            <div style={{ textAlign: 'center' }}>
              <div>Favorite</div>
              <div style={{ fontSize: 32, color: tokens.colors.textMuted }}>Favorite</div>
            </div>
          </SpringPop>
        </div>
      </FadeIn>
    </ContentArea>
  </FullBleed>
)
```

**Visual:** Thank you message with animated icons popping in sequentially.

---

### ReferencesSection (Pattern)

Source links display.

```tsx
const ReferencesSection = () => (
  <FullBleed background={tokens.colors.bg}>
    <ContentArea>
      <FadeIn>
        <Title>References</Title>
      </FadeIn>
      <FadeIn delay={15}>
        <div style={{
          marginTop: 40,
          fontSize: 36,
          color: tokens.colors.textMuted,
          lineHeight: 2,
        }}>
          <div>Official documentation and technical blogs</div>
          <div>Links in description</div>
        </div>
      </FadeIn>
    </ContentArea>
  </FullBleed>
)
```

---

### MediaSection (Pattern)

Section with background media and text overlay.

```tsx
const MediaSection = () => (
  <FullBleed>
    <CoverMedia src={staticFile('media/project/feature_1.png')} />
    {/* Optional: dark overlay for readability */}
    <div style={{
      position: 'absolute',
      inset: 0,
      background: 'rgba(0,0,0,0.4)',
    }} />
    <ContentArea>
      <FadeIn>
        <Title style={{ color: '#fff' }}>Feature Highlight</Title>
      </FadeIn>
    </ContentArea>
  </FullBleed>
)
```

---

## 5. Background Effects

### PulsingGlow (Pattern)

Breathing glow effect.

```tsx
const PulsingGlow = () => {
  const frame = useCurrentFrame()
  const pulse = interpolate(
    Math.sin(frame * 0.1),
    [-1, 1],
    [0.3, 0.6]
  )

  return (
    <div style={{
      position: 'absolute',
      inset: 0,
      background: `radial-gradient(
        circle at 50% 50%,
        rgba(0, 212, 255, ${pulse}) 0%,
        transparent 60%
      )`,
    }} />
  )
}

// Usage
<FullBleed background="#0a0a0f">
  <PulsingGlow />
  <ContentArea>
    <Title style={{ color: '#fff' }}>Tech Title</Title>
  </ContentArea>
</FullBleed>
```

**Visual:** Soft, pulsing glow in the center of the screen.

---

### GradientShift (Pattern)

Animated gradient background.

```tsx
const GradientShift = () => {
  const frame = useCurrentFrame()
  const hue = interpolate(frame, [0, 150], [220, 280], {
    extrapolateRight: 'wrap',
  })

  return (
    <div style={{
      position: 'absolute',
      inset: 0,
      background: `linear-gradient(
        135deg,
        hsl(${hue}, 70%, 60%) 0%,
        hsl(${hue + 60}, 70%, 50%) 100%
      )`,
    }} />
  )
}

// Usage
<FullBleed>
  <GradientShift />
  <ContentArea>
    <Title style={{ color: '#fff' }}>Dynamic Background</Title>
  </ContentArea>
</FullBleed>
```

**Visual:** Gradient colors slowly shift over time.

---

## 6. Design Tokens

### Default Tokens (White Minimalist)

```tsx
import { tokens, font } from './FullBleedLayout'
```

```tsx
tokens = {
  colors: {
    bg: '#fff',                        // Background
    text: '#1a1a1a',                   // Primary text
    textMuted: 'rgba(0,0,0,0.5)',      // Secondary text
    accent: '#2563eb',                 // Blue accent
    positive: '#059669',               // Green (positive data)
    negative: '#dc2626',               // Red (negative data)
    orange: '#ea580c',                 // Orange accent
  },
  fontSize: {
    hero: 100,      // Hero titles
    title: 80,      // Section titles
    subtitle: 56,   // Subtitles
    body: 40,       // Body text
    caption: 32,    // Captions
    dataLarge: 120, // Large data numbers
    data: 72,       // Data numbers
  },
  spacing: {
    page: 40,       // Page margins
    section: 50,    // Between sections
    element: 30,    // Between elements
    tight: 16,      // Tight spacing
  },
  layout: {
    minContentWidth: 0.85,  // 85% screen width min
    maxContentWidth: 0.95,  // 95% screen width max
    cardWidth: 1000,        // Card width (1080p)
    subtitleMargin: 100,    // Bottom margin for subtitles
  },
}

font = '-apple-system, "SF Pro Display", "Noto Sans SC", "Helvetica Neue", sans-serif'
```

### Dark Tokens (Tech Style)

```tsx
import { darkTokens } from './FullBleedLayout'
```

```tsx
darkTokens = {
  colors: {
    bg: '#0a0a0f',
    bgCard: 'rgba(255,255,255,0.05)',
    text: '#ffffff',
    textMuted: 'rgba(255,255,255,0.6)',
    accent: '#00d4ff',      // Neon blue
    accentPurple: '#a855f7', // Neon purple
    positive: '#22c55e',
    negative: '#ef4444',
  },
  // fontSize, spacing, layout same as tokens
}
```

### Gradient Tokens (Vibrant Style)

```tsx
import { gradientTokens } from './FullBleedLayout'
```

```tsx
gradientTokens = {
  colors: {
    bg: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    bgWarm: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    bgCool: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    text: '#ffffff',
    textMuted: 'rgba(255,255,255,0.8)',
    accent: '#ffd700',
    positive: '#22c55e',
    negative: '#ef4444',
  },
}
```

---

## 7. Debug Overlay

Visual debugging helper for layout verification.

```tsx
import { DebugOverlay } from './FullBleedLayout'
```

**Props:**
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `show` | boolean | `false` | Enable/disable overlay |

**Usage:**
```tsx
// Add at the end of any section
<FullBleed>
  <ContentArea>
    <Title>Content</Title>
  </ContentArea>
  <DebugOverlay show={true} />  {/* Remove in production */}
</FullBleed>
```

**Visual markers:**
- Red border: Screen edges
- Blue dashed: 85% content area
- Pink area: Bottom 100px subtitle safe zone

---

## Complete Example

```tsx
import { AbsoluteFill, Sequence, staticFile } from 'remotion'
import {
  FullBleed, ContentArea, CoverMedia, DualLayerMedia, KenBurnsMedia,
  FadeIn, SpringPop, AnimatedCounter,
  Title, DataDisplay,
  tokens, font,
} from './FullBleedLayout'

const HeroSection = () => (
  <FullBleed background={tokens.colors.bg}>
    <ContentArea>
      <FadeIn>
        <Title size="hero" color={tokens.colors.accent}>
          The Ultimate Guide
        </Title>
      </FadeIn>
      <FadeIn delay={15}>
        <Title size="medium" color={tokens.colors.textMuted}>
          Everything You Need to Know
        </Title>
      </FadeIn>
    </ContentArea>
  </FullBleed>
)

const StatsSection = () => (
  <FullBleed>
    <ContentArea>
      <FadeIn>
        <Title>Key Metrics</Title>
      </FadeIn>
      <div style={{ display: 'flex', gap: 100, marginTop: 60 }}>
        <SpringPop delay={15}>
          <DataDisplay value={<AnimatedCounter value={1000000} delay={15} />} label="Users" />
        </SpringPop>
        <SpringPop delay={25}>
          <DataDisplay value="99.9%" label="Uptime" color={tokens.colors.positive} />
        </SpringPop>
        <SpringPop delay={35}>
          <DataDisplay value="<10ms" label="Latency" color={tokens.colors.orange} />
        </SpringPop>
      </div>
    </ContentArea>
  </FullBleed>
)

const ScreenshotSection = () => (
  <DualLayerMedia
    src={staticFile('media/project/demo_screenshot.png')}
    foregroundFit="contain"
    blurAmount={30}
  />
)

export const MyVideo = () => (
  <AbsoluteFill style={{ fontFamily: font }}>
    <Sequence from={0} durationInFrames={90}>
      <HeroSection />
    </Sequence>
    <Sequence from={90} durationInFrames={120}>
      <StatsSection />
    </Sequence>
    <Sequence from={210} durationInFrames={150}>
      <ScreenshotSection />
    </Sequence>
  </AbsoluteFill>
)
```

---

## 8. Chapter Progress Bar

### ChapterProgressBar

动态章节进度条，显示在视频底部，实时显示当前播放进度和章节。

```tsx
import { useCurrentFrame } from 'remotion'
```

**设计特点:**
- 白色简约风格，配合视频主题
- 圆角胶囊形状章节按钮
- 当前章节高亮（DeepSeek 蓝）
- 已播章节浅灰背景
- 底部蓝色进度条

**完整组件代码:**

```tsx
// 章节数据结构
const chapters = [
  { name: "hero", label: "开场", start_frame: 0, duration_frames: 532 },
  { name: "features", label: "功能介绍", start_frame: 532, duration_frames: 900 },
  // ... 其他章节
]
const TOTAL_FRAMES = 6008  // 总帧数

// 进度条组件
const ChapterProgressBar = () => {
  const frame = useCurrentFrame()
  const progress = frame / TOTAL_FRAMES

  return (
    <div style={{
      position: 'absolute', bottom: 0, left: 0, right: 0, height: 130,
      background: '#fff', borderTop: '1px solid #e5e7eb',
      display: 'flex', alignItems: 'center', padding: '0 50px', gap: 16,
      fontFamily: font,
    }}>
      {chapters.map((ch) => {
        const chStart = ch.start_frame / TOTAL_FRAMES
        const chEnd = (ch.start_frame + ch.duration_frames) / TOTAL_FRAMES
        const isActive = progress >= chStart && progress < chEnd
        const isPast = progress >= chEnd
        const chProgress = isActive ? (progress - chStart) / (chEnd - chStart) : isPast ? 1 : 0

        return (
          <div key={ch.name} style={{
            flex: ch.duration_frames,
            height: 80, borderRadius: 40, position: 'relative', overflow: 'hidden',
            background: isActive ? '#4f6ef7' : isPast ? '#f3f4f6' : '#f9fafb',
            border: isActive ? 'none' : '1px solid #e5e7eb',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            {isActive && (
              <div style={{
                position: 'absolute', left: 0, top: 0, bottom: 0,
                width: `${chProgress * 100}%`,
                background: 'rgba(255,255,255,0.25)',
                borderRadius: 40,
              }} />
            )}
            <span style={{
              position: 'relative', zIndex: 1,
              color: isActive ? '#fff' : isPast ? '#374151' : '#9ca3af',
              fontSize: 60, fontWeight: isActive ? 700 : 500,
              whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
              padding: '0 20px',
            }}>{ch.label}</span>
          </div>
        )
      })}
      {/* 底部总进度条 */}
      <div style={{
        position: 'absolute', bottom: 0, left: 0, right: 0, height: 4,
        background: '#e5e7eb',
      }}>
        <div style={{
          height: '100%', width: `${progress * 100}%`,
          background: '#4f6ef7',
        }} />
      </div>
    </div>
  )
}
```

**在主视频组件中使用:**

```tsx
export const MyVideo = () => (
  <AbsoluteFill style={{ background: '#fff' }}>
    <Audio src={staticFile('podcast_audio.wav')} />
    <AbsoluteFill style={{ transform: 'scale(2)', transformOrigin: 'top left', width: '50%', height: '50%' }}>
      {chapters.map(section => (
        <Sequence key={section.name} from={section.start_frame} durationInFrames={section.duration_frames}>
          <SectionComponent name={section.name} />
        </Sequence>
      ))}
    </AbsoluteFill>
    <ChapterProgressBar />  {/* 添加进度条 */}
  </AbsoluteFill>
)
```

**自定义配色:**

| 属性 | 默认值 | 说明 |
|------|--------|------|
| 背景色 | `#fff` | 进度条背景 |
| 边框色 | `#e5e7eb` | 顶部边框和胶囊边框 |
| 当前章节 | `#4f6ef7` | DeepSeek 蓝 |
| 已播章节 | `#f3f4f6` | 浅灰色 |
| 未播章节 | `#f9fafb` | 更浅的灰色 |
| 进度条高亮 | `#4f6ef7` | DeepSeek 蓝 |

---

## Checklist

Before rendering, verify:

- [ ] Root container uses `<FullBleed>` or `position: absolute; inset: 0`
- [ ] All Img/Video use `width: 100%; height: 100%`
- [ ] No `margin: auto` or `placeItems: center` on root containers
- [ ] Title font size >= 80px (hero/large)
- [ ] Page padding <= 50px
- [ ] Non-16:9 media uses `<DualLayerMedia>`
- [ ] Bottom 100px left clear for subtitles
