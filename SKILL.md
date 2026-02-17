---
name: video-podcast-maker
description: Use when user provides a topic and wants an automated video podcast created - handles research, script writing, TTS audio synthesis, Remotion video creation, and final MP4 output with background music
author: 探索未至之境
created: 2025-01-27
updated: 2026-02-14
bilibili: https://space.bilibili.com/441831884
---

# Video Podcast Maker

## Quick Start

> **5分钟上手？** 查看 [docs/QUICKSTART.md](docs/QUICKSTART.md)
>
> **遇到问题？** 查看 [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
>
> **组件参考？** 查看 [docs/COMPONENTS.md](docs/COMPONENTS.md)

打开 Claude Code，直接说：**"帮我制作一个关于 [你的主题] 的 B站视频播客"**

---

## Overview

Automated pipeline to create professional **Bilibili (B站) 横屏知识视频** from a topic.

> **目标平台：B站横屏视频 (16:9)**
> - 分辨率：3840×2160 (4K) 或 1920×1080 (1080p)
> - 风格：简约纯白（默认）

**技术栈：** Claude + Azure TTS + Remotion + FFmpeg

### 适用场景

| 适合 | 不适合 |
|------|--------|
| 知识科普视频 | 竖屏短视频 |
| 产品对比评测 | 直播录像 |
| 教程讲解 | 真人出镜 |
| 新闻资讯解读 | Vlog |
| 技术深度分析 | 音乐 MV |

### 输出规格

| 参数 | 值 |
|------|-----|
| **分辨率** | 3840×2160 (4K) |
| **帧率** | 30 fps |
| **编码** | H.264, 16Mbps |
| **音频** | AAC, 192kbps |
| **时长** | 1-15 分钟 |

---

## 核心设计原则

> **"宁可撑爆，不可留白"** — 文字和UI必须占满屏幕，最大化视觉冲击力。

| 规则 | 数值 | 说明 |
|------|------|------|
| **内容宽度** | ≥85% 屏幕 | 不要缩在中间 |
| **页面边距** | 30-50px | 极窄，内容贴边 |
| **主标题** | 80-100px | 超大粗体 |
| **副标题** | 48-64px | 醒目清晰 |
| **数据数字** | 64-140px | 数据即主角 |
| **元素间距** | 24-40px | 紧凑排列 |

---

## 硬约束规则（验收标准）

> **布局约束是单元测试，不满足即重写。**

### 必须满足

| ID | 约束 | 检查方法 |
|----|------|----------|
| **L1** | 根容器 `position: absolute; inset: 0` | 检查最外层 style |
| **L2** | 根容器 `overflow: hidden; padding: 0; margin: 0` | 检查最外层 style |
| **L3** | 媒体 `width: 100%; height: 100%` | 检查所有 Img/Video |
| **L4** | 默认 `objectFit: cover`，非 16:9 用双层结构 | 检查媒体组件 |
| **L5** | 内容区宽度 ≥85% 屏幕 | 检查 maxWidth |
| **L6** | 主标题 ≥80px，副标题 ≥48px | 检查 fontSize |
| **L7** | 页面边距 ≤50px | 检查 padding |
| **L8** | 底部留 80-100px 给字幕 | 检查 paddingBottom |

### 禁止的写法

```tsx
// ❌ 禁止：会导致缩小居中
style={{ margin: 'auto' }}
style={{ justifyContent: 'center', alignItems: 'center' }}  // 对根容器
style={{ maxWidth: 600 }}  // 太小
style={{ objectFit: 'contain' }}  // 除非用双层结构

// ✅ 正确：使用预制组件
<FullBleed>
  <ContentArea>
    <CoverMedia src={...} />
  </ContentArea>
</FullBleed>
```

### 自检清单

生成 Remotion 组件后必须确认：
1. [ ] 根容器使用 `<FullBleed>` 或 `position: absolute; inset: 0`
2. [ ] 所有 Img/Video 为 `width: 100%; height: 100%`
3. [ ] 无 `margin: auto` 或 `placeItems: center`
4. [ ] 主标题 ≥80px
5. [ ] 页面 padding ≤50px
6. [ ] 非 16:9 素材使用 `<DualLayerMedia>`

**任一项不满足，必须重写。**

---

## FullBleed 布局系统

> **用预制组件代替自由布局。** 详见 [docs/COMPONENTS.md](docs/COMPONENTS.md)

### 安装

```bash
cp ~/.claude/skills/video-podcast-maker/FullBleedLayout.tsx src/remotion/
```

### 核心组件

| 组件 | 用途 | 硬约束 |
|------|------|--------|
| `<FullBleed>` | 章节根容器 | `position: absolute; inset: 0; overflow: hidden` |
| `<ContentArea>` | 内容区域 | 宽度 85%-95%，底部留白 |
| `<CoverMedia>` | 图片/视频 | `width/height: 100%; objectFit: cover` |
| `<DualLayerMedia>` | 非 16:9 素材 | 模糊背景层 + 清晰前景层 |
| `<KenBurnsMedia>` | 带缩放的媒体 | cover + 缩放动效 |

### 基本用法

```tsx
import {
  FullBleed, ContentArea, CoverMedia, DualLayerMedia,
  FadeIn, SpringPop, Title, DataDisplay, tokens, font
} from './FullBleedLayout'

const HeroSection = () => (
  <FullBleed background={tokens.colors.bg}>
    <ContentArea>
      <FadeIn>
        <Title size="hero">主标题</Title>
      </FadeIn>
      <FadeIn delay={15}>
        <Title size="medium" color={tokens.colors.textMuted}>副标题</Title>
      </FadeIn>
    </ContentArea>
  </FullBleed>
)
```

---

## 文件路径与命名规范

### 目录结构

```
videos/{video-name}/                    # 视频项目目录
├── topic_definition.md                 # Step 0: 主题定义
├── topic_research.md                   # Step 1: 研究资料
├── podcast.txt                         # Step 3: 旁白脚本
├── media_manifest.json                 # Step 4: 素材清单
├── publish_info.md                     # Step 5+12: 发布信息
├── podcast_audio.wav                   # Step 7: TTS 音频
├── podcast_audio.srt                   # Step 7: 字幕文件
├── timing.json                         # Step 7: 时间轴
├── thumbnail_*.png                     # Step 6: 封面
├── output.mp4                          # Step 9: Remotion 输出
├── video_with_bgm.mp4                  # Step 10: 添加 BGM
├── final_video.mp4                     # Step 11: 最终输出
└── bgm.mp3                             # 背景音乐

public/media/{video-name}/              # 素材目录 (Remotion 可访问)
├── {section}_{index}.{ext}             # 通用素材
├── {section}_screenshot.png            # 网页截图
├── {section}_screenshot_cropped.png    # 裁剪后截图
├── {section}_logo.png                  # Logo
├── {section}_web_{index}.{ext}         # 网络图片
└── {section}_ai.png                    # AI 生成图片
```

### 命名规则

**视频名称 `{video-name}`**: 全小写英文，连字符分隔（如 `reference-manager-comparison`）

**章节名称 `{section}`**: 全小写英文，下划线分隔，与 `[SECTION:xxx]` 一致

**缩略图命名**:
| 类型 | 16:9 | 4:3 |
|------|------|-----|
| Remotion | `thumbnail_remotion_16x9.png` | `thumbnail_remotion_4x3.png` |
| AI | `thumbnail_ai_16x9.png` | `thumbnail_ai_4x3.png` |

### 渲染前后文件操作

```bash
# 渲染前
cp videos/{name}/podcast_audio.wav videos/{name}/timing.json public/
[ -f videos/{name}/media_manifest.json ] && cp videos/{name}/media_manifest.json public/

# 渲染后清理
rm -f public/podcast_audio.wav public/timing.json public/media_manifest.json
rm -rf public/media/{name}
```

---

## Workflow

| Step | Tool | Output |
|------|------|--------|
| **0. Define Direction** | brainstorming | `topic_definition.md` |
| **1. Research** | WebSearch, WebFetch | `topic_research.md` |
| **2. Design Sections** | brainstorming | 5-7 sections plan |
| **3. Write Script** | Claude | `podcast.txt` |
| **4. Collect Media** | Playwright/WebSearch | `media_manifest.json` |
| **5. Publish Info (Part 1)** | Claude | `publish_info.md` |
| **6. Thumbnail** | Remotion/imagen/imagenty | `thumbnail_*.png` |
| **7. Generate Audio** | generate_tts.py | `.wav`, `.srt`, `timing.json` |
| **8. Create Video** | Remotion | Composition ready |
| **9. Render** | remotion render | `output.mp4` |
| **10. Add BGM** | FFmpeg | `video_with_bgm.mp4` |
| **11. Subtitles** | FFmpeg + SRT | `final_video.mp4` |
| **12. Publish Info (Part 2)** | Claude | Update chapters |

### Validation Checkpoints

**After Step 7 (TTS)**:
- [ ] `podcast_audio.wav` exists and plays correctly
- [ ] `timing.json` has all sections with correct timestamps
- [ ] `podcast_audio.srt` encoding is UTF-8

**After Step 9 (Render)**:
- [ ] `output.mp4` resolution is 3840x2160
- [ ] Audio-video sync verified
- [ ] No black frames

**After Step 11 (Final)**:
- [ ] `final_video.mp4` resolution is 3840x2160
- [ ] Subtitles display correctly (if added)
- [ ] File size is reasonable

---

## Step 0: Define Topic Direction

使用 brainstorming 确认：
1. **目标受众**: 技术开发者 / 普通用户 / 学生 / 专业人士
2. **视频定位**: 科普入门 / 深度解析 / 新闻速报 / 教程实操
3. **内容范围**: 历史背景 / 技术原理 / 使用方法 / 对比评测
4. **视频风格**: 严肃专业 / 轻松幽默 / 快节奏
5. **时长预期**: 短 (1-3分钟) / 中 (3-7分钟) / 长 (7-15分钟)

保存为 `videos/{name}/topic_definition.md`

---

## Step 1: Research Topic

Use WebSearch and WebFetch. Save to `videos/{name}/topic_research.md`.

---

## Step 2: Design Video Sections

Design 5-7 sections:
- Hero/Intro (15-25s)
- Core concepts (30-45s each)
- Demo/Examples (30-60s)
- Comparison/Analysis (30-45s)
- Summary (20-30s)

---

## Step 3: Write Narration Script

Create `videos/{name}/podcast.txt` with section markers:

```text
[SECTION:hero]
大家好，欢迎来到本期视频。今天我们聊一个...

[SECTION:features]
它有以下功能...

[SECTION:demo]
让我演示一下...

[SECTION:summary]
总结一下，xxx是目前最xxx的xxx。

[SECTION:references]
本期视频参考了官方文档和技术博客。

[SECTION:outro]
感谢观看！点赞投币收藏，关注我，下期再见！
```

**数字必须使用中文读音** - 所有数字必须写成中文，TTS 才能正确朗读：

| 类型 | ❌ 错误 | ✅ 正确 |
|------|---------|---------|
| 整数 | 29, 3999, 128 | 二十九，三千九百九十九，一百二十八 |
| 小数 | 1.2, 3.5 | 一点二，三点五 |
| 百分比 | 15%, -10% | 百分之十五，负百分之十 |
| 日期 | 2025-01-15 | 二零二五年一月十五日 |
| 大数字 | 6144, 234324 | 六千一百四十四，二十三万四千三百二十四 |
| 英文单位 | 128GB, 273GB/s | 一百二十八G，二百七十三GB每秒 |
| 科学记数 | 1 PFLOPS | 一PFLOPS |

**示例对比**:
```text
❌ 错误: 售价3999美元，内存128GB，去年10月15日开卖
✅ 正确: 售价三千九百九十九美元，内存一百二十八GB，去年十月十五日开卖

❌ 错误: DeepSeek R1 14B每秒2074个token
✅ 正确: DeepSeek R1蒸馏版十四B每秒两千零七十四个token
```

**章节说明**:
- **summary**: 纯内容总结，不包含互动引导
- **references** (可选): 一句话概括参考来源
- **outro**: 感谢 + 一键三连引导
- 空内容的 `[SECTION:xxx]` 为静音章节

---

## Step 4: Collect Media Assets

**首先询问用户**：是否需要使用 **imagen skill** 生成 AI 图片素材？

Claude 逐章节询问素材来源：
1. **跳过** - 纯文字动效
2. **本地文件** - 指定路径
3. **网页截图** - Playwright 截图
4. **网络检索** - 搜索下载
5. **AI 生成** - 使用 imagen skill（需用户确认）

如果用户选择 AI 生成，调用 imagen skill 生成图片：
```
使用 imagen skill 生成：[图片描述]
```

素材保存到 `public/media/{video-name}/`，生成 `media_manifest.json`。

**推荐素材来源**: 见 [docs/MEDIA_ASSETS.md](docs/MEDIA_ASSETS.md)

---

## Step 5: Generate Publish Info (Part 1)

基于 `podcast.txt` 生成 `publish_info.md`:
- 标题（数字 + 主题 + 吸引词）
- 标签（10个，含产品名/领域词/热门标签）
- 简介（100-200字）

---

## Step 6: Generate Video Thumbnail

**询问用户选择封面生成方式**:
1. **Remotion生成** - 代码控制，风格与视频一致
2. **AI文生图（imagen skill）** - 使用 imagen skill 生成创意封面
3. **两者都生成** - 同时生成两种风格供选择

每种方式生成 **两个比例**: 16:9 和 4:3

**Remotion 渲染封面**:
```bash
npx remotion still src/remotion/index.ts Thumbnail16x9 videos/{name}/thumbnail_remotion_16x9.png
npx remotion still src/remotion/index.ts Thumbnail4x3 videos/{name}/thumbnail_remotion_4x3.png
```

**使用 imagen skill 生成封面**:
```
使用 imagen skill 生成视频封面：
- 主题：[视频主题]
- 风格：科技感/简约/活泼
- 比例：16:9 和 4:3
```

---

## Step 7: Generate TTS Audio

```bash
cp ~/.claude/skills/video-podcast-maker/generate_tts.py .
python3 generate_tts.py --input videos/{name}/podcast.txt --output-dir videos/{name}
```

**多音字处理** - 使用同音字替换：
| 原词 | 替换为 | 说明 |
|------|--------|------|
| 一行命令 | 一航命令 | "航" 只有 háng |
| 代码行 | 代码航 | 同上 |

**Outputs**: `podcast_audio.wav`, `podcast_audio.srt`, `timing.json`

---

## Step 8: Create Remotion Composition

复制文件到 public/:
```bash
cp videos/{name}/podcast_audio.wav videos/{name}/timing.json public/
```

使用 `timing.json` 同步：

```tsx
import timingData from '../public/timing.json'

// 4K 分辨率 + scale(2) 容器
<Composition
  durationInFrames={timingData.total_frames}
  fps={timingData.fps}
  width={3840}
  height={2160}
  ...
/>

export const MyVideo = () => (
  <AbsoluteFill style={{ background: '#fff' }}>
    <Audio src={staticFile('podcast_audio.wav')} />
    <AbsoluteFill style={{ transform: 'scale(2)', transformOrigin: 'top left', width: '50%', height: '50%' }}>
      {timingData.sections.map(section => (
        <Sequence key={section.name} from={section.start_frame} durationInFrames={section.duration_frames}>
          <SectionComponent name={section.name} />
        </Sequence>
      ))}
    </AbsoluteFill>
  </AbsoluteFill>
)
```

**视觉风格**: 见 [docs/VISUAL_STYLES.md](docs/VISUAL_STYLES.md)

**组件参考**: 见 [docs/COMPONENTS.md](docs/COMPONENTS.md)

### 章节进度条（可选）

**询问用户是否需要底部章节进度条**，显示当前播放进度和章节名称。

默认样式：白底简约风格
- 圆角胶囊形状章节按钮
- 当前章节蓝色高亮 + 内部进度填充
- 已播章节浅灰色
- 底部蓝色总进度条

如果用户需要，添加 `<ChapterProgressBar />` 组件：

```tsx
// 章节数据（从 timing.json 生成，添加中文 label）
const chapters = [
  { name: "hero", label: "开场", start_frame: 0, duration_frames: 532 },
  { name: "features", label: "功能介绍", start_frame: 532, duration_frames: 900 },
  // ... 根据实际章节填写
]
const TOTAL_FRAMES = timingData.total_frames

const ChapterProgressBar = () => {
  const frame = useCurrentFrame()
  const progress = frame / TOTAL_FRAMES

  return (
    <div style={{
      position: 'absolute', bottom: 0, left: 0, right: 0, height: 110,
      background: '#fff', borderTop: '1px solid #e5e7eb',
      display: 'flex', alignItems: 'center', padding: '0 50px', gap: 16,
      fontFamily: font,
    }}>
      {chapters.map((ch) => {
        const chStart = ch.start_frame / TOTAL_FRAMES
        const chEnd = (ch.start_frame + ch.duration_frames) / TOTAL_FRAMES
        const isActive = progress >= chStart && progress < chEnd
        const isPast = progress >= chEnd
        const chProgress = isActive ? (progress - chStart) / (chEnd - chStart) : isPast ? 1 : 0

        return (
          <div key={ch.name} style={{
            flex: ch.duration_frames,
            height: 64, borderRadius: 32, position: 'relative', overflow: 'hidden',
            background: isActive ? '#4f6ef7' : isPast ? '#f3f4f6' : '#f9fafb',
            border: isActive ? 'none' : '1px solid #e5e7eb',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            {isActive && (
              <div style={{
                position: 'absolute', left: 0, top: 0, bottom: 0,
                width: `${chProgress * 100}%`,
                background: 'rgba(255,255,255,0.25)',
                borderRadius: 32,
              }} />
            )}
            <span style={{
              position: 'relative', zIndex: 1,
              color: isActive ? '#fff' : isPast ? '#374151' : '#9ca3af',
              fontSize: 32, fontWeight: isActive ? 700 : 500,
              whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
              padding: '0 20px',
            }}>{ch.label}</span>
          </div>
        )
      })}
      <div style={{
        position: 'absolute', bottom: 0, left: 0, right: 0, height: 4,
        background: '#e5e7eb',
      }}>
        <div style={{ height: '100%', width: `${progress * 100}%`, background: '#4f6ef7' }} />
      </div>
    </div>
  )
}

// 在主视频组件中添加
export const MyVideo = () => (
  <AbsoluteFill style={{ background: '#fff' }}>
    <Audio src={staticFile('podcast_audio.wav')} />
    <AbsoluteFill style={{ transform: 'scale(2)', transformOrigin: 'top left', width: '50%', height: '50%' }}>
      {/* 章节内容 */}
    </AbsoluteFill>
    <ChapterProgressBar />  {/* 添加进度条 */}
  </AbsoluteFill>
)
```

详细组件文档见 [docs/COMPONENTS.md](docs/COMPONENTS.md#8-chapter-progress-bar)

---

## Step 9: Render Video

> **NEVER run `npx remotion studio`** — Always render directly.

```bash
npx remotion render src/remotion/index.ts CompositionId videos/{name}/output.mp4 --video-bitrate 16M
```

**验证 4K**:
```bash
ffprobe -v quiet -show_entries stream=width,height -of csv=p=0 videos/{name}/output.mp4
# 期望: 3840,2160
```

---

## Step 10: Mix with Background Music

```bash
cp ~/.claude/skills/video-podcast-maker/music/perfect-beauty-191271.mp3 videos/{name}/bgm.mp3

ffmpeg -y \
  -i videos/{name}/output.mp4 \
  -stream_loop -1 -i videos/{name}/bgm.mp3 \
  -filter_complex "[0:a]volume=1.0[a1];[1:a]volume=0.05[a2];[a1][a2]amix=inputs=2:duration=first[aout]" \
  -map 0:v -map "[aout]" \
  -c:v copy -c:a aac -b:a 192k \
  videos/{name}/video_with_bgm.mp4
```

---

## Step 11: Add Subtitles (可选)

**询问用户是否需要字幕。** 如不需要：
```bash
cp videos/{name}/video_with_bgm.mp4 videos/{name}/final_video.mp4
```

**添加字幕（纯白背景用深色字幕）**:
```bash
ffmpeg -y -i videos/{name}/video_with_bgm.mp4 \
  -vf "subtitles=videos/{name}/podcast_audio.srt:force_style='FontName=PingFang SC,FontSize=14,PrimaryColour=&H00333333,OutlineColour=&H00FFFFFF,Bold=1,Outline=2,Shadow=0,MarginV=20'" \
  -c:v libx264 -crf 18 -preset slow -s 3840x2160 \
  -c:a copy videos/{name}/final_video.mp4
```

**关键参数**:
- `-s 3840x2160` - 强制 4K
- `-crf 18 -preset slow` - 高质量编码

---

## Step 12: Complete Publish Info (Part 2)

从 `timing.json` 生成 B站章节：

```
00:00 开场
00:23 功能介绍
00:55 演示
01:20 总结
```

格式：`MM:SS 章节标题`，每段间隔 ≥5秒。

---

## Background Music Options

Available at `~/.claude/skills/video-podcast-maker/music/`:
- `perfect-beauty-191271.mp3` - Upbeat, positive
- `snow-stevekaldes-piano-397491.mp3` - Calm piano

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Numbers in Arabic digits | Write in Chinese: "3999" → "三千九百九十九" |
| Running `npx remotion studio` | **NEVER** — use `npx remotion render` |
| Audio/video timing mismatch | Use `timing.json`, don't hardcode |
| Section not syncing | `[SECTION:name]` must match component names |
| TTS chunks too long | Keep MAX_CHARS=400 |
| Subtitle font missing | Use PingFang SC (mac), Microsoft YaHei (win) |
| Subtitle invisible on white | Use dark color `PrimaryColour=&H00333333` |
| Video blurry | Use `--video-bitrate 16M` and `-crf 18 -preset slow` |
| Not 4K | Composition 3840x2160, `scale(2)` wrapper |
| Text too small | Title 80-100px, subtitle 48-64px |
| Too much whitespace | Content ≥85% width, card 900-1100px |

---

## Requirements

### System Tools

```bash
brew install ffmpeg node  # macOS
```

### Python Dependencies

```bash
pip install azure-cognitiveservices-speech requests
```

### Node.js Dependencies

```bash
npm install remotion @remotion/cli @remotion/player
```

### Environment Variables

```bash
# Azure TTS (required)
export AZURE_SPEECH_KEY="your-azure-speech-key"
export AZURE_SPEECH_REGION="eastasia"

# Optional: AI image generation
export GEMINI_API_KEY="..."        # imagen (Google)
export DASHSCOPE_API_KEY="..."     # imagenty (阿里云)
```

### Optional: AI Image Generation

```bash
pip install google-genai pillow    # imagen
pip install dashscope requests      # imagenty
```

---

## Documentation

| Doc | Content |
|-----|---------|
| [QUICKSTART.md](docs/QUICKSTART.md) | 5分钟快速入门 |
| [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | 故障排除指南 |
| [COMPONENTS.md](docs/COMPONENTS.md) | Remotion 组件参考 |
| [VISUAL_STYLES.md](docs/VISUAL_STYLES.md) | 视觉风格规范 |
| [MEDIA_ASSETS.md](docs/MEDIA_ASSETS.md) | 素材来源推荐 |
