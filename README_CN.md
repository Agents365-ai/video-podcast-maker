# 视频播客生成器

[English](README.md)

自动化流程，从主题生成专业视频播客。**支持 B站 (Bilibili)、YouTube、小红书、抖音和微信视频号**，多语言输出（zh-CN、en-US）。集成研究、脚本撰写、多引擎 TTS（Edge/Azure/豆包/CosyVoice）、Remotion 视频渲染和 FFmpeg 音频混音。

**支持工具：** [Claude Code](https://claude.ai/code) · [OpenClaw](https://openclaw.ai/) (ClawHub) · [OpenCode](https://opencode.ai/) · [Codex](https://openai.com/index/introducing-codex/) — 任何支持 SKILL.md 的 coding agent

**发布平台：** B站 · YouTube · 小红书 · 抖音 · 微信视频号

> **无需编程！** 用自然语言描述你的主题，coding agent 会一步步引导你完成。你做创意决策，agent 处理所有技术细节。制作你的第一个视频播客，比你想象的更简单。

> **提示：** 本项目仍在持续迭代完善中，部分功能可能还不太成熟。欢迎提出宝贵意见和建议 — 可以 [提交 Issue](https://github.com/Agents365-ai/video-podcast-maker/issues) 或直接联系作者！

## 功能特点

- **主题研究** - 网络搜索与内容收集
- **脚本撰写** - 带章节标记的结构化旁白
- **多 TTS 引擎** - Edge TTS（免费）、Azure Speech、火山引擎豆包、CosyVoice、ElevenLabs、Google Cloud TTS、OpenAI TTS
- **Remotion 视频** - 基于 React 的视频合成与动画
- **可视化样式编辑** - 在 Remotion Studio 界面调整颜色、字体、布局
- **实时预览** - Remotion Studio 即时调试，渲染前预览效果
- **自动同步** - 通过 `timing.json` 实现音视频同步
- **背景音乐** - FFmpeg 叠加背景音乐
- **字幕烧录** - 可选 SRT 字幕嵌入
- **4K 输出** - 3840x2160 分辨率，画质清晰
- **章节进度条** - 可视化时间轴，实时显示当前章节
- **中英混读** - Azure Speech 支持中英文混合旁白
- **发音校正** - 全局 + 项目级多音字词典，精准控制中文发音
- **B站模板** - 开箱即用的 Remotion 模板（`Video.tsx`、`Root.tsx`、`Thumbnail.tsx`、`podcast.txt`），快速搭建项目
- **偏好学习** - 自动学习用户风格偏好（颜色、字号、语速），智能应用到后续视频
- **多平台支持** - B站 (Bilibili)、YouTube、小红书、抖音和微信视频号，独立配置平台和语言
- **多语言支持** - 中文 (zh-CN) 和英文 (en-US) 脚本模板、TTS 音色、字幕字体
- **字幕偏好** - 自定义字体、字号、颜色、描边，支持开关字幕烧录
- **CTA 可配置** - 自动（B站三连/YouTube订阅）、动画、文字、自定义

### 平台优化

**B站:**
- **脚本结构** - 欢迎开场 + 一键三连片尾引导
- **章节时间戳** - 自动生成 `MM:SS` 格式，直接复制到B站
- **封面生成** - AI (imagen/imagen-qwen) 或 Remotion，自动生成 16:9 + 4:3 双版本
- **视觉风格** - 大字饱满、极少留白、信息密度高
- **发布信息** - 标题公式、标签策略、简介模板

**YouTube:**
- **SEO 优化** - 标题 <70 字符、关键词描述、标签和 hashtags
- **Chapters** - 自动生成 YouTube 章节时间戳（首行 0:00）
- **CTA** - "Like, Subscribe & Share" 文字动画或自定义

**小红书:**
- **标题** - 不超过 20 字，简洁有力，可用 emoji
- **正文** - 200-500 字，种草/知识分享风格，支持 emoji
- **话题标签** - `#话题#` 格式（双井号），5-10 个
- **封面** - 3:4（1080x1440）适配信息流
- **CTA** - "点赞收藏加关注" 文字动画

**抖音:**
- **格式** - 仅竖屏精华片段（9:16），不生成横屏长视频
- **文案** - 100-200 字，口语化风格，支持 emoji
- **话题标签** - `#话题` 格式（单井号），3-8 个
- **CTA** - "点赞关注" 纯文字（无动画）

**微信视频号:**
- **格式** - 仅竖屏精华片段（9:16），不生成横屏长视频
- **文案** - 100-300 字，知识分享风格，适合转发
- **话题标签** - `#话题` 格式（单井号），3-8 个
- **CTA** - "点赞关注，转发给朋友" 纯文字（无动画）

## 工作流程

![工作流程](skills/video-podcast-maker/assets/workflow.png)

## ⚠️ 给读到这里的你（不是给 AI 看的）：`podcast.txt` 必须人工反复打磨

> **这一节是写给你这个真人的，不是写给 agent 的。** 整条流水线后面所有环节 — TTS 朗读、字幕、章节切换、动画节奏、最终成片 — **全部由这一份 `podcast.txt` 决定**。脚本不行，4K 渲出来的也是垃圾。
>
> AI 生成的初稿只是起点。请你亲自做下面这些事，**不要交给 AI 代劳**：
>
> 1. **按口播节奏在脑子里默读。** 每句话当成一口气说完 — 哪句让你"换气换不过来"、哪句要回头重读才懂，立刻改。读得舒服 ≠ 听得舒服，TTS 卡住的地方往往就是你默读时也卡的地方。
> 2. **至少改三遍。**
>    - 第一遍：抓错别字、明显语病、绕口处
>    - 第二遍：砍废话、砍套话、砍"那么我们今天就来聊一聊"这种开场
>    - 第三遍：调节奏 — 哪里断句、哪里加停顿、长句切短、重音落在哪个词上
> 3. **逐章节通读。** 每个 `[SECTION:xxx]` 块从头看到尾，确认开头有钩子、结尾能自然过渡到下一节，不是一堆并列要点堆在一起。
> 4. **数字 / 专有名词 / 英文术语单独审一遍。** TTS 念错的 90% 都集中在这里。读音不对的，去 `phonemes.json` 加词条；读着别扭的，直接换说法。
> 5. **心里要有时长账。** 中文按 **每分钟约 280 字** 估算（英文约每分钟 150 词）。目标 5-10 分钟 ≈ 1400-2800 字，不要凑。
>
> **校验通过的唯一标准：脑子里走完一遍，没有任何一句让你皱眉。** 达不到就不要进 Step 8（TTS），否则你只是在用 4K 渲染一段连你自己都不想听完的内容。

## 相关技能

本技能依赖 **remotion-best-practices**，并可与其他可选技能配合使用：

- **remotion-best-practices** - Remotion 官方最佳实践（必需，提供核心 Remotion 模式与规范）
- **find-skills** - 官方技能发现工具（可选，用于查找和安装更多技能）
- **ffmpeg** - 高级音视频处理（可选）
- **imagen / imagen-qwen** - AI 封面生成（可选）


## 环境要求

### 系统要求

| 软件 | 版本 | 用途 |
|------|------|------|
| **macOS / Linux** | - | 已在 macOS 测试，兼容 Linux |
| **Python** | 3.8+ | TTS 脚本、自动化 |
| **Node.js** | 18+ | Remotion 视频渲染 |
| **FFmpeg** | 4.0+ | 音视频处理 |

### 安装依赖

```bash
# macOS
brew install ffmpeg node python3

# Ubuntu/Debian
sudo apt install ffmpeg nodejs python3 python3-pip

# Python 依赖（requirements.txt 位于技能包内）
pip install -r skills/video-podcast-maker/requirements.txt
```

> **推荐通过 marketplace 安装：** 一般用户应通过 [365-skills marketplace](https://github.com/Agents365-ai/365-skills) 安装本技能，而非克隆本仓库。届时 SKILL.md / scripts / templates 会位于 agent 暴露的 `${SKILL_DIR}` 路径下；README 中的路径写法是面向贡献者（仓库根目录视角）。

### 项目初始化（必需）

> **重要：** 本技能需要一个 Remotion 项目作为基础。

**组件关系说明：**

| 组件 | 来源 | 作用 |
|------|------|------|
| **Remotion 项目** | `npx create-video` | 基础框架，包含 `src/`、`public/`、`package.json` |
| **video-podcast-maker** | SKILL.md 工作流 | 工作流编排（本技能） |

```bash
# 第一步：创建 Remotion 项目（基础框架）
npx create-video@latest my-video-project
cd my-video-project
npm i  # 安装 Remotion 依赖

# 第二步：验证安装
npx remotion studio  # 应打开浏览器预览
```

如果你已有 Remotion 项目：

```bash
cd your-existing-project
npm install remotion @remotion/cli @remotion/player zod
```

### 所需 API 密钥

| 服务 | 用途 | 获取方式 |
|------|------|---------|
| **Azure Speech** | TTS 语音合成（高质量后端） | [Azure 门户](https://portal.azure.com/) → 语音服务 |
| **火山引擎豆包语音** | TTS 语音合成（备选后端） | [火山引擎控制台](https://console.volcengine.com/speech/service/8) |
| **阿里云 CosyVoice** | TTS 语音合成（备选后端） | [百炼控制台](https://bailian.console.aliyun.com/) |
| **Edge TTS** | TTS 语音合成（默认后端，免费，无需密钥） | `pip install edge-tts` |
| **ElevenLabs** | TTS 语音合成（英文最高质量） | [ElevenLabs](https://elevenlabs.io/) |
| **Google Cloud TTS** | TTS 语音合成（语言支持最广） | [Google Cloud 控制台](https://console.cloud.google.com/) |
| **OpenAI** | TTS 语音合成（简洁 API） | [OpenAI Platform](https://platform.openai.com/) |
| **Google Gemini** | AI 封面生成（可选） | [AI Studio](https://aistudio.google.com/) |
| **阿里云百炼** | AI 封面生成 - 中文优化（可选） | [百炼控制台](https://bailian.console.aliyun.com/) |

### 环境变量

添加到 `~/.zshrc` 或 `~/.bashrc`：

```bash
# TTS 后端选择：edge（默认，免费）、azure、doubao、cosyvoice、elevenlabs、google、openai
export TTS_BACKEND="edge"                            # 默认值，或 "azure" / "doubao" / "cosyvoice" / "elevenlabs" / "google" / "openai"

# Azure TTS（高质量后端）
export AZURE_SPEECH_KEY="your-azure-speech-key"
export AZURE_SPEECH_REGION="eastasia"

# 火山引擎豆包 TTS（备选后端）
export VOLCENGINE_APPID="your-volcengine-appid"
export VOLCENGINE_ACCESS_TOKEN="your-volcengine-access-token"
export VOLCENGINE_CLUSTER="volcano_tts"              # 默认值，可按控制台配置修改
export VOLCENGINE_VOICE_TYPE="BV001_streaming"       # 可按控制台音色修改

# 阿里云 CosyVoice TTS（备选后端）+ AI 封面
export DASHSCOPE_API_KEY="your-dashscope-api-key"

# 可选：Edge TTS 语音覆盖
export EDGE_TTS_VOICE="zh-CN-XiaoxiaoNeural"

# ElevenLabs TTS
export ELEVENLABS_API_KEY="your-elevenlabs-api-key"

# Google Cloud TTS
export GOOGLE_TTS_API_KEY="your-google-tts-api-key"

# OpenAI TTS
export OPENAI_API_KEY="your-openai-api-key"

# 可选：Google Gemini 生成 AI 封面
export GEMINI_API_KEY="your-gemini-api-key"
```

然后重新加载：`source ~/.zshrc`

## 快速开始

### 使用方法

本技能适用于支持 `SKILL.md` 的 coding agent，包括 [Claude Code](https://claude.ai/claude-code)、[Codex](https://openai.com/index/introducing-codex/) 和 [OpenCode](https://github.com/opencode-ai/opencode)。只需告诉你的 agent：

> "帮我制作一个关于 [你的主题] 的视频播客"

agent 会自动引导你完成整个流程。

> **提示：** 经过多次测试，初次生成的效果和模型效果有很大的关系，模型越智能越先进，生成的效果会越好。目前初次生成 Codex 和 Claude Code 生成的视频效果都不错，OpenCode 搭配 GLM-5 也还不错。如果第一次生成的不够好，可以在 Remotion Studio 预览，并让 coding agent 继续修改。

### 预览与可视化编辑

在渲染最终视频前，使用 Remotion Studio 实时预览和可视化编辑样式：

```bash
npx remotion studio src/remotion/index.ts
```

这会打开一个浏览器编辑器，你可以：
- **可视化样式编辑** - 在右侧面板调整颜色、字体、尺寸
- 逐帧拖动时间轴查看效果
- 编辑组件时实时看到更新
- 即时调试时间和动画

#### 可编辑属性

| 分类 | 属性 |
|------|------|
| **颜色** | 主色调、背景色、文字颜色、强调色 |
| **字体** | 标题大小 (72-120)、副标题、正文 |
| **进度条** | 显示/隐藏、高度、字号、激活颜色 |
| **音频** | BGM 音量 (0-0.3) |
| **动画** | 启用/禁用入场动画 |


## 配置文件

下表所有路径都相对于技能根目录（本仓库为 `skills/video-podcast-maker/`，通过 marketplace 安装后为 `${SKILL_DIR}`）：

| 文件 | 作用域 | 说明 |
|------|--------|------|
| `phonemes.json` | 全局 | 多音字词典，所有视频项目共享。首次运行时由脚本从 `phonemes.template.json` 自动复制。可直接编辑添加/修正发音（如 行 háng vs xíng）。项目级覆盖放在 `videos/{名称}/phonemes.json` |
| `user_prefs.template.json` | 全局 | 偏好默认模板。首次运行时自动复制为 `user_prefs.json`，后续随使用自动学习你的风格 |
| `prefs_schema.json` | 全局 | 偏好验证的 JSON Schema，无需手动编辑 |
| `tsconfig.json` | 全局 | Remotion 模板的 TypeScript 配置 |

## 输出结构

```
videos/{视频名称}/
├── topic_definition.md      # 主题定义
├── topic_research.md        # 研究笔记
├── podcast.txt              # 旁白脚本
├── phonemes.json            # （可选）项目专属发音覆盖
├── podcast_audio.wav        # TTS 音频
├── podcast_audio.srt        # 字幕文件
├── timing.json              # 章节时间轴
├── thumbnail_*.png          # 视频封面
├── publish_info.md          # 标题、标签、简介
├── part_*.wav               # TTS 分段（临时，Step 14 清理）
├── output.mp4               # 原始渲染（临时）
├── video_with_bgm.mp4       # 含背景音乐（临时）
└── final_video.mp4          # 最终输出
```

## 背景音乐

`skills/video-podcast-maker/assets/` 目录下包含：
- `perfect-beauty-191271.mp3` - 轻快积极
- `snow-stevekaldes-piano-397491.mp3` - 舒缓钢琴

## 开发路线

- [x] 支持竖屏视频 (9:16)，适配 B站手机端沉浸式播放
- [x] Remotion 转场效果 (@remotion/transitions)，章节间过渡更专业
- [x] 组件模板库 (ComparisonCard, Timeline, CodeBlock, QuoteBlock, FeatureGrid, DataBar, StatCounter, FlowChart, IconCard)
- [x] 广播级画质升级（渐变背景、多层阴影、动画计数器、质量检查清单）
- [x] 多 TTS 引擎支持（7 引擎：Edge、Azure、豆包、CosyVoice、ElevenLabs、OpenAI、Google Cloud）
- [x] Edge TTS 免费后端（无需 API 密钥）
- [x] 多平台支持（B站 + YouTube），独立语言配置（zh-CN、en-US）
- [x] 断点续传（`--resume` 参数）
- [x] 预估模式（`--dry-run` 预估时长，不调用 API）
- [x] 用户偏好自我进化（自动学习视觉/TTS/内容风格偏好）
- [x] 视觉检查 - 对生成后的页面进行视觉检查，检查其美观性、布局合理性等
- [x] 将技能文档重构为可被 Claude Code、Codex、OpenCode、OpenClaw 共同使用的 `SKILL.md` 工作流
- [x] 设计学习系统 — 从参考视频/图片中学习设计风格，构建设计参考库和可复用的风格档案
- [ ] Playwright 自动抓取 — 通过 URL 直接分析 B站/YouTube 视频设计风格（Phase 4）
- [ ] Step 9 智能推荐 — 制作视频时自动匹配并推荐已有风格档案（Phase 5）
- [ ] 封面设计学习 — 将学到的封面风格应用到 Thumbnail.tsx 模板（Phase 5）
- [ ] YouTube 自动化发布 — 通过 YouTube Data API 上传视频、元数据、章节、封面
- [ ] Windows 适配 (WSL 验证 + 文档)

## 💬 社区

- **Discord:** https://discord.gg/79JF5Atuk
- **微信:** 扫描下方二维码

<p align="center">
  <img src="https://raw.githubusercontent.com/Agents365-ai/images_payment/main/qrcode/agents365ai_wechat_1.png" width="200" alt="微信交流群">
</p>

## ❤️ 支持作者

如果这个项目对你有帮助，欢迎支持作者：

<table>
  <tr>
    <td align="center">
      <img src="https://raw.githubusercontent.com/Agents365-ai/images_payment/main/qrcode/wechat-pay.png" width="180" alt="微信支付">
      <br>
      <b>微信支付</b>
    </td>
    <td align="center">
      <img src="https://raw.githubusercontent.com/Agents365-ai/images_payment/main/qrcode/alipay.png" width="180" alt="支付宝">
      <br>
      <b>支付宝</b>
    </td>
    <td align="center">
      <img src="https://raw.githubusercontent.com/Agents365-ai/images_payment/main/qrcode/buymeacoffee.png" width="180" alt="Buy Me a Coffee">
      <br>
      <b>Buy Me a Coffee</b>
    </td>
    <td align="center">
      <img src="https://raw.githubusercontent.com/Agents365-ai/images_payment/main/awarding/award.gif" width="180" alt="打赏">
      <br>
      <b>打赏</b>
    </td>
  </tr>
</table>

## 👤 作者

**Agents365-ai**

- B站: https://space.bilibili.com/441831884
- GitHub: https://github.com/Agents365-ai

## 📄 开源协议

[MIT](LICENSE)
