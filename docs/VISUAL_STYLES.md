# Visual Styles Reference

Detailed visual style configurations for Video Podcast Maker.

## Style Selection Guide

| Style | Use Case | Characteristics |
|-------|----------|-----------------|
| **Minimal White (Default)** | Product intros, tutorials, comparisons | Pure white background, large text, high contrast |
| **Dark Tech** | AI/tech topics, night viewing | Dark background, neon accents, glow effects |
| **Gradient Vibrant** | Creative content, branding | Soft gradient backgrounds, rich colors |

**Select style in Step 0 (Topic Definition)** or default to Minimal White.

---

## Minimal White (Default)

> **"Less is more"** - Pure white background, large titles, minimal layout, content is the design.

### Color Palette

```tsx
const colors = {
  bg: '#fff',                          // Pure white background
  text: '#1a1a1a',                     // Dark gray main text
  textMuted: 'rgba(0,0,0,0.5)',        // Gray secondary text
  accent: '#2563eb',                   // Blue accent
  accentGreen: '#059669',              // Green (positive data)
  accentRed: '#dc2626',                // Red (negative/warning)
  accentOrange: '#ea580c',             // Orange (neutral accent)
}

const font = '-apple-system, "SF Pro Display", "Noto Sans SC", "Helvetica Neue", sans-serif'
```

### Card Component

```tsx
const Card = ({ children }) => (
  <div style={{
    background: 'rgba(0,0,0,0.03)',
    border: '1px solid rgba(0,0,0,0.06)',
    borderRadius: 24, padding: '36px 56px',
  }}>{children}</div>
)
```

### FadeIn Animation

```tsx
const FadeIn = ({ children, delay = 0, y = 30, dur = 25 }) => {
  const frame = useCurrentFrame()
  const progress = interpolate(frame - delay, [0, dur], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  })
  return <div style={{ opacity: progress, transform: `translateY(${interpolate(progress, [0,1], [y,0])}px)` }}>{children}</div>
}
```

### Design Specs

| Element | Spec | Notes |
|---------|------|-------|
| **Background** | Pure white `#fff` | No gradients, clean |
| **Page Margin** | 30-50px | Minimal margins, edge content |
| **Element Gap** | 24-40px | Compact, no large gaps |
| **Main Title** | 80-100px, fontWeight 800 | Bold, visual anchor |
| **Subtitle** | 48-64px, fontWeight 700 | Clear but secondary |
| **Body Text** | 32-44px, fontWeight 500-600 | Readable |
| **Data Numbers** | 64-80px, fontWeight 800 | Data as hero |
| **Large Data** | 96-140px | Single key metric |
| **Emoji/Icons** | 56-80px (list), 140-160px (focus) | Large and clear |
| **Card Width** | 80-95% of screen | Fill it up |
| **Progress Bar** | 40-56px height | Bold |
| **Border Radius** | 16-24px | Modern feel |
| **Accents** | Blue `#2563eb`, Green `#059669`, Red `#dc2626` | High contrast |
| **Animation** | FadeIn + translateY | Simple, not flashy |

### Font Size Quick Reference

| Scene | Main Title | Subtitle | Body | Data |
|-------|------------|----------|------|------|
| Hero | 88-100px | 48-56px | - | - |
| Feature List | 72-80px | 40-48px | 28-36px | - |
| Data Comparison | 64-72px | - | 32px | 44-64px |
| Summary | 72-80px | 40-48px | 32-40px | - |
| Outro (Triple) | 80px | - | 36-44px | - |

---

## Dark Tech (Alternative)

> **Use Case:** AI/tech topics, night viewing, cyberpunk style

### Color Palette

```tsx
const darkColors = {
  bg: '#0a0a0f',                         // Deep black background
  bgCard: 'rgba(255,255,255,0.05)',      // Semi-transparent card
  text: '#ffffff',                        // White main text
  textMuted: 'rgba(255,255,255,0.6)',    // Gray secondary text
  accent: '#00d4ff',                      // Neon blue
  accentPurple: '#a855f7',               // Neon purple
  accentGreen: '#22c55e',                // Neon green
  glow: '0 0 30px rgba(0,212,255,0.3)',  // Glow effect
}
```

### Dark Card Component

```tsx
const DarkCard = ({ children }) => (
  <div style={{
    background: 'rgba(255,255,255,0.05)',
    border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: 20,
    padding: '32px 48px',
    backdropFilter: 'blur(10px)',
    boxShadow: '0 0 30px rgba(0,212,255,0.1)',
  }}>{children}</div>
)
```

### Design Specs

| Element | Spec | Notes |
|---------|------|-------|
| **Background** | `#0a0a0f` or dark gradient | Pure black or deep blue-black |
| **Text** | White `#fff` | High contrast |
| **Accents** | Neon blue `#00d4ff`, neon purple `#a855f7` | Glow effects |
| **Cards** | Semi-transparent + `backdropFilter: blur` | Frosted glass effect |
| **Subtitles** | White + dark stroke | Ensure readability |

---

## Gradient Vibrant (Alternative)

> **Use Case:** Creative content, entertainment, brand promotion

### Color Palette

```tsx
const gradientColors = {
  bgGradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', // Purple-blue
  bgWarm: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',     // Pink-red
  bgCool: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',     // Blue-cyan
  text: '#ffffff',
  textShadow: '0 2px 10px rgba(0,0,0,0.3)',
}
```

### Gradient Background Component

```tsx
const GradientBg = ({ gradient = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }) => (
  <div style={{
    position: 'absolute',
    inset: 0,
    background: gradient,
  }} />
)
```

### Design Specs

| Element | Spec | Notes |
|---------|------|-------|
| **Background** | 135 degree two-color gradient | Soft transition |
| **Text** | White + shadow | `textShadow` for readability |
| **Cards** | White semi-transparent `rgba(255,255,255,0.9)` | Content highlight |
| **Accents** | Gold `#ffd700`, white | Contrast with gradient |

---

## Switching Styles

Modify `tokens.colors` in `FullBleedLayout.tsx`, or create multiple color sets:

```tsx
// Import different styles
import { tokens } from './FullBleedLayout'  // Minimal White (default)
// import { darkTokens as tokens } from './FullBleedLayout'  // Dark Tech
// import { gradientTokens as tokens } from './FullBleedLayout'  // Gradient Vibrant

// Or specify directly in component
<FullBleed background={tokens.colors.bg}>  // Default white
<FullBleed background="#0a0a0f">           // Dark
<FullBleed background="linear-gradient(135deg, #667eea 0%, #764ba2 100%)">  // Gradient
```
