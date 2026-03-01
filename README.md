# Video Podcast Maker

[中文文档](README_CN.md)

Automated pipeline to create professional video podcasts from a topic. **Optimized for Bilibili (B站)**. Combines research, script generation, Microsoft Azure TTS, Remotion video rendering, and FFmpeg audio mixing.

> **No coding required!** Just describe your topic in plain language - Claude guides you through each step interactively. You make creative decisions, Claude handles all the technical details. Creating your first video podcast is easier than you think.

## Features

- **Topic Research** - Web search and content gathering
- **Script Writing** - Structured narration with section markers
- **Azure TTS** - High-quality Chinese/English text-to-speech
- **Remotion Video** - React-based video composition with animations
- **Visual Style Editing** - Adjust colors, fonts, and layout in Remotion Studio UI
- **Real-time Preview** - Remotion Studio for instant debugging before render
- **Auto Timing** - Audio-video sync via `timing.json`
- **BGM Mixing** - Background music overlay with FFmpeg
- **Subtitle Burning** - Optional SRT subtitle embedding
- **4K Output** - 3840x2160 resolution for crisp uploads
- **Chapter Progress Bar** - Visual timeline showing current section during playback
- **Bilingual TTS** - Chinese/English mixed narration with Azure Speech
- **Pronunciation Correction** - Built-in polyphone dictionary + custom phoneme support
- **Bilibili Templates** - Ready-to-use Remotion templates (`Video.tsx`, `Root.tsx`, `Thumbnail.tsx`, `podcast.txt`) for quick project scaffolding

### Bilibili Optimizations

- **Script Structure** - Welcome intro + call-to-action outro (一键三连)
- **Chapter Timestamps** - Auto-generated `MM:SS` format for B站 chapters
- **Thumbnail Generation** - AI (imagen/imagenty) or Remotion, auto-generates 16:9 + 4:3 versions
- **Visual Style** - Bold text, minimal whitespace, high information density
- **Publish Info** - Title formulas, tag strategies, description templates

## Workflow

![Workflow](assets/workflow.png)

## Related Skills

This skill depends on **remotion-best-practices** and works alongside other optional skills:

- **remotion-best-practices** - Official Remotion best practices (required, provides core Remotion patterns and guidelines)
- **find-skills** - Official skill discovery tool (required, helps find and install additional skills)
- **ffmpeg** - Advanced audio/video processing (optional)
- **imagen / imagenty** - AI thumbnail generation (optional)


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
| **video-podcast-maker** | Claude Code skill | Workflow orchestration (this skill) |

```bash
# Step 1: Create a new Remotion project (base framework)
npx create-video@latest my-video-project
cd my-video-project
npm i  # Install Remotion dependencies

# Step 2: Verify installation
npx remotion studio  # Should open browser preview
```

If you already have a Remotion project:

```bash
cd your-existing-project
npm install remotion @remotion/cli @remotion/player zod
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
| [SKILL.md](SKILL.md) | Complete 14-step workflow with pronunciation correction |
## Quick Start

### Usage

This skill is designed for use with [Claude Code](https://claude.ai/claude-code) or [Opencode](https://github.com/opencode-ai/opencode). Simply tell Claude:

> "Create a video podcast about [your topic]"

Claude will guide you through the entire workflow automatically.
Claude will guide you through the entire workflow automatically.
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

Included tracks in `assets/`:
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
