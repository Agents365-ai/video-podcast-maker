# Design System

This folder contains components from `remotion-design-master`.

## Setup

Run the setup script to copy the design system:

```bash
./scripts/setup-design.sh
```

Or manually copy:

```bash
cp -r ~/.claude/skills/remotion-design-master/src/* src/remotion/design/
```

## Usage

After setup, import components:

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
