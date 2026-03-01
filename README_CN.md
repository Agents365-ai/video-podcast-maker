# 视频播客生成器

[English](README.md)

自动化流程，从主题生成专业视频播客。**针对 B站 (Bilibili) 优化**。集成研究、脚本撰写、微软 Azure TTS、Remotion 视频渲染和 FFmpeg 音频混音。

> **无需编程！** 用自然语言描述你的主题，Claude 会一步步引导你完成。你做创意决策，Claude 处理所有技术细节。制作你的第一个视频播客，比你想象的更简单。

## 功能特点

- **主题研究** - 网络搜索与内容收集
- **脚本撰写** - 带章节标记的结构化旁白
- **Azure TTS** - 高质量中英文语音合成
- **Remotion 视频** - 基于 React 的视频合成与动画
- **可视化样式编辑** - 在 Remotion Studio 界面调整颜色、字体、布局
- **实时预览** - Remotion Studio 即时调试，渲染前预览效果
- **自动同步** - 通过 `timing.json` 实现音视频同步
- **背景音乐** - FFmpeg 叠加背景音乐
- **字幕烧录** - 可选 SRT 字幕嵌入
- **4K 输出** - 3840x2160 分辨率，画质清晰
- **章节进度条** - 可视化时间轴，实时显示当前章节
- **中英混读** - Azure Speech 支持中英文混合旁白
- **发音校正** - 内置多音字词典 + 自定义拼音支持
- **B站模板** - 开箱即用的 Remotion 模板（`Video.tsx`、`Root.tsx`、`Thumbnail.tsx`、`podcast.txt`），快速搭建项目

### B站优化

- **脚本结构** - 欢迎开场 + 一键三连片尾引导
- **章节时间戳** - 自动生成 `MM:SS` 格式，直接复制到B站
- **封面生成** - AI (imagen/imagenty) 或 Remotion，自动生成 16:9 + 4:3 双版本
- **视觉风格** - 大字饱满、极少留白、信息密度高
- **发布信息** - 标题公式、标签策略、简介模板

## 工作流程

![工作流程](assets/workflow.png)

## 相关技能

本技能可与以下 Remotion 相关技能配合使用（均为可选）：

- **remotion-best-practices** - Remotion 通用模式与最佳实践
- **remotion-design-master** - 设计系统，提供组件和主题（可选，适合结构化设计）
- **ffmpeg** - 高级音视频处理
- **imagen / imagenty** - AI 封面生成


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

# Python 依赖
pip install azure-cognitiveservices-speech requests
```

### 项目初始化（必需）

> **重要：** 本技能需要一个 Remotion 项目作为基础。

**组件关系说明：**

| 组件 | 来源 | 作用 |
|------|------|------|
| **Remotion 项目** | `npx create-video` | 基础框架，包含 `src/`、`public/`、`package.json` |
| **video-podcast-maker** | Claude Code skill | 工作流编排（本技能） |

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
| **Azure Speech** | TTS 语音合成（必需） | [Azure 门户](https://portal.azure.com/) → 语音服务 |
| **Google Gemini** | AI 封面生成（可选） | [AI Studio](https://aistudio.google.com/) |
| **阿里云百炼** | AI 封面生成 - 中文优化（可选） | [百炼控制台](https://bailian.console.aliyun.com/) |

### 环境变量

添加到 `~/.zshrc` 或 `~/.bashrc`：

```bash
# Azure TTS（必需）
export AZURE_SPEECH_KEY="your-azure-speech-key"
export AZURE_SPEECH_REGION="eastasia"

# 可选：Google Gemini 生成 AI 封面
export GEMINI_API_KEY="your-gemini-api-key"

# 可选：阿里云百炼生成 AI 封面（中文优化）
export DASHSCOPE_API_KEY="your-dashscope-api-key"
```

然后重新加载：`source ~/.zshrc`

## 快速开始

### 使用方法

本技能专为 [Claude Code](https://claude.ai/claude-code) 或 [Opencode](https://github.com/opencode-ai/opencode) 设计。只需告诉 Claude：

> "帮我制作一个关于 [你的主题] 的视频播客"

Claude 会自动引导你完成整个流程。

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
| **字体** | 标题大小 (60-120)、副标题、正文 |
| **进度条** | 显示/隐藏、高度、字号、激活颜色 |
| **音频** | BGM 音量 (0-0.3) |
| **动画** | 启用/禁用入场动画 |

```
┌─────────────────────────────────────────────────────────────────┐
│  Remotion Studio                                                │
├──────────────────────────────────┬──────────────────────────────┤
│                                  │  属性面板                     │
│                                  │  ─────────────────────────── │
│     视频预览                      │  主色调       [#4f6ef7]      │
│     (实时)                        │  背景色       [#ffffff]      │
│                                  │  标题大小     [====80===]    │
│     ┌─────────────────────┐      │  显示进度条   [✓]            │
│     │   你的视频在这里     │      │  进度条高度   [==130==]      │
│     │                     │      │  BGM音量      [=0.05====]    │
│     └─────────────────────┘      │  启用动画     [✓]            │
│                                  │                              │
│  ◀──────────●──────────────▶     │  [渲染视频]                   │
│  时间轴                           │                              │
└──────────────────────────────────┴──────────────────────────────┘
```

## 输出结构

```
videos/{视频名称}/
├── topic_definition.md      # 主题定义
├── topic_research.md        # 研究笔记
├── podcast.txt              # 旁白脚本
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

`music/` 目录下包含：
- `perfect-beauty-191271.mp3` - 轻快积极
- `snow-stevekaldes-piano-397491.mp3` - 舒缓钢琴

## 开源协议

MIT

## 支持作者

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
  </tr>
</table>

## 作者

**Agents365-ai**

- B站: https://space.bilibili.com/441831884
- GitHub: https://github.com/Agents365-ai
