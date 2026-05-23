# Video Podcast Maker

[中文文档](README_CN.md)

Automated pipeline to create professional video podcasts from a topic. **Supports Bilibili, YouTube, Xiaohongshu, Douyin, and WeChat Channels** with multi-language output (zh-CN, en-US). Combines research, script generation, multi-engine TTS (Edge/Azure/Doubao/CosyVoice), Remotion video rendering, and FFmpeg audio mixing.

**Works with:** [Claude Code](https://claude.ai/code) · [OpenClaw](https://openclaw.ai/) (ClawHub) · [OpenCode](https://opencode.ai/) · [Codex](https://openai.com/index/introducing-codex/) — any coding agent that supports SKILL.md

**Publish to:** Bilibili · YouTube · Xiaohongshu · Douyin · WeChat Channels

> **No coding required!** Just describe your topic in plain language — the coding agent guides you through each step interactively. You make creative decisions, the agent handles all the technical details. Creating your first video podcast is easier than you think.

> **Note:** This project is still under active development and may not be fully mature yet. We are continuously iterating and improving. Your feedback and suggestions are greatly appreciated — feel free to [open an issue](https://github.com/Agents365-ai/video-podcast-maker/issues) or reach out!

## Features

- **Topic Research** - Web search and content gathering
- **Script Writing** - Structured narration with section markers
- **Multi-TTS** - Edge TTS (free), Azure Speech, Volcengine Doubao, CosyVoice, ElevenLabs, Google Cloud TTS, OpenAI TTS
- **Remotion Video** - React-based video composition with animations
- **Visual Style Editing** - Adjust colors, fonts, and layout in Remotion Studio UI
- **Real-time Preview** - Remotion Studio for instant debugging before render
- **Auto Timing** - Audio-video sync via `timing.json`
- **BGM Mixing** - Background music overlay with FFmpeg
- **Remotion-native Subtitles** - SRT rendered inside Remotion at 4K with React/CSS; legacy FFmpeg burn-in remains available for special cases
- **4K Output** - 3840x2160 resolution for crisp uploads
- **Chapter Progress Bar** - Visual timeline showing current section during playback
- **Bilingual TTS** - Chinese/English mixed narration with Azure Speech or CosyVoice
- **Pronunciation Correction** - Global + per-project phoneme dictionaries for Chinese polyphone fixes
- **Bilibili Templates** - Ready-to-use Remotion templates (`Video.tsx`, `Root.tsx`, `Thumbnail.tsx`, `podcast.txt`) for quick project scaffolding
- **Component Library** - Reusable visual building blocks (ComparisonCard, Timeline, CodeBlock, QuoteBlock, FeatureGrid, DataBar, StatCounter, FlowChart, IconCard, DiagramReveal, AudioWaveform, LottieAnimation, MediaSection, SectionLayouts, AnimatedBackground) for composing rich section layouts
- **Manual Style Profiles** - User-managed `style_profiles` in `user_prefs.json` carry palette / typography / animation settings across videos (automatic preference learning is on the roadmap, not yet implemented)
- **Multi-Platform** - Bilibili, YouTube, Xiaohongshu, Douyin, and WeChat Channels with independent platform and language settings
- **Multi-Language** - Chinese (zh-CN) and English (en-US) script templates, TTS voices, subtitle fonts
- **Subtitle Preferences** - Custom font, size, color, outline; toggle subtitle burning on/off
- **Configurable CTA** - Auto (Bilibili triple/YouTube subscribe), animation, text, or custom

### Platform Optimizations

**Bilibili:**
- **Script Structure** - Welcome intro + call-to-action outro (一键三连)
- **Chapter Timestamps** - Auto-generated `MM:SS` format for B站 chapters
- **Thumbnail Generation** - AI (imagen/imagen-qwen) or Remotion, auto-generates 16:9 + 4:3 versions
- **Visual Style** - Bold text, minimal whitespace, high information density
- **Publish Info** - Title formulas, tag strategies, description templates

**YouTube:**
- **SEO Optimization** - Title <70 chars, keyword-rich description, tags and hashtags
- **Chapters** - Auto-generated YouTube chapter timestamps (first line at 0:00)
- **CTA** - "Like, Subscribe & Share" text animation or custom

**Xiaohongshu (小红书):**
- **Title** - Max 20 chars, punchy and emoji-friendly
- **Description** - 200-500 chars, 种草/knowledge-sharing style with emoji
- **Hashtags** - `#话题#` format (double hash), 5-10 tags
- **Thumbnail** - 3:4 (1080x1440) for feed optimization
- **CTA** - "点赞收藏加关注" text animation

**Douyin (抖音):**
- **Format** - Vertical shorts only (9:16), no horizontal long-form
- **Description** - 100-200 chars, casual and conversational with emoji
- **Hashtags** - `#话题` format (single hash), 3-8 tags
- **CTA** - "点赞关注" text only (no animation)

**WeChat Channels (微信视频号):**
- **Format** - Vertical shorts only (9:16), no horizontal long-form
- **Description** - 100-300 chars, knowledge-sharing style for forwarding
- **Hashtags** - `#话题` format (single hash), 3-8 tags
- **CTA** - "点赞关注，转发给朋友" text only (no animation)

## Workflow

![Workflow](assets/workflow.png)

## ⚠️ For the human reading this (not the AI): manually polish `podcast.txt`, repeatedly

> **This section is for you, the human — not the agent.** Every downstream step — TTS narration, subtitles, section transitions, animation timing, final cut — **is derived from this single `podcast.txt`**. A weak script renders into 4K garbage. No amount of polish downstream saves it.
>
> The AI-generated draft is a starting point, nothing more. Do these yourself — **don't hand them off to the AI**:
>
> 1. **Mentally read it as the narrator.** Treat each sentence as one breath — if a line forces you to "catch your breath" or backtrack to parse, fix it. Where you stumble silently is where TTS stumbles audibly.
> 2. **Revise at least three times.**
>    - Pass 1: typos, awkward phrasing, tongue-twisters
>    - Pass 2: cut filler, cut throat-clearing intros ("So today we're going to talk about…"), cut redundancy
>    - Pass 3: tune rhythm — where to pause, where to break a long sentence, which word carries the stress
> 3. **Read each `[SECTION:xxx]` block end-to-end.** Confirm each section opens with a hook and lands a clean transition into the next — not a bullet-point dump.
> 4. **Audit numbers, proper nouns, and English terms separately.** ~90% of TTS mispronunciations live here. If pronunciation is wrong, add it to `phonemes.json`; if it just sounds awkward, rewrite it.
> 5. **Know your length budget.** Estimate **~280 zh-CN chars/min** or **~150 en words/min**. A 5–10 min video means ~1400–2800 chars / 750–1500 words. Don't pad to fill time.
>
> **The only acceptance test:** read through it once in your head — does any line make you wince? If yes, don't move on to Step 8 (TTS) yet. Otherwise you're just rendering 4K of something even you don't want to hear.

## Related Skills

This skill depends on **remotion-best-practices** and works alongside other optional skills:

- **remotion-best-practices** - Official Remotion best practices (required, provides core Remotion patterns and guidelines)
- **find-skills** - Official skill discovery tool (optional, helps find and install additional skills)
- **ffmpeg** - Advanced audio/video processing (optional)
- **imagen / imagen-qwen** - AI thumbnail generation (optional)


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

# Python dependencies (installs only what the skill's scripts/ need)
pip install -r requirements.txt
```

### Project Setup (Required)

> **Important:** This skill requires a Remotion project as the foundation.

**Understanding the components:**

| Component | Source | Purpose |
|-----------|--------|---------|
| **Remotion Project** | `npx create-video` | Base framework with `src/`, `public/`, `package.json` |
| **video-podcast-maker** | SKILL.md workflow | Workflow orchestration (this skill) |

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
| **Azure Speech** | TTS audio generation (high quality) | [Azure Portal](https://portal.azure.com/) → Speech Services |
| **Volcengine Doubao Speech** | TTS audio generation (alternative backend) | [Volcengine Console](https://console.volcengine.com/speech/service/8) |
| **Aliyun CosyVoice** | TTS audio generation (alternative backend) | [Aliyun Bailian](https://bailian.console.aliyun.com/) |
| **Edge TTS** | TTS audio generation (default, free, no key needed) | `pip install edge-tts` |
| **ElevenLabs** | TTS audio generation (highest quality English) | [ElevenLabs](https://elevenlabs.io/) |
| **Google Cloud TTS** | TTS audio generation (wide language support) | [Google Cloud Console](https://console.cloud.google.com/) |
| **OpenAI** | TTS audio generation (simple API) | [OpenAI Platform](https://platform.openai.com/) |
| **Google Gemini** | AI thumbnail generation (optional) | [AI Studio](https://aistudio.google.com/) |
| **Aliyun Dashscope** | AI thumbnail - Chinese optimized (optional) | [Aliyun Bailian](https://bailian.console.aliyun.com/) |

### Environment Variables

Add to `~/.zshrc` or `~/.bashrc`:

```bash
# TTS Backend: edge (default, free), azure, doubao, cosyvoice, elevenlabs, google, openai
export TTS_BACKEND="edge"                            # Default (free), or "azure" / "doubao" / "cosyvoice" / "elevenlabs" / "google" / "openai"

# Azure TTS (high quality)
export AZURE_SPEECH_KEY="your-azure-speech-key"
export AZURE_SPEECH_REGION="eastasia"

# Volcengine Doubao TTS (alternative backend)
export VOLCENGINE_APPID="your-volcengine-appid"
export VOLCENGINE_ACCESS_TOKEN="your-volcengine-access-token"
export VOLCENGINE_CLUSTER="volcano_tts"              # Default cluster, adjust per console config
export VOLCENGINE_VOICE_TYPE="BV001_streaming"       # Adjust per console voice options

# Aliyun CosyVoice TTS (alternative backend) + AI thumbnails
export DASHSCOPE_API_KEY="your-dashscope-api-key"

# Optional: Edge TTS voice override
export EDGE_TTS_VOICE="zh-CN-XiaoxiaoNeural"

# ElevenLabs TTS
export ELEVENLABS_API_KEY="your-elevenlabs-api-key"

# Google Cloud TTS
export GOOGLE_TTS_API_KEY="your-google-tts-api-key"

# OpenAI TTS
export OPENAI_API_KEY="your-openai-api-key"

# Optional: Google Gemini for AI thumbnails
export GEMINI_API_KEY="your-gemini-api-key"
```

Then reload: `source ~/.zshrc`

## Quick Start

### Usage

This skill is designed for use with coding agents that support `SKILL.md`, including [Claude Code](https://claude.ai/claude-code), [Codex](https://openai.com/index/introducing-codex/), and [OpenCode](https://github.com/opencode-ai/opencode). Simply tell your agent:

> "Create a video podcast about [your topic]"

The agent will guide you through the entire workflow automatically.

> **Tips:** The quality of first-generation output heavily depends on the model's intelligence and capabilities — the smarter and more advanced the model, the better the results. In our testing, both Codex and Claude Code produce excellent videos on the first try, and OpenCode paired with GLM-5 also delivers solid results. If the initial output isn't perfect, you can preview it in Remotion Studio and ask the coding agent to keep refining until you're satisfied.

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
| **Typography** | Title size (72-120), subtitle size, body size |
| **Progress Bar** | Show/hide, height, font size, active color |
| **Audio** | BGM volume (0-0.3) |
| **Animation** | Enable/disable entrance animations |


## Configuration Files

| File | Scope | Purpose |
|------|-------|---------|
| `phonemes.json` | Global | Chinese polyphone dictionary shared across all projects. Edit to add/fix pronunciations (e.g., 行 háng vs xíng). Per-project overrides go in `videos/{name}/phonemes.json` |
| `user_prefs.template.json` | Global | Default preferences template. Copied to `user_prefs.json` on first run, which auto-evolves as the skill learns your style |
| `prefs_schema.json` | Global | JSON Schema for preference validation. Do not edit manually |
| `tsconfig.json` | Global | TypeScript config for Remotion templates |

## Output Structure

```
videos/{video-name}/
├── topic_definition.md      # Topic direction
├── topic_research.md        # Research notes
├── podcast.txt              # Narration script
├── phonemes.json            # (Optional) Project-specific pronunciation overrides
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

## 💬 Community

- **Discord:** https://discord.gg/79JF5Atuk
- **WeChat:** scan the QR code below

<p align="center">
  <img src="https://raw.githubusercontent.com/Agents365-ai/images_payment/main/qrcode/agents365ai_wechat_1.png" width="200" alt="WeChat Community Group">
</p>

## ❤️ Support

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
    <td align="center">
      <img src="https://raw.githubusercontent.com/Agents365-ai/images_payment/main/awarding/award.gif" width="180" alt="Give a Reward">
      <br>
      <b>Give a Reward</b>
    </td>
  </tr>
</table>

## 👤 Author

**Agents365-ai**

- Bilibili: https://space.bilibili.com/441831884
- GitHub: https://github.com/Agents365-ai

## 📄 License

[MIT](LICENSE)
