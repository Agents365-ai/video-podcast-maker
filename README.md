# Video Podcast Maker

[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/Agents365-ai/video-podcast-maker?style=flat&logo=github)](https://github.com/Agents365-ai/video-podcast-maker/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/Agents365-ai/video-podcast-maker?style=flat&logo=github)](https://github.com/Agents365-ai/video-podcast-maker/network/members)
[![Latest Release](https://img.shields.io/github/v/release/Agents365-ai/video-podcast-maker?logo=github)](https://github.com/Agents365-ai/video-podcast-maker/releases/latest)
[![Last Commit](https://img.shields.io/github/last-commit/Agents365-ai/video-podcast-maker?logo=github)](https://github.com/Agents365-ai/video-podcast-maker/commits/main)

[![SkillsMP](https://img.shields.io/badge/SkillsMP-listed-1f6feb)](https://skillsmp.com)
[![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-plugin-8a2be2)](https://github.com/Agents365-ai/365-skills)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-2ea44f)](https://agentskills.io)

[中文文档](README_CN.md)

Automated pipeline to create professional video podcasts from a topic. **Supports Bilibili, YouTube, Xiaohongshu, Douyin, and WeChat Channels** with multi-language output (zh-CN, en-US). Combines research, script generation, multi-engine TTS (11 backends via the [ttscn](https://github.com/Agents365-ai/ttsCN) bridge), Remotion rendering, and FFmpeg mixing. Current release: **v5.2.1** — see [CHANGELOG.md](CHANGELOG.md) for version history.

**Works with:** [Claude Code](https://claude.ai/code) · [OpenClaw](https://openclaw.ai/) · [OpenCode](https://opencode.ai/) · [Codex](https://openai.com/index/introducing-codex/) · [Pi](https://github.com/earendil-works/pi-coding-agent) — any coding agent that supports SKILL.md

**Publish to:** Bilibili · YouTube · Xiaohongshu · Douyin · WeChat Channels

> **No coding required!** Just describe your topic in plain language — the coding agent guides you through each step interactively. You make creative decisions, the agent handles all the technical details.

> **Note:** This project is still under active development and may not be fully mature yet. Your feedback is greatly appreciated — feel free to [open an issue](https://github.com/Agents365-ai/video-podcast-maker/issues).

## Features

- **Topic → 4K video** - research, narration script, TTS audio, Remotion composition, 4K render + BGM in one pipeline
- **11 TTS backends** - Edge (free), Azure, CosyVoice, Doubao, Tencent, Baidu, MiniMax, Xunfei, ElevenLabs, OpenAI, Google — all synthesized by the required [ttscn](https://github.com/Agents365-ai/ttsCN) component skill
- **Asset engine** - per-video manifest with license provenance; producers are user files, assetseeker stock, imagencn AI stills, videogencn AI B-roll, and Hyperframes overlays — paid generation always asks first
- **4K output + Remotion-native subtitles** - 3840×2160; SRT rendered in React at 4K (legacy FFmpeg burn-in available)
- **Design learning** - extract style profiles from reference videos/images; auto-applied when topics match
- **Vertical shorts** - 9:16 highlight clips generated from long-form sections
- **Multi-platform & multi-language** - Bilibili / YouTube / Xiaohongshu / Douyin / WeChat Channels × zh-CN / en-US, with per-platform publish info
- **Pronunciation control** - global + per-project phoneme dictionaries for Chinese polyphones

## Quick Start

**1. Install** — via the [365-skills marketplace](https://github.com/Agents365-ai/365-skills) (recommended) or by cloning this repo.

**2. Set up** — Python 3.8+, Node.js 18+, FFmpeg, and a Remotion project:

```bash
brew install ffmpeg node python3          # macOS (Ubuntu: sudo apt install ffmpeg nodejs python3)
pip install -r skills/video-podcast-maker/requirements.txt
npx create-video@latest my-video-project   # or reuse an existing Remotion project
cd my-video-project && npm i
```

**3. Configure** — set `TTS_BACKEND` plus its API keys (see [TTS Backends](#tts-backends) and [Environment Variables](#environment-variables)).

**4. Tell your agent:**

> "Create a video podcast about [your topic]"

The agent runs the whole workflow (research → script → TTS → Remotion composition → Studio review → 4K render + BGM). Preview and iterate in Remotion Studio (`npx remotion studio src/remotion/index.ts`); the agent waits for your explicit "render 4K" confirmation before the final render.

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
> **The only acceptance test:** read through it once in your head — does any line make you wince? If yes, don't move on to Step 7 (TTS) yet. Otherwise you're just rendering 4K of something even you don't want to hear.

## Workflow

![Pipeline](images/pipeline.png)

![Component Skills](images/skills.png)

![Asset Flow](images/assets.png)

## Related Skills

- **[remotion-best-practices](https://github.com/remotion-dev/skills)** - required; core Remotion patterns and guidelines
- **[ttscn](https://github.com/Agents365-ai/ttsCN)** - required; the TTS engine behind all 11 backends (install under `~/.claude/skills/ttscn`, as a Pi skill, or set `TTSCN_HOME`)
- **[assetseeker](https://github.com/Agents365-ai/assetSeeker)** - optional; license-vetted stock photos/video/BGM/SFX/icons/fonts
- **[imagencn](https://github.com/Agents365-ai/imagenCN)** - optional; AI stills and thumbnails (paid APIs)
- **[videogencn](https://github.com/Agents365-ai/videogenCN)** - optional; AI video clips for B-roll (paid APIs)
- **[Hyperframes](https://github.com/heygen-com/hyperframes)** - optional; transparent overlay animations (Node 22+)

## Requirements

| Software | Version | Purpose |
| ---------- | --------- | --------- |
| **macOS / Linux** | - | Tested on macOS, Linux compatible |
| **Python** | 3.8+ | TTS script, automation |
| **Node.js** | 18+ | Remotion video rendering |
| **FFmpeg** | 4.0+ | Audio/video processing |

> **Marketplace install (recommended):** users typically install this skill via the [365-skills marketplace](https://github.com/Agents365-ai/365-skills) rather than cloning. SKILL.md, scripts, and templates then live under the agent's `${SKILL_DIR}`; paths in this README are written from the repo-root perspective for contributors.

### TTS Backends (all via ttscn)

All 11 platforms are synthesized by the **required** [ttscn](https://github.com/Agents365-ai/ttsCN) component skill. Set `TTS_BACKEND` to any platform id; only the active platform's env vars are needed:

| `TTS_BACKEND` | Provider | Required env vars | Get Key |
| --------------- | ---------- | ------------------- | --------- |
| `edge` (default) | Microsoft Edge TTS | *(none — free)* | — |
| `azure` | Microsoft Azure Speech | `AZURE_SPEECH_KEY` (+ optional `AZURE_SPEECH_REGION`, default `eastasia`) | [Azure Portal](https://portal.azure.com/) |
| `cosyvoice` | Aliyun CosyVoice | `DASHSCOPE_API_KEY` | [Aliyun Bailian](https://bailian.console.aliyun.com/) |
| `doubao` | Volcengine Doubao | `VOLCENGINE_APPID`, `VOLCENGINE_ACCESS_TOKEN` | [Volcengine Console](https://console.volcengine.com/speech/service/8) |
| `tencent` | Tencent Cloud TTS | `TENCENT_SECRET_ID`, `TENCENT_SECRET_KEY` | [Tencent Console](https://console.cloud.tencent.com/tts) |
| `baidu` | Baidu AI TTS | `BAIDU_APP_ID`, `BAIDU_API_KEY`, `BAIDU_SECRET_KEY` | [Baidu Console](https://console.bce.baidu.com/ai/#/ai/speech/overview) |
| `minimax` | MiniMax TTS | `MINIMAX_API_KEY` | [MiniMax Platform](https://platform.minimaxi.com/) |
| `xunfei` | iFlytek Xunfei TTS | `XUNFEI_APP_ID`, `XUNFEI_API_KEY`, `XUNFEI_API_SECRET` | [Xfyun](https://www.xfyun.cn/) |
| `elevenlabs` | ElevenLabs | `ELEVENLABS_API_KEY` | [ElevenLabs](https://elevenlabs.io/) |
| `openai` | OpenAI TTS | `OPENAI_API_KEY` | [OpenAI Platform](https://platform.openai.com/) |
| `google` | Google Cloud TTS | `GOOGLE_TTS_API_KEY` | [Google Cloud Console](https://console.cloud.google.com/) |

**Non-TTS keys (optional):** `GEMINI_API_KEY` / `DASHSCOPE_API_KEY` for AI thumbnails (imagencn).

### Environment Variables

Add to `~/.zshrc` or `~/.bashrc`:

```bash
export TTS_BACKEND="edge"                  # azure / cosyvoice / doubao / tencent / baidu / minimax / xunfei / elevenlabs / openai / google
export TTS_VOICE="zh-CN-XiaoxiaoNeural"    # optional; unset = platform default
export TTS_RATE="+5%"                      # optional; also settable in user_prefs.json (global.tts.rate)
export TTS_STYLE="gentle"                  # optional; azure only
export AZURE_SPEECH_KEY="..."              # keys for the active platform only (see table above)
export GEMINI_API_KEY="..."                # optional: AI thumbnails
export DASHSCOPE_API_KEY="..."             # optional: AI thumbnails (also the cosyvoice TTS key)
```

Then reload: `source ~/.zshrc`

## Configuration

Mutable user-level files live in `~/.video-podcast-maker/` (shared across projects, safe from skill updates); the rest live in the skill root (`skills/video-podcast-maker/` in this repo, `${SKILL_DIR}` when installed):

| File | Location | Purpose |
| ------ | -------- | --------- |
| `phonemes.json` | `~/.video-podcast-maker/` | Global polyphone dictionary; auto-created from the bundled template; per-project overrides in `videos/{name}/phonemes.json` |
| `user_prefs.json` | `~/.video-podcast-maker/` | Your preferences (TTS, BGM, platform, visual overrides, style profiles); auto-created from template |
| `user_prefs.template.json` / `phonemes.template.json` | Skill root | Default templates — sources for the user-level copies |
| `prefs_schema.json` | Skill root | JSON Schema for preference validation |
| `tsconfig.json` | Skill root | TypeScript config for Remotion templates |

**Output structure** — every video renders into its own `videos/{name}/` directory:

```
videos/{video-name}/
├── topic_definition.md      # Topic direction
├── topic_research.md        # Research notes
├── podcast.txt              # Narration script
├── phonemes.json            # (Optional) pronunciation overrides
├── assets/manifest.json     # Asset registry (role / source / license)
├── podcast_audio.wav        # TTS audio
├── podcast_audio.srt        # Subtitles
├── timing.json              # Section timing (drives animation sync)
├── thumbnail_*.png          # Video thumbnails
├── publish_info.md          # Title, tags, description
├── output.mp4               # Raw 4K render
├── video_with_bgm.mp4       # With BGM
├── bgm.mp3                  # Background music
├── final_video.mp4          # Final output
└── shorts/                  # (Optional) 9:16 vertical shorts
```

**Background music:** bundled tracks live in `skills/video-podcast-maker/assets/` — `perfect-beauty-191271.mp3` (upbeat) and `snow-stevekaldes-piano-397491.mp3` (calm piano). Per-platform behavior (thumbnails, chapters, CTA, publish formats) is documented in the skill's `references/platform-matrix.md`.

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

- Bilibili: <https://space.bilibili.com/441831884>
- GitHub: <https://github.com/Agents365-ai>

## 📄 License

[CC BY-NC 4.0](LICENSE) — Free for non-commercial use. Commercial use requires permission.
