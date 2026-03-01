---
name: video-podcast-maker
description: Use when user provides a topic and wants an automated video podcast created - handles research, script writing, TTS audio synthesis, Remotion video creation, and final MP4 output with background music
author: 探索未至之境
created: 2025-01-27
updated: 2026-02-27
bilibili: https://space.bilibili.com/441831884
dependencies:
  - remotion-best-practices
  - find-skills
---

> **REQUIRED: Load Remotion Best Practices First**
>
> This skill depends on `remotion-best-practices` (official Remotion best practices). **You MUST invoke it before proceeding:**
> ```
> Skill tool: skill="remotion-best-practices"
> ```

# Video Podcast Maker

## Quick Start

打开 Claude Code，直接说：**"帮我制作一个关于 [你的主题] 的 B站视频播客"**

---

## Prerequisites (One-time Setup)

### 0.1 环境检查清单

| 工具 | 检查命令 | 安装 (macOS) |
|------|----------|--------------|
| Node.js 18+ | `node -v` | `brew install node` |
| Python 3.8+ | `python3 --version` | `brew install python3` |
| FFmpeg | `ffmpeg -version` | `brew install ffmpeg` |

### 0.2 API 密钥

```bash
# Azure Speech (必需) - 添加到 ~/.zshrc
export AZURE_SPEECH_KEY="your-azure-speech-key"
export AZURE_SPEECH_REGION="eastasia"

# 验证
echo $AZURE_SPEECH_KEY  # 应显示你的密钥
```

获取方式：[Azure 门户](https://portal.azure.com/) → 创建"语音服务"资源

### 0.3 Python 依赖

```bash
pip install azure-cognitiveservices-speech requests
```

### 0.4 Remotion 项目设置

```bash
# 创建 Remotion 项目（如已有则跳过）
npx create-video@latest my-video-project
cd my-video-project
npm i  # 安装依赖

# 验证
npx remotion studio  # 应打开浏览器预览
```

### 0.5 快速验证

```bash
# 一键检查所有依赖
echo "=== 环境检查 ===" && \
node -v && \
python3 --version && \
ffmpeg -version 2>&1 | head -1 && \
[ -n "$AZURE_SPEECH_KEY" ] && echo "✓ AZURE_SPEECH_KEY 已设置" || echo "✗ AZURE_SPEECH_KEY 未设置"
```

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

## Technical Rules

以下是视频制作的技术硬约束，其他视觉设计和布局由 Claude 根据内容自由发挥：

| Rule | Requirement |
|------|-------------|
| **4K Output** | 3840×2160, use `scale(2)` wrapper over 1920×1080 design space |
| **Content Width** | ≥85% of screen width, no tiny centered boxes |
| **Bottom Safe Zone** | Bottom 100px reserved for subtitles |
| **Audio Sync** | All animations driven by `timing.json` timestamps |
| **Thumbnail** | Must generate both 16:9 (1920×1080) AND 4:3 (1200×900) |
| **Font** | PingFang SC / Noto Sans SC for Chinese text |

---

## Visual Design Reference

以下尺寸来自已验证的生产视频（1080p 设计空间，`scale(2)` 放大到 4K），**必须遵循**：

### Typography Scale (1080p design space)

| Element | Size | Weight | When to Use |
|---------|------|--------|-------------|
| **Hero Title** | 72–120px | 800 | Opening section, brand moment |
| **Section Title** | 72–80px | 700–800 | Each section's main heading |
| **Large Emphasis** | 40–68px | 600–700 | Key statements, conclusions, quotes |
| **Subtitle / Description** | 30–40px | 500–600 | Under section titles, subheadings |
| **Card Title** | 34–38px | 700 | Feature cards, list group headers |
| **Body Text** | 26–34px | 500–600 | Paragraphs, list items, descriptions |
| **Tags / Pills** | 20–26px | 600 | Labels, badges, categories |

> **Anti-patterns (NEVER do):**
> - No text smaller than 18px in 1080p design space
> - No hero title smaller than 72px
> - No section title smaller than 60px
> - No card/body text smaller than 24px

### Layout Patterns

| Pattern | Specification |
|---------|---------------|
| **Card** | `borderRadius: 20–28px`, `padding: 28–44px`, `border: 1–3px solid`, `boxShadow: 0 10px 40px rgba(0,0,0,0.08)` |
| **Section Padding** | `padding: 40–80px` on content sections, `60–100px` on hero sections |
| **Grid Gap** | `gap: 20–40px` between cards/items |
| **Hero / Impact** | Full viewport centered (flexbox center), no excessive padding |
| **Content Max Width** | 800–950px for centered blocks, or full width with padding |

### FadeIn Animation Pattern

```tsx
const FadeIn = ({ children, delay = 0 }: { children: React.ReactNode; delay?: number }) => {
  const frame = useCurrentFrame()
  const opacity = interpolate(frame - delay, [0, 15], [0, 1], { extrapolateRight: 'clamp' })
  const y = interpolate(frame - delay, [0, 15], [20, 0], { extrapolateRight: 'clamp' })
  return <div style={{ opacity, transform: `translateY(${y}px)` }}>{children}</div>
}
```

### Glow Effect Pattern

```tsx
const Glow = ({ color, x, y, size }: { color: string; x: string; y: string; size: number }) => (
  <div style={{
    position: 'absolute', left: x, top: y, width: size, height: size,
    background: `radial-gradient(circle, ${color}08 0%, transparent 70%)`,
    transform: 'translate(-50%, -50%)', pointerEvents: 'none',
  }} />
)
```

### Progress Bar Specification (native 4K, outside `scale(2)`)

| Property | Value |
|----------|-------|
| **Bar Height** | 130px |
| **Background** | `#fff`, `borderTop: 2px solid #e5e7eb` |
| **Padding** | `0 60px`, `gap: 20px` |
| **Pill Height** | 76px, `borderRadius: 38px` |
| **Pill Width** | `flex: ch.duration_frames` (proportional by chapter length) |
| **Active State** | Solid primary color bg, white text, weight 700, inner progress overlay `rgba(255,255,255,0.25)` |
| **Past State** | `#f3f4f6` bg |
| **Future State** | `#f9fafb` bg, `2px solid #e5e7eb` border |
| **Text Size** | 38px |
| **Bottom Line** | 5px full-width, `#e5e7eb` bg with primary color fill |

---

## 文件路径与命名规范

### 目录结构

```
project-root/                           # Remotion 项目根目录
├── src/remotion/                       # Remotion 源码
│   ├── compositions/                   # 视频 Composition 定义
│   ├── Root.tsx                        # Remotion 入口
│   └── index.ts                        # 导出
│
├── public/media/{video-name}/          # 素材目录 (Remotion staticFile() 可访问)
│   ├── {section}_{index}.{ext}         # 通用素材
│   ├── {section}_screenshot.png        # 网页截图
│   ├── {section}_logo.png              # Logo
│   ├── {section}_web_{index}.{ext}     # 网络图片
│   └── {section}_ai.png                # AI 生成图片
│
├── videos/{video-name}/                # 视频项目资产 (非 Remotion 代码)
│   ├── topic_definition.md             # Step 0: 主题定义
│   ├── topic_research.md               # Step 1: 研究资料
│   ├── podcast.txt                     # Step 3: 旁白脚本
│   ├── media_manifest.json             # Step 4: 素材清单
│   ├── publish_info.md                 # Step 5+12: 发布信息
│   ├── podcast_audio.wav               # Step 7: TTS 音频
│   ├── podcast_audio.srt               # Step 7: 字幕文件
│   ├── timing.json                     # Step 7: 时间轴
│   ├── thumbnail_*.png                 # Step 6: 封面
│   ├── output.mp4                      # Step 9: Remotion 输出
│   ├── video_with_bgm.mp4              # Step 10: 添加 BGM
│   ├── final_video.mp4                 # Step 11: 最终输出
│   └── bgm.mp3                         # 背景音乐
│
└── remotion.config.ts                  # Remotion 配置
```

> ⚠️ **重要**: Remotion 渲染时必须指定完整输出路径，否则默认输出到 `out/`:
> ```bash
> npx remotion render src/remotion/index.ts CompositionId videos/{name}/output.mp4
> ```

### 命名规则

**视频名称 `{video-name}`**: 全小写英文，连字符分隔（如 `reference-manager-comparison`）

**章节名称 `{section}`**: 全小写英文，下划线分隔，与 `[SECTION:xxx]` 一致

**缩略图命名** (⚠️ 16:9 和 4:3 **都是必须的**，B站不同位置使用不同比例):
| 类型 | 16:9 (播放页横版) | 4:3 (推荐流/动态竖版) |
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

### Progress Tracking

在 Step 0 开始时，使用 `TaskCreate` 创建所有步骤的 tasks，每步开始时 `TaskUpdate` 为 `in_progress`，完成后标记 `completed`。

| Step | Tool | Output |
|------|------|--------|
| **0. Define Direction** | `brainstorming` | `topic_definition.md` |
| **1. Research** | WebSearch, WebFetch | `topic_research.md` |
| **2. Design Sections** | `brainstorming` | 5-7 sections plan |
| **3. Write Script** | Claude | `podcast.txt` |
| **4. Collect Media** | Playwright/WebSearch | `media_manifest.json` |
| **5. Publish Info (Part 1)** | Claude | `publish_info.md` |
| **6. Thumbnail** | Remotion/imagen/imagenty | `thumbnail_*.png` |
| **7. Generate Audio** | generate_tts.py | `.wav`, `.srt`, `timing.json` |
| **8. Create Video** | Remotion | Composition ready |
| **8.5. Studio Preview** | remotion studio | ✅ Preview verified |
| **9. Render** | remotion render | `output.mp4` |
| **10. Add BGM** | FFmpeg | `video_with_bgm.mp4` |
| **11. Subtitles** | FFmpeg + SRT | `final_video.mp4` |
| **12. Publish Info (Part 2)** | Claude | Update chapters |
| **13. Verify** | Claude | Verification report |
| **14. Cleanup** | Claude | Remove temp files |

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

使用 `brainstorming` skill 确认：
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

### Content Density Selection

Before designing, assign each section a density tier based on content volume:

| Tier | Items | Best For |
|------|-------|----------|
| **Impact** | 1 | Hook, hero, CTA, brand moment — largest text |
| **Standard** | 2-3 | Features, comparison, demo |
| **Compact** | 4-6 | Feature grid, ecosystem |
| **Dense** | 6+ | Data tables, detailed comparisons — smallest text |

Example section plan with tiers:
```
hero: Impact (1 brand moment)
features: Standard (3 feature cards)
ecosystem: Compact (5 integration icons)
performance: Standard (2 comparison bars)
cta: Impact (1 call-to-action)
```

### Title Position Confirmation

使用 AskUserQuestion 询问用户标题位置偏好：

| 位置 | 风格 | 适用场景 |
|------|------|----------|
| **顶部居中** | 视频风格 | 大多数视频内容 (推荐) |
| **顶部左侧** | 演示风格 | 商务/正式内容 |
| **全屏居中** | 英雄风格 | 仅用于 Hook/Hero 场景 |

**规则：** 单个视频内保持标题位置一致。

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
   - **Unsplash** (https://unsplash.com) - 高质量免费图片
   - **Pexels** (https://pexels.com) - 免费 CC0 图片
   - **Pixabay** (https://pixabay.com) - 免费素材库
   - **unDraw** (https://undraw.co) - 开源 SVG 插图
   - **StockSnap** (https://stocksnap.io) - 高清免费图片
   - **Simple Icons** (https://simpleicons.org) - 品牌 SVG 图标
5. **AI 生成** - 使用 imagen skill（需用户确认）

如果用户选择 AI 生成，调用 imagen skill 生成图片：
```
使用 imagen skill 生成：[图片描述]
```

素材保存到 `public/media/{video-name}/`，生成 `media_manifest.json`。


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

⚠️ **必须生成两个比例**: 16:9 (播放页) 和 4:3 (推荐流/动态)，缺一不可

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

### 多音字/发音校正 (SSML Phoneme)

TTS 脚本支持三种方式校正发音，优先级从高到低：

**1. 内联标注** (最高优先级) - 在 podcast.txt 中直接标注：
```text
每个执行器[zhí xíng qì]都有自己的上下文窗口
如果不合格，就打回重做[chóng zuò]
```

**2. 项目词典** - 在 `videos/{name}/phonemes.json` 中定义：
```json
{
  "执行器": "zhí xíng qì",
  "重做": "chóng zuò",
  "一行命令": "yì háng mìng lìng"
}
```

**3. 内置词典** - 预置常见多音字（自动应用）：

| 词语 | 拼音 | 说明 |
|------|------|------|
| 执行/运行/并行 | xíng | "行"作"执行"义 |
| 一行命令/代码行 | háng | "行"作"行列"义 |
| 重做/重新/重复 | chóng | "重"作"重复"义 |

**拼音格式**: 使用带声调符号的拼音（如 `zhí xíng qì`），脚本会自动转换为 Azure SAPI 格式。

**Outputs**: `podcast_audio.wav`, `podcast_audio.srt`, `timing.json`
---

## Step 8: Create Remotion Composition

复制文件到 public/:
```bash
cp videos/{name}/podcast_audio.wav videos/{name}/timing.json public/
```

使用 `timing.json` 同步。

### 标准视频模板（必须遵循）

使用 `templates/Video.tsx` 作为起点，已包含完整实现（4K 缩放、章节进度条、音频集成）。

```bash
cp ~/.claude/skills/video-podcast-maker/templates/Video.tsx src/remotion/
cp ~/.claude/skills/video-podcast-maker/templates/Root.tsx src/remotion/
```

模板中的 ChapterProgressBar 是**自包含实现**，无需额外依赖。

### 关键架构说明

| 要点 | 说明 |
|------|------|
| **ChapterProgressBar 位置** | 必须放在 `scale(2)` 容器**外部**，否则宽度会被压缩 |
| **章节宽度分配** | 使用 `flex: ch.duration_frames` 按时长比例分配 |
| **进度指示** | 当前章节内显示白色进度条，底部显示总进度 |
| **4K 缩放** | 内容区域使用 `scale(2)` 从 1920×1080 放大到 3840×2160 |

**ChapterProgressBar 默认启用**，提供用户导航和进度反馈。如不需要，可在创建视频组件时告知 Claude 关闭。

### 一键三连片尾

**Claude behavior:** 使用 AskUserQuestion 询问用户片尾一键三连的实现方式：

> "片尾一键三连动画如何实现？"
>
> - **使用预制 MP4 动画（推荐）** — 直接嵌入专业制作的一键三连动画视频，黑白两版可选
> - **Remotion 代码生成** — 用 Remotion 组件渲染自定义一键三连动画

**预制 MP4 用法：**

```bash
# 复制到项目 public 目录
cp ~/.claude/skills/video-podcast-maker/assets/bilibili-triple-white.mp4 public/media/{video-name}/
# 或黑色背景版本
cp ~/.claude/skills/video-podcast-maker/assets/bilibili-triple-black.mp4 public/media/{video-name}/
```

```tsx
// 在 outro section 中使用 <OffthreadVideo> 嵌入
import { OffthreadVideo, staticFile } from "remotion";

// 白色背景版
<OffthreadVideo src={staticFile("media/{video-name}/bilibili-triple-white.mp4")} />
// 黑色背景版
<OffthreadVideo src={staticFile("media/{video-name}/bilibili-triple-black.mp4")} />
```

可用素材：
| 文件 | 背景 | 适用场景 |
|------|------|----------|
| `bilibili-triple-white.mp4` | 白色 | 默认白色主题视频 |
| `bilibili-triple-black.mp4` | 黑色 | 深色主题视频 |

---

## Step 8.5: Studio Preview

**Claude behavior:** 使用 AskUserQuestion 询问用户：

> "建议先启动 Remotion Studio 预览，迭代修改满意后再渲染最终 4K 视频，可以节省大量渲染时间。是否启动预览？"
>
> - **是（推荐）** — 启动 Studio 预览，迭代修改，满意后再执行 Step 9 渲染
> - **否** — 跳过预览，直接渲染 4K 视频

Use Remotion Studio for real-time preview before final render:

```bash
# Start Remotion Studio (opens browser)
npx remotion studio src/remotion/index.ts
```

**Studio features:**
- Real-time preview with timeline scrubbing
- Hot reload on code changes
- Visual debugging of animations and layout

**Alternative: Quick preview render**
```bash
# 720p preview (~4x faster than 4K)
npx remotion render src/remotion/index.ts CompositionId videos/{name}/preview.mp4 --scale 0.33 --crf 28

# Preview first 10 seconds only
npx remotion render src/remotion/index.ts CompositionId videos/{name}/preview.mp4 --frames 0-300 --scale 0.5

# Static frame screenshots
npx remotion still src/remotion/index.ts CompositionId videos/{name}/frame_0.png --frame 0
npx remotion still src/remotion/index.ts CompositionId videos/{name}/frame_300.png --frame 300
```

**Recommended workflow:**
1. Use `remotion studio` for iterative development
2. Check pronunciation — if incorrect, fix in `podcast.txt` (inline `[拼音]`) or `phonemes.json`, re-run `generate_tts.py`, copy to `public/`
3. Quick preview render to check full flow
4. Final 4K render when satisfied

---

## Step 9: Render Video

> Use `npx remotion studio` for preview, then render directly for final output.

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
cp ~/.claude/skills/video-podcast-maker/assets/perfect-beauty-191271.mp3 videos/{name}/bgm.mp3

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

**Claude behavior:** Ask before skipping: "需要烧录字幕吗？字幕可以提高视频的可访问性。"

如不需要字幕：
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

## Step 13: Verify Output

视频完成后，执行以下验证：

### 13.1 文件存在性检查

```bash
VIDEO_DIR="videos/{name}"
echo "=== 文件检查 ==="
for f in podcast.txt podcast_audio.wav podcast_audio.srt timing.json output.mp4 final_video.mp4; do
  [ -f "$VIDEO_DIR/$f" ] && echo "✓ $f" || echo "✗ $f 缺失"
done
```

### 13.2 技术指标验证

```bash
echo "=== 技术指标 ==="
# 分辨率
RES=$(ffprobe -v quiet -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "$VIDEO_DIR/final_video.mp4")
[ "$RES" = "3840,2160" ] && echo "✓ 分辨率: 3840x2160 (4K)" || echo "✗ 分辨率: $RES (非4K)"

# 时长
DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$VIDEO_DIR/final_video.mp4" | cut -d. -f1)
echo "✓ 时长: ${DUR}s"

# 编码
CODEC=$(ffprobe -v quiet -select_streams v:0 -show_entries stream=codec_name -of csv=p=0 "$VIDEO_DIR/final_video.mp4")
echo "✓ 视频编码: $CODEC"

# 文件大小
SIZE=$(ls -lh "$VIDEO_DIR/final_video.mp4" | awk '{print $5}')
echo "✓ 文件大小: $SIZE"
```

### 13.3 验证报告模板

完成验证后，向用户报告：

```
=== 验证完成 ===
✓ 文件完整性: 6/6
✓ 分辨率: 3840x2160
✓ 时长: XXs
✓ 编码: h264
✓ 大小: XXX MB

是否需要清理临时文件？(Step 14)
```

---

## Step 14: Cleanup (可选)

**Claude behavior:** Ask before skipping: "要清理临时文件吗？可以释放磁盘空间，但会删除中间产物。"

### 14.1 列出临时文件

执行前，先向用户展示将被删除的文件：

```bash
VIDEO_DIR="videos/{name}"
echo "=== 将删除的临时文件 ==="
ls -lh "$VIDEO_DIR"/part_*.wav 2>/dev/null | awk '{print $9, "(" $5 ")"}'
ls -lh "$VIDEO_DIR"/concat_list.txt 2>/dev/null | awk '{print $9, "(" $5 ")"}'
ls -lh "$VIDEO_DIR"/output.mp4 2>/dev/null | awk '{print $9, "(" $5 ")"}'
ls -lh "$VIDEO_DIR"/video_with_bgm.mp4 2>/dev/null | awk '{print $9, "(" $5 ")"}'
echo ""
echo "=== 将保留的文件 ==="
ls -lh "$VIDEO_DIR"/final_video.mp4 "$VIDEO_DIR"/podcast_audio.wav "$VIDEO_DIR"/podcast_audio.srt "$VIDEO_DIR"/timing.json "$VIDEO_DIR"/podcast.txt 2>/dev/null | awk '{print $9, "(" $5 ")"}'
```

### 14.2 用户确认

**询问用户**:
> 以上临时文件将被删除，保留最终成品和源文件。是否继续？

### 14.3 执行清理

用户确认后执行：

```bash
VIDEO_DIR="videos/{name}"
rm -f "$VIDEO_DIR"/part_*.wav
rm -f "$VIDEO_DIR"/concat_list.txt
rm -f "$VIDEO_DIR"/output.mp4
rm -f "$VIDEO_DIR"/video_with_bgm.mp4
echo "✓ 临时文件已清理"
```

### 14.4 清理后文件结构

```
videos/{name}/
├── final_video.mp4      # 最终成品
├── podcast.txt          # 原始脚本
├── podcast_audio.wav    # 音频
├── podcast_audio.srt    # 字幕
├── timing.json          # 时间轴
├── topic_research.md    # 研究资料
├── publish_info.md      # 发布信息
├── thumbnail_*_16x9.png # 封面图 16:9 (必须)
└── thumbnail_*_4x3.png  # 封面图 4:3 (必须)
```

---

## Background Music Options

Available at `~/.claude/skills/video-podcast-maker/assets/`:
- `perfect-beauty-191271.mp3` - Upbeat, positive
- `snow-stevekaldes-piano-397491.mp3` - Calm piano

---

## Troubleshooting (常见问题)

### TTS: Azure API 密钥错误

**症状**: `Error: Authentication failed`, `HTTP 401 Unauthorized`

**解决方案**:
```bash
# 检查环境变量
echo $AZURE_SPEECH_KEY
echo $AZURE_SPEECH_REGION

# 设置环境变量
export AZURE_SPEECH_KEY="your-key-here"
export AZURE_SPEECH_REGION="eastasia"
```

---

### FFmpeg: BGM 混音问题

**症状**: BGM 音量过大盖住人声，BGM 结尾突然中断

**解决方案**:
```bash
# 基础混音（人声为主，BGM 降低）
ffmpeg -i voice.mp3 -i bgm.mp3 \
  -filter_complex "[0:a]volume=1.0[voice];[1:a]volume=0.15[bgm];[voice][bgm]amix=inputs=2:duration=first" \
  -ac 2 output.mp3

# 带淡入淡出的混音
ffmpeg -i voice.mp3 -i bgm.mp3 \
  -filter_complex "
    [0:a]volume=1.0[voice];
    [1:a]volume=0.15,afade=t=in:st=0:d=2,afade=t=out:st=58:d=2[bgm];
    [voice][bgm]amix=inputs=2:duration=first
  " output.mp3
```

---

### 快速检查清单

**渲染前检查**:
- [ ] 所有素材文件存在
- [ ] timing.json 格式正确
- [ ] 音频时长与 timing 匹配
- [ ] 环境变量已设置
- [ ] 磁盘空间充足 (>20GB for 4K)

**渲染后检查**:
- [ ] 视频时长正确
- [ ] 音画同步
- [ ] 字幕显示正常
- [ ] 无黑屏/空白帧
