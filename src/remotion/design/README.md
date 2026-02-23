# Design System

Components from [remotion-design-master](https://github.com/Agents365-ai/remotion-design-master).

## Setup

```bash
npm run setup
```

This script will:
1. Clone from GitHub if not available locally
2. Copy design components to this folder

## Usage

```tsx
import { FullBleed, ContentArea, FadeIn, Title } from './design'
import { minimalWhite } from './design/themes'
```

## Components

| Category | Components |
|----------|------------|
| Layout | FullBleed, ContentArea, CoverMedia, DualLayerMedia |
| Animation | FadeIn, SpringPop, SlideIn, Typewriter |
| Typography | Title, Text, Caption, Code, Quote |
| Data | DataDisplay, AnimatedCounter, ProgressBar |
| Navigation | ChapterProgressBar, SectionIndicator |
| Themes | minimalWhite, darkTech, gradientVibrant |
