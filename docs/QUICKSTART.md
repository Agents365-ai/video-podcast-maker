# Video Podcast Maker 快速入门指南

5 分钟上手，从主题到成品 B站视频。

---

## 1. 环境准备

### 必需软件

| 软件 | 安装命令 (macOS) |
|------|-----------------|
| Node.js 18+ | `brew install node` |
| Python 3.8+ | `brew install python3` |
| FFmpeg | `brew install ffmpeg` |

### 必需 API 密钥

**Azure Speech** - TTS 语音合成（必需）

```bash
# 添加到 ~/.zshrc
export AZURE_SPEECH_KEY="your-azure-speech-key"
export AZURE_SPEECH_REGION="eastasia"
```

获取方式：[Azure 门户](https://portal.azure.com/) → 创建"语音服务"资源

### Python 依赖

```bash
pip install azure-cognitiveservices-speech requests
```

---

## 2. 最快路径

打开 Claude Code，直接说：

> "帮我制作一个关于 [你的主题] 的 B站视频播客"

Claude 会自动引导你完成所有步骤。无需记住任何命令。

---

## 3. 12 步工作流速览

| 步骤 | 做什么 | 产出 |
|------|--------|------|
| **0. 定方向** | 确定受众、定位、风格、时长 | `topic_definition.md` |
| **1. 调研** | WebSearch 收集资料 | `topic_research.md` |
| **2. 设计章节** | 规划 5-7 个章节 | 章节大纲 |
| **3. 写脚本** | 撰写旁白，添加 `[SECTION:xxx]` 标记 | `podcast.txt` |
| **4. 收集素材** | 截图、Logo、图片 | `public/media/{name}/` |
| **5. 发布信息** | 标题、标签、简介 | `publish_info.md` |
| **6. 封面** | Remotion 或 AI 生成 | `thumbnail_*.png` |
| **7. 生成音频** | Azure TTS | `podcast_audio.wav` + `timing.json` |
| **8. 创建视频** | 编写 Remotion 组件 | `src/remotion/` |
| **9. 渲染** | Remotion render | `output.mp4` |
| **10. 混音** | FFmpeg 叠加 BGM | `video_with_bgm.mp4` |
| **11. 字幕** | FFmpeg 烧录字幕（可选） | `final_video.mp4` |
| **12. 章节时间戳** | 从 timing.json 生成 | 更新 `publish_info.md` |

---

## 4. 关键文件一览

```
videos/{video-name}/
├── topic_definition.md      # 主题定义
├── topic_research.md        # 研究笔记
├── podcast.txt              # 旁白脚本（带 [SECTION:xxx] 标记）
├── podcast_audio.wav        # TTS 音频
├── podcast_audio.srt        # 字幕文件
├── timing.json              # 章节时间轴（驱动 Remotion 同步）
├── thumbnail_*.png          # 视频封面
├── publish_info.md          # 标题、标签、简介、章节
├── output.mp4               # Remotion 渲染（无 BGM）
├── video_with_bgm.mp4       # 含背景音乐
└── final_video.mp4          # 最终输出

public/media/{video-name}/   # Remotion 素材目录
├── hero_1.png
├── demo_screenshot.png
└── ...
```

---

## 5. 常用命令

### TTS 音频生成

```bash
# 在视频目录下运行
cd videos/{name}
python3 ~/.claude/skills/video-podcast-maker/generate_tts.py

# 调整语速
TTS_RATE="+15%" python3 ~/.claude/skills/video-podcast-maker/generate_tts.py  # 加快
TTS_RATE="-10%" python3 ~/.claude/skills/video-podcast-maker/generate_tts.py  # 放慢
```

产出：`podcast_audio.wav`, `podcast_audio.srt`, `timing.json`

### Remotion 渲染

```bash
# 渲染前：复制音频和时间轴到 public/
cp videos/{name}/podcast_audio.wav public/
cp videos/{name}/timing.json public/

# 渲染视频（4K, 16Mbps）
npx remotion render src/remotion/index.ts CompositionId videos/{name}/output.mp4 --video-bitrate 16M

# 渲染封面
npx remotion still src/remotion/index.ts Thumbnail16x9 videos/{name}/thumbnail_remotion_16x9.png

# 渲染后：清理
rm -f public/podcast_audio.wav public/timing.json
```

### BGM 混音

```bash
ffmpeg -y -i videos/{name}/output.mp4 \
  -stream_loop -1 -i ~/.claude/skills/video-podcast-maker/music/perfect-beauty-191271.mp3 \
  -filter_complex "[0:a]volume=1.0[a1];[1:a]volume=0.05[a2];[a1][a2]amix=inputs=2:duration=first[aout]" \
  -map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 192k videos/{name}/video_with_bgm.mp4
```

### 字幕烧录（可选）

```bash
ffmpeg -y -i videos/{name}/video_with_bgm.mp4 \
  -vf "subtitles=videos/{name}/podcast_audio.srt:force_style='FontName=PingFang SC,FontSize=14,PrimaryColour=&H00333333,OutlineColour=&H00FFFFFF,Bold=1,Outline=2'" \
  -c:v libx264 -crf 18 -preset slow -s 3840x2160 -c:a copy videos/{name}/final_video.mp4
```

---

## 6. podcast.txt 脚本格式

```text
[SECTION:hero]
大家好，欢迎来到本期视频。今天我们聊一个...

[SECTION:features]
它有以下三个核心功能...

[SECTION:demo]
让我演示一下...

[SECTION:summary]
总结一下，它是目前最好用的...

[SECTION:outro]
感谢观看！点赞投币收藏，关注我，下期再见！
```

**要点：**
- `[SECTION:xxx]` 标记章节，名称与 Remotion 组件对应
- `outro` 空内容时自动标记为静音，Remotion 会额外添加时长
- 英文词汇自动用美式发音

---

## 7. 下一步

- 完整文档：[SKILL.md](../SKILL.md)
- 中文说明：[README_CN.md](../README_CN.md)
- 布局规范：[FullBleedLayout.tsx](../FullBleedLayout.tsx)

**可选 API 密钥：**

```bash
# AI 封面生成
export GEMINI_API_KEY="..."        # Google Gemini (imagen)
export DASHSCOPE_API_KEY="..."     # 阿里云百炼 (中文优化)
```

---

## 常见问题

**Q: TTS 报错 "AZURE_SPEECH_KEY not set"**
A: 确保已设置环境变量并 `source ~/.zshrc`

**Q: Remotion 渲染失败**
A: 检查 `timing.json` 是否复制到 `public/`，章节名称是否与组件匹配

**Q: 视频内容缩在中间**
A: 遵循"宁可撑爆，不可留白"原则，使用 `<FullBleed>` 组件，内容宽度 ≥85%

---

作者：探索未至之境 | B站：https://space.bilibili.com/441831884
