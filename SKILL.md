---
name: video-podcast-maker
description: Use when user provides a topic and wants an automated video podcast created - handles research, script writing, TTS audio synthesis, Remotion video creation, and final MP4 output with background music
author: 探索未至之境
created: 2025-01-27
updated: 2026-02-20
bilibili: https://space.bilibili.com/441831884
---

# Video Podcast Maker

## Quick Start

> **5分钟上手？** 查看 [docs/QUICKSTART.md](docs/QUICKSTART.md)
>
> **遇到问题？** 查看 [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

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

## Design System

**使用 `remotion-design-master` skill 提供的设计系统。**

```bash
# 安装设计组件
TEMP_DIR=$(mktemp -d)
git clone --depth 1 https://github.com/Agents365-ai/remotion-design-master.git "$TEMP_DIR/rdm"
cp -r "$TEMP_DIR/rdm/src/"* src/remotion/design/
rm -rf "$TEMP_DIR"
```

设计系统包含：
- **布局组件**: FullBleed, ContentArea, CoverMedia, DualLayerMedia
- **动画组件**: FadeIn, SpringPop, SlideIn, Typewriter
- **数据展示**: DataDisplay, AnimatedCounter, ProgressBar
- **导航组件**: ChapterProgressBar, SectionIndicator
- **主题**: minimalWhite (默认), darkTech, gradientVibrant

**硬约束规则、组件文档、视觉风格** 详见 `remotion-design-master` skill。

> ⚠️ **HARD CONSTRAINT: 优先使用设计系统组件**
>
> 在 Step 8 创建视频组件时，**禁止**从零实现已有组件。必须优先检查并使用 `remotion-design-master` 提供的组件：
> - ChapterProgressBar (章节进度条) - **默认使用**（可选关闭）
> - FadeIn, SlideIn (动画) - 优先使用
> - FullBleed, ContentArea (布局) - 优先使用
>
> 如果设计系统组件不满足需求，应先扩展设计系统，而非在视频组件中重复实现。

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

### Prerequisites (One-time Setup)

在开始任何视频项目前，确保已完成以下设置：

```bash
# 1. 创建 Remotion 项目（如已有则跳过）
npx create-video@latest my-video-project
cd my-video-project

# 2. 安装设计系统
mkdir -p src/remotion/design
cp -r ~/.claude/skills/remotion-design-master/src/* src/remotion/design/

# 3. 验证
npx remotion studio  # 应打开浏览器预览
```

详细步骤见 [docs/QUICKSTART.md](docs/QUICKSTART.md)

### Video Production Steps

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
| **7.5. Component Check** | remotion-design-master | ✅ 组件清单确认 |
| **8. Create Video** | Remotion | Composition ready |
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

## Step 7.5: Design System Component Check (必做)

在创建视频组件前，**必须**检查 `remotion-design-master` 设计系统可用组件：

```bash
# 列出所有可用组件
ls ~/.claude/skills/remotion-design-master/src/components/
```

### 推荐组件清单

| 组件 | 用途 | 路径 | 使用建议 |
|------|------|------|----------|
| **ChapterProgressBar** | 底部章节进度条 | `navigation/ChapterProgressBar.tsx` | ✅ 默认使用 |
| **FadeIn** | 淡入动画 | `animations/FadeIn.tsx` | 推荐 |
| **SlideIn** | 滑入动画 | `animations/SlideIn.tsx` | 推荐 |
| **FullBleed** | 全屏布局 | `layouts/FullBleed.tsx` | 推荐 |
| **ContentArea** | 内容区域 | `layouts/ContentArea.tsx` | 推荐 |
| **Title** | 标题组件 | `ui/Title.tsx` | 推荐 |

> **注意**：ChapterProgressBar 默认启用。如需关闭，请在 Step 8 时告知 Claude。

### 验证命令

```bash
# 检查设计系统是否已安装
[ -d "src/remotion/design" ] && echo "✓ 设计系统已安装" || echo "✗ 需要安装设计系统"

# 检查 ChapterProgressBar 是否存在
[ -f "src/remotion/design/components/navigation/ChapterProgressBar.tsx" ] && echo "✓ ChapterProgressBar 可用" || echo "⚠ 需要从设计系统复制"
```

如果设计系统未安装，执行：
```bash
cp -r ~/.claude/skills/remotion-design-master/src/* src/remotion/design/
```

---

## Step 8: Create Remotion Composition

复制文件到 public/:
```bash
cp videos/{name}/podcast_audio.wav videos/{name}/timing.json public/
```

使用 `timing.json` 同步。

### 标准视频模板（必须遵循）

```tsx
import { AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame } from 'remotion'
import timingData from '../../public/timing.json'

// 章节中文名映射
const sectionNamesCN: Record<string, string> = {
  hero: '开场',
  // ... 其他章节映射
  outro: '结语',
}

// 颜色配置
const colors = { primary: '#2563eb', text: '#1f2937', muted: '#6b7280' }
const font = 'PingFang SC, -apple-system, sans-serif'

// ⚠️ 必须使用设计系统的 ChapterProgressBar 或按此模式实现
const ChapterProgressBar = () => {
  const frame = useCurrentFrame()
  const totalFrames = timingData.total_frames
  const progress = frame / totalFrames

  return (
    <div style={{
      position: 'absolute', bottom: 0, left: 0, width: '100%', height: 110,
      background: '#fff', borderTop: '2px solid #e5e7eb',
      display: 'flex', alignItems: 'center', padding: '0 50px', gap: 16,
      fontFamily: font,
    }}>
      {timingData.sections.map((ch: any) => {
        const chStart = ch.start_frame / totalFrames
        const chEnd = (ch.start_frame + ch.duration_frames) / totalFrames
        const isActive = progress >= chStart && progress < chEnd
        const isPast = progress >= chEnd
        const chProgress = isActive ? (progress - chStart) / (chEnd - chStart) : isPast ? 1 : 0

        return (
          <div key={ch.name} style={{
            flex: ch.duration_frames, // 按时长分配宽度
            height: 64, borderRadius: 32, position: 'relative', overflow: 'hidden',
            background: isActive ? colors.primary : isPast ? '#f3f4f6' : '#f9fafb',
            border: isActive ? 'none' : '2px solid #e5e7eb',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            {isActive && (
              <div style={{
                position: 'absolute', left: 0, top: 0, bottom: 0,
                width: `${chProgress * 100}%`,
                background: 'rgba(255,255,255,0.25)', borderRadius: 32,
              }} />
            )}
            <span style={{
              position: 'relative', zIndex: 1,
              color: isActive ? '#fff' : isPast ? '#374151' : '#9ca3af',
              fontSize: 32, fontWeight: isActive ? 700 : 500,
            }}>{sectionNamesCN[ch.name] || ch.name}</span>
          </div>
        )
      })}
      <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, height: 4, background: '#e5e7eb' }}>
        <div style={{ height: '100%', width: `${progress * 100}%`, background: colors.primary }} />
      </div>
    </div>
  )
}

export const MyVideo = () => (
  <AbsoluteFill style={{ background: '#fff' }}>
    <Audio src={staticFile('podcast_audio.wav')} />
    {/* 4K 内容区域 - scale(2) 容器 */}
    <AbsoluteFill style={{ transform: 'scale(2)', transformOrigin: 'top left', width: '50%', height: '50%' }}>
      {timingData.sections.map((section: any) => (
        <Sequence key={section.name} from={section.start_frame} durationInFrames={section.duration_frames}>
          <SectionComponent name={section.name} />
        </Sequence>
      ))}
    </AbsoluteFill>
    {/* ⚠️ 进度条必须放在 scale(2) 容器外部 */}
    <ChapterProgressBar />
  </AbsoluteFill>
)
```

### 关键架构说明

| 要点 | 说明 |
|------|------|
| **ChapterProgressBar 位置** | 必须放在 `scale(2)` 容器**外部**，否则宽度会被压缩 |
| **章节宽度分配** | 使用 `flex: ch.duration_frames` 按时长比例分配 |
| **进度指示** | 当前章节内显示白色进度条，底部显示总进度 |
| **4K 缩放** | 内容区域使用 `scale(2)` 从 1920×1080 放大到 3840×2160 |

**ChapterProgressBar 默认启用**，提供用户导航和进度反馈。如不需要，可在创建视频组件时告知 Claude 关闭。

---

## Step 8.5: Preview & Debug (Optional)

**Claude behavior:** Ask before skipping: "要先用 Remotion Studio 预览吗？可以在 4K 渲染前发现问题，节省时间。"

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
2. Quick preview render to check full flow
3. Final 4K render when satisfied

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
└── thumbnail_*.png      # 封面图
```

---

## Background Music Options

Available at `~/.claude/skills/video-podcast-maker/music/`:
- `perfect-beauty-191271.mp3` - Upbeat, positive
- `snow-stevekaldes-piano-397491.mp3` - Calm piano

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| **重新实现已有组件** | **优先检查 remotion-design-master，使用现有组件** |
| ChapterProgressBar 放在 scale(2) 内 | 必须放在 scale(2) 容器**外部**，否则宽度被压缩 |
| 进度条章节等宽分配 | 使用 `flex: ch.duration_frames` 按时长比例分配 |
| Numbers in Arabic digits | Write in Chinese: "3999" → "三千九百九十九" |
| Skipping preview | Use `npx remotion studio` for debugging before final render |
| Output in `out/` instead of `videos/{name}/` | Must specify full path: `npx remotion render ... videos/{name}/output.mp4` |
| Audio/video timing mismatch | Use `timing.json`, don't hardcode |
| Section not syncing | `[SECTION:name]` must match component names |
| TTS chunks too long | Keep MAX_CHARS=400 |
| Subtitle font missing | Use PingFang SC (mac), Microsoft YaHei (win) |
| Subtitle invisible on white | Use dark color `PrimaryColour=&H00333333` |
| Video blurry | Use `--video-bitrate 16M` and `-crf 18 -preset slow` |
| Not 4K | Composition 3840x2160, `scale(2)` wrapper |

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
| [MEDIA_ASSETS.md](docs/MEDIA_ASSETS.md) | 素材来源推荐 |
| **remotion-design-master** | 组件参考、视觉风格、硬约束规则 |
