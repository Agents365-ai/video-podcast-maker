# Video Podcast Maker

[中文文档](README_CN.md)

Automated pipeline to create professional video podcasts from a topic. **Optimized for Bilibili (B站)**. Combines research, script generation, Microsoft Azure TTS, Remotion video rendering, and FFmpeg audio mixing.

## Features

- **Topic Research** - Web search and content gathering
- **Script Writing** - Structured narration with section markers
- **Azure TTS** - High-quality Chinese/English text-to-speech
- **Remotion Video** - React-based video composition with animations
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

## Workflow

```
User provides topic
       ↓
Define topic direction (brainstorm)
       ↓
Research & collect materials
       ↓
Design video sections
       ↓
Write narration script
       ↓
Generate publish info (title/tags/summary)
       ↓
Generate video thumbnail
       ↓
Generate TTS audio (Azure)
       ↓
Create Remotion composition
       ↓
Render video frames
       ↓
Mix: video + audio + BGM
       ↓
Add subtitles (optional)
       ↓
Verify output (resolution, duration, encoding)
       ↓
Cleanup temp files (user confirmation)
       ↓
Output final MP4
```

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

# Node.js dependencies (run in project directory)
npm install remotion @remotion/cli @remotion/player
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
| [Components](docs/COMPONENTS.md) | Remotion component reference |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Error diagnosis and fixes |
| [Visual Styles](docs/VISUAL_STYLES.md) | Style configurations |
| [Media Assets](docs/MEDIA_ASSETS.md) | Asset sources and naming |

## Quick Start

### Usage

This skill is designed for use with [Claude Code](https://claude.ai/claude-code) or [Opencode](https://github.com/opencode-ai/opencode). Simply tell Claude:

> "Create a video podcast about [your topic]"

Claude will guide you through the entire workflow automatically.

For manual setup or customization, see [docs/QUICKSTART.md](docs/QUICKSTART.md).

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

## Design Principles

**"Fill the screen, no empty space"** - Text and UI should maximize screen usage for visual impact.

| Element | Size | Notes |
|---------|------|-------|
| Content width | ≥85% screen | Don't shrink to center |
| Page margin | 30-50px | Minimal margins |
| Main title | 80-100px | Bold, attention-grabbing |
| Subtitle | 48-64px | Clear and visible |
| Data numbers | 64-140px | Data as hero |
| Card width | 900-1100px (1080p) | Fill the space |

### FullBleed Layout System

Pre-built components that enforce full-screen layouts:

```bash
cp ~/.claude/skills/video-podcast-maker/FullBleedLayout.tsx src/remotion/
```

| Component | Purpose |
|-----------|---------|
| `<FullBleed>` | Root container with `inset: 0` |
| `<ContentArea>` | Content area, 85%-95% width |
| `<CoverMedia>` | Media with `objectFit: cover` |
| `<DualLayerMedia>` | Blur background + clear foreground |

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
      <img src="images/wechat-pay.png" width="180" alt="WeChat Pay">
      <br>
      <b>WeChat Pay</b>
    </td>
    <td align="center">
      <img src="images/alipay.png" width="180" alt="Alipay">
      <br>
      <b>Alipay</b>
    </td>
  </tr>
</table>

## Author

**探索未至之境**

- Bilibili: https://space.bilibili.com/441831884
- GitHub: https://github.com/niehu2018
