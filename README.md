# Video Podcast Maker

[中文文档](README_CN.md)

Automated pipeline to create professional video podcasts from a topic. **Optimized for Bilibili (B站)**. Combines research, script generation, Microsoft Azure TTS, Remotion video rendering, and FFmpeg audio mixing.

> **No coding required!** Just describe your topic in plain language - Claude guides you through each step interactively. You make creative decisions, Claude handles all the technical details. Creating your first video podcast is easier than you think.

## Features

- **Topic Research** - Web search and content gathering
- **Script Writing** - Structured narration with section markers
- **Azure TTS** - High-quality Chinese/English text-to-speech
- **Remotion Video** - React-based video composition with animations
- **Design System** - Powered by [remotion-design-master](https://github.com/Agents365-ai/remotion-design-master) for professional layouts and components
- **Visual Style Editing** - Adjust colors, fonts, and layout in Remotion Studio UI
- **Real-time Preview** - Remotion Studio for instant debugging before render
- **Auto Timing** - Audio-video sync via `timing.json`
- **BGM Mixing** - Background music overlay with FFmpeg
- **Subtitle Burning** - Optional SRT subtitle embedding
- **4K Output** - 3840x2160 resolution for crisp uploads
- **Chapter Progress Bar** - Visual timeline showing current section during playback

### Bilibili Optimizations

- **Script Structure** - Welcome intro + call-to-action outro (一键三连)
- **Chapter Timestamps** - Auto-generated `MM:SS` format for B站 chapters
- **Thumbnail Generation** - AI (imagen/imagenty) or Remotion, auto-generates 16:9 + 4:3 versions
- **Visual Style** - Bold text, minimal whitespace, high information density
- **Publish Info** - Title formulas, tag strategies, description templates

### Design System: remotion-design-master

This skill utilizes **[remotion-design-master](https://github.com/Agents365-ai/remotion-design-master)** for all Remotion components and visual design.

```bash
npm run setup  # Auto-clones from GitHub and installs design components
```

**Core Principle:** "Fill the screen, no empty space" - maximize screen usage for visual impact.

| Element | Size | Notes |
|---------|------|-------|
| Content width | ≥85% screen | Don't shrink to center |
| Main title | 80-100px | Bold, attention-grabbing |
| Data numbers | 64-140px | Data as hero |

**Components:**

| Component | Purpose |
|-----------|---------|
| `<FullBleed>` | Root container with `inset: 0` |
| `<ContentArea>` | Content area, 85%-95% width |
| `<FadeIn>` | Fade + slide up animation |
| `<ChapterProgressBar>` | Video chapter indicator |

See [remotion-design-master](https://github.com/Agents365-ai/remotion-design-master) for full documentation.

## Workflow

![Workflow](docs/workflow.png)

## Related Skills

This skill is part of a layered architecture with other Remotion-related skills:

```
┌─────────────────────────────────────────────────────────────────┐
│                    video-podcast-maker                          │
│         (Full workflow: Topic → Research → Script → TTS → Video)│
│                                                                 │
│  ┌─────────────────────┐    ┌─────────────────────────────┐    │
│  │ remotion-design-    │    │   remotion-best-practices   │    │
│  │ master              │    │                             │    │
│  │ (UI Component Lib)  │    │   (Remotion Framework)      │    │
│  │                     │    │                             │    │
│  │ • ChapterProgressBar│    │   • Animation API           │    │
│  │ • FadeIn, SlideIn   │    │   • Composition structure   │    │
│  │ • FullBleed         │    │   • Audio handling          │    │
│  │ • Title, ContentArea│    │   • Subtitle rendering      │    │
│  │ • Theme system      │    │   • FFmpeg integration      │    │
│  └─────────────────────┘    └─────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

| Skill | Layer | Purpose |
|-------|-------|---------|
| **remotion-best-practices** | Foundation | General Remotion framework knowledge (API, animations, audio, subtitles) |
| **remotion-design-master** | UI Layer | Reusable component library (progress bar, animations, layouts, themes) |
| **video-podcast-maker** | Application | Complete workflow that uses both skills above to generate B站 video podcasts |

**Dependency:** When creating video components in Step 8, this skill **requires** components from `remotion-design-master`.

## Requirements

### System Requirements

| Software | Version | Purpose |
|----------|---------|---------|
| **macOS / Linux** | - | Tested on macOS, Linux compatible |
| **Python** | 3.8+ | TTS script, automation |
| **Node.js** | 18+ | Remotion video rendering |
| **FFmpeg** | 4.0+ | Audio/video processing |

### Installation

```bash
# macOS
brew install ffmpeg node python3

# Ubuntu/Debian
sudo apt install ffmpeg nodejs python3 python3-pip

# Python dependencies
pip install azure-cognitiveservices-speech requests
```

### Project Setup (Required)

> **Important:** This skill requires a Remotion project as the foundation.

**Understanding the components:**

| Component | Source | Purpose |
|-----------|--------|---------|
| **Remotion Project** | `npx create-video` | Base framework with `src/`, `public/`, `package.json` |
| **remotion-design-master** | Claude Code skill | Design components (FullBleed, FadeIn, etc.) copied into your project |
| **video-podcast-maker** | Claude Code skill | Workflow orchestration (this skill) |

```bash
# Step 1: Create a new Remotion project (base framework)
npx create-video@latest my-video-project
cd my-video-project

# Step 2: Install design system from remotion-design-master (components)
mkdir -p src/remotion/design
cp -r ~/.claude/skills/remotion-design-master/src/* src/remotion/design/

# Step 3: Verify installation
npx remotion studio  # Should open browser preview
```

If you already have a Remotion project:

```bash
cd your-existing-project
npm install remotion @remotion/cli @remotion/player zod

# Install design system
mkdir -p src/remotion/design
cp -r ~/.claude/skills/remotion-design-master/src/* src/remotion/design/
```

### API Keys Required

| Service | Purpose | Get Key |
|---------|---------|---------|
| **Azure Speech** | TTS audio generation (required) | [Azure Portal](https://portal.azure.com/) → Speech Services |
| **Google Gemini** | AI thumbnail generation (optional) | [AI Studio](https://aistudio.google.com/) |
| **Aliyun Dashscope** | AI thumbnail - Chinese optimized (optional) | [Aliyun Bailian](https://bailian.console.aliyun.com/) |

### Environment Variables

Add to `~/.zshrc` or `~/.bashrc`:

```bash
# Azure TTS (required)
export AZURE_SPEECH_KEY="your-azure-speech-key"
export AZURE_SPEECH_REGION="eastasia"

# Optional: Google Gemini for AI thumbnails
export GEMINI_API_KEY="your-gemini-api-key"

# Optional: Aliyun for AI thumbnails (Chinese optimized)
export DASHSCOPE_API_KEY="your-dashscope-api-key"
```

Then reload: `source ~/.zshrc`

## Documentation

| Document | Description |
|----------|-------------|
| [Quick Start](docs/QUICKSTART.md) | 5-minute guide to get started |
| [SKILL.md](SKILL.md) | Complete 14-step workflow |
| [remotion-design-master](https://github.com/Agents365-ai/remotion-design-master) | Design system, components, hard constraints |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Error diagnosis and fixes |
| [Media Assets](docs/MEDIA_ASSETS.md) | Asset sources and naming |

## Quick Start

### Usage

This skill is designed for use with [Claude Code](https://claude.ai/claude-code) or [Opencode](https://github.com/opencode-ai/opencode). Simply tell Claude:

> "Create a video podcast about [your topic]"

Claude will guide you through the entire workflow automatically.

For manual setup or customization, see [docs/QUICKSTART.md](docs/QUICKSTART.md).

### Preview & Visual Editing with Remotion Studio

Before rendering the final video, use Remotion Studio to preview and visually edit styles:

```bash
npx remotion studio src/remotion/index.ts
```

This opens a browser-based editor where you can:
- **Visual Style Editing** - Adjust colors, fonts, and sizes in the right panel
- Scrub through the timeline frame-by-frame
- See live updates as you edit components
- Debug timing and animations instantly

#### Editable Properties

| Category | Properties |
|----------|-----------|
| **Colors** | Primary color, background, text color, accent |
| **Typography** | Title size (60-120), subtitle size, body size |
| **Progress Bar** | Show/hide, height, font size, active color |
| **Audio** | BGM volume (0-0.3) |
| **Animation** | Enable/disable entrance animations |

```
┌─────────────────────────────────────────────────────────────────┐
│  Remotion Studio                                                │
├──────────────────────────────────┬──────────────────────────────┤
│                                  │  Props Panel                 │
│                                  │  ─────────────────────────── │
│     Video Preview                │  primaryColor    [#4f6ef7]   │
│     (Real-time)                  │  backgroundColor [#ffffff]   │
│                                  │  titleSize       [====80===] │
│     ┌─────────────────────┐      │  showProgressBar [✓]         │
│     │   Your Video Here   │      │  progressBarHeight [==130==] │
│     │                     │      │  bgmVolume       [=0.05====] │
│     └─────────────────────┘      │  enableAnimations [✓]        │
│                                  │                              │
│  ◀──────────●──────────────▶     │  [Render Video]              │
│  Timeline                        │                              │
└──────────────────────────────────┴──────────────────────────────┘
```

## Output Structure

```
videos/{video-name}/
├── topic_definition.md      # Topic direction
├── topic_research.md        # Research notes
├── podcast.txt              # Narration script
├── podcast_audio.wav        # TTS audio
├── podcast_audio.srt        # Subtitles
├── timing.json              # Section timing for sync
├── thumbnail_*.png          # Video thumbnails
├── publish_info.md          # Title, tags, description
├── part_*.wav               # TTS segments (temp, cleanup via Step 14)
├── output.mp4               # Raw render (temp)
├── video_with_bgm.mp4       # With BGM (temp)
└── final_video.mp4          # Final output
```

## Background Music

Included tracks in `music/`:
- `perfect-beauty-191271.mp3` - Upbeat, positive
- `snow-stevekaldes-piano-397491.mp3` - Calm piano

## License

MIT

## Support

If this project helps you, consider supporting the author:

<table>
  <tr>
    <td align="center">
      <img src="https://raw.githubusercontent.com/Agents365-ai/images_payment/main/qrcode/wechat-pay.png" width="180" alt="WeChat Pay">
      <br>
      <b>WeChat Pay</b>
    </td>
    <td align="center">
      <img src="https://raw.githubusercontent.com/Agents365-ai/images_payment/main/qrcode/alipay.png" width="180" alt="Alipay">
      <br>
      <b>Alipay</b>
    </td>
    <td align="center">
      <img src="https://raw.githubusercontent.com/Agents365-ai/images_payment/main/qrcode/buymeacoffee.png" width="180" alt="Buy Me a Coffee">
      <br>
      <b>Buy Me a Coffee</b>
    </td>
  </tr>
</table>

## Author

**Agents365-ai**

- Bilibili: https://space.bilibili.com/441831884
- GitHub: https://github.com/Agents365-ai
