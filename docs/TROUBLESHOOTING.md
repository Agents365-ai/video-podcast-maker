# Video Podcast Maker 故障排除指南

本文档涵盖视频播客制作工具链中常见问题的诊断和解决方案。

---

## 目录

1. [TTS 语音合成问题](#1-tts-语音合成问题)
2. [Remotion 渲染问题](#2-remotion-渲染问题)
3. [FFmpeg 后处理问题](#3-ffmpeg-后处理问题)
4. [布局和显示问题](#4-布局和显示问题)
5. [文件和路径问题](#5-文件和路径问题)

---

## 1. TTS 语音合成问题

### 1.1 Azure API 密钥错误

**症状**
```
Error: Authentication failed
Error: Invalid subscription key
HTTP 401 Unauthorized
```

**原因**
- API Key 未设置或已过期
- Region 配置错误
- 订阅已到期或超出配额

**解决方案**
```bash
# 检查环境变量
echo $AZURE_TTS_KEY
echo $AZURE_TTS_REGION

# 设置环境变量
export AZURE_TTS_KEY="your-key-here"
export AZURE_TTS_REGION="eastasia"  # 或 eastus, westus2 等

# 测试 API 连通性
curl -X POST "https://${AZURE_TTS_REGION}.tts.speech.microsoft.com/cognitiveservices/v1" \
  -H "Ocp-Apim-Subscription-Key: ${AZURE_TTS_KEY}" \
  -H "Content-Type: application/ssml+xml" \
  -H "X-Microsoft-OutputFormat: audio-16khz-128kbitrate-mono-mp3" \
  -d '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="zh-CN"><voice name="zh-CN-XiaoxiaoNeural">测试</voice></speak>' \
  -o test.mp3
```

**预防**
- 将 API Key 存储在 `.env` 文件中
- 定期检查 Azure 订阅状态
- 设置配额告警

---

### 1.2 音频质量问题

**症状**
- 音频听起来模糊或有噪音
- 音量过大或过小
- 音频采样率不匹配

**原因**
- 输出格式设置不当
- 采样率与项目不匹配
- 压缩过度

**解决方案**
```bash
# 检查音频信息
ffprobe -v quiet -show_format -show_streams audio.mp3

# 推荐的高质量输出格式
# audio-48khz-192kbitrate-mono-mp3 (高质量)
# audio-24khz-160kbitrate-mono-mp3 (平衡)

# 音频标准化
ffmpeg -i input.mp3 -af "loudnorm=I=-16:TP=-1.5:LRA=11" output.mp3

# 转换采样率
ffmpeg -i input.mp3 -ar 48000 output.mp3
```

**预防**
- 统一使用 48kHz 采样率
- 使用 `audio-48khz-192kbitrate-mono-mp3` 格式
- 在合成后检查音频质量

---

### 1.3 中英文发音问题

**症状**
- 英文单词被读成拼音
- 中文夹杂英文时断句错误
- 专有名词发音错误

**原因**
- SSML 语言标签缺失
- 未使用 `<lang>` 切换语言
- 词汇表 (lexicon) 未配置

**解决方案**
```xml
<!-- 正确的中英文混合 SSML -->
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"
       xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="zh-CN">
  <voice name="zh-CN-XiaoxiaoNeural">
    今天我们来聊聊
    <lang xml:lang="en-US">Python</lang>
    编程语言。
  </voice>
</speak>

<!-- 使用 phoneme 指定发音 -->
<phoneme alphabet="sapi" ph="pai3 sen1">Python</phoneme>
```

```python
# 自动检测并包装英文
import re

def wrap_english(text):
    pattern = r'([a-zA-Z]+(?:\s+[a-zA-Z]+)*)'
    return re.sub(pattern, r'<lang xml:lang="en-US">\1</lang>', text)
```

**预防**
- 在脚本预处理阶段检测语言切换点
- 维护常见英文词汇的发音映射表
- 测试关键专有名词的发音

---

### 1.4 多音字处理

**症状**
- "重要" 被读成 "chóng yào" 而不是 "zhòng yào"
- "银行" 被读成 "yín xíng" 而不是 "yín háng"
- "长大" 被读成 "cháng dà" 而不是 "zhǎng dà"

**原因**
- TTS 引擎对多音字的上下文理解有限
- 未使用拼音注释

**解决方案**
```xml
<!-- 使用 phoneme 指定拼音 -->
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="zh-CN">
  <voice name="zh-CN-XiaoxiaoNeural">
    这件事很
    <phoneme alphabet="sapi" ph="zhong4">重</phoneme>要。
  </voice>
</speak>

<!-- 使用 say-as 标签 -->
<say-as interpret-as="characters">重</say-as>
```

```python
# 常见多音字映射表
polyphonic_chars = {
    '重要': '<phoneme alphabet="sapi" ph="zhong4 yao4">重要</phoneme>',
    '银行': '<phoneme alphabet="sapi" ph="yin2 hang2">银行</phoneme>',
    '长大': '<phoneme alphabet="sapi" ph="zhang3 da4">长大</phoneme>',
    '数据': '<phoneme alphabet="sapi" ph="shu4 ju4">数据</phoneme>',
    '行为': '<phoneme alphabet="sapi" ph="xing2 wei2">行为</phoneme>',
}

def fix_polyphonic(text):
    for word, ssml in polyphonic_chars.items():
        text = text.replace(word, ssml)
    return text
```

**预防**
- 建立项目专属的多音字词典
- 在脚本审核阶段标注多音字
- 使用 TTS 预听功能验证发音

---

### 1.5 语速控制问题

**症状**
- 语音过快听不清
- 语音过慢拖沓
- 不同段落速度不一致

**原因**
- prosody rate 设置不当
- 未考虑内容类型差异

**解决方案**
```xml
<!-- 使用 prosody 控制语速 -->
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="zh-CN">
  <voice name="zh-CN-XiaoxiaoNeural">
    <!-- 正常速度 -->
    <prosody rate="0%">这是正常语速的内容。</prosody>

    <!-- 慢速（重要内容） -->
    <prosody rate="-20%">这是需要强调的重要内容。</prosody>

    <!-- 快速（过渡内容） -->
    <prosody rate="+15%">这是快速过渡的内容。</prosody>

    <!-- 使用具体值 -->
    <prosody rate="medium">中等语速</prosody>
    <prosody rate="slow">慢速</prosody>
  </voice>
</speak>
```

```python
# 根据内容类型设置语速
def get_rate_for_content(content_type):
    rates = {
        'intro': '-10%',      # 开场白稍慢
        'explanation': '-15%', # 解释性内容更慢
        'transition': '+10%',  # 过渡内容稍快
        'conclusion': '-5%',   # 结尾稍慢
        'normal': '0%'
    }
    return rates.get(content_type, '0%')
```

**预防**
- 为不同内容类型预设语速模板
- 整体音频时长控制在预期范围内
- 测试时检查是否与视频节奏匹配

---

## 2. Remotion 渲染问题

### 2.1 Module not found 错误

**症状**
```
Error: Cannot find module '@remotion/player'
Error: Cannot find module './components/MyComponent'
Module not found: Can't resolve 'react'
```

**原因**
- 依赖未安装
- 路径大小写错误 (macOS/Linux 差异)
- package.json 版本冲突

**解决方案**
```bash
# 清理并重新安装依赖
rm -rf node_modules package-lock.json
npm install

# 检查 Remotion 相关依赖
npm ls | grep remotion

# 确保所有 Remotion 包版本一致
npm install @remotion/cli@latest @remotion/renderer@latest remotion@latest

# 检查文件是否存在（注意大小写）
ls -la src/components/

# 验证导入路径
# 错误: import { MyComp } from './components/mycomp'
# 正确: import { MyComp } from './components/MyComp'
```

**预防**
- 使用 `npm ci` 而不是 `npm install` 确保一致性
- 在 `.gitattributes` 中设置 `* text=auto`
- 定期运行 `npm outdated` 检查更新

---

### 2.2 黑屏问题

**症状**
- 渲染输出为纯黑视频
- 预览正常但渲染黑屏
- 部分帧黑屏

**原因**
- 异步数据未加载完成
- 组件渲染错误被静默吞掉
- delayRender/continueRender 未正确配对

**解决方案**
```tsx
// 正确使用 delayRender
import { delayRender, continueRender, useCurrentFrame } from 'remotion';

export const MyComponent: React.FC = () => {
  const [data, setData] = useState(null);
  const [handle] = useState(() => delayRender('Loading data...'));

  useEffect(() => {
    fetch('/data.json')
      .then(res => res.json())
      .then(data => {
        setData(data);
        continueRender(handle);
      })
      .catch(err => {
        console.error('Data load failed:', err);
        continueRender(handle); // 错误时也要调用！
      });
  }, [handle]);

  if (!data) return null;

  return <div>{/* render content */}</div>;
};
```

```bash
# 启用详细日志排查问题
npx remotion render src/index.tsx MyComposition out.mp4 --log=verbose

# 单独渲染某一帧检查
npx remotion still src/index.tsx MyComposition frame.png --frame=100
```

**预防**
- 始终为 `delayRender` 提供描述字符串
- 在 catch 块中也调用 `continueRender`
- 设置合理的超时时间

---

### 2.3 视频模糊

**症状**
- 输出视频不清晰
- 文字边缘锯齿明显
- 图片质量下降

**原因**
- CRF 值过高（质量过低）
- 缩放导致的模糊
- 源素材分辨率不足

**解决方案**
```bash
# 使用更低的 CRF 值（18-23 推荐）
npx remotion render src/index.tsx MyComposition out.mp4 \
  --codec=h264 \
  --crf=18 \
  --pixel-format=yuv420p

# 检查源图片分辨率
ffprobe -v quiet -show_entries stream=width,height input.jpg

# 4K 视频推荐设置
npx remotion render src/index.tsx MyComposition out.mp4 \
  --width=3840 \
  --height=2160 \
  --crf=18 \
  --pixel-format=yuv420p
```

```tsx
// 确保图片使用正确的尺寸
<Img
  src={imgSrc}
  style={{
    width: '100%',
    height: '100%',
    objectFit: 'cover'
  }}
/>

// 避免小图片放大
// 4K 视频中，背景图至少需要 3840x2160
```

**预防**
- 源素材分辨率应 >= 输出分辨率
- CRF 值保持在 18-23 之间
- 文字使用矢量字体而非图片

---

### 2.4 4K 分辨率问题

**症状**
- 4K 渲染失败
- 内存不足错误
- 渲染速度极慢

**原因**
- 系统内存不足
- 浏览器进程限制
- 并发度过高

**解决方案**
```bash
# 限制并发数
npx remotion render src/index.tsx MyComposition out.mp4 \
  --width=3840 \
  --height=2160 \
  --concurrency=2

# 增加 Node.js 内存限制
NODE_OPTIONS="--max-old-space-size=8192" npx remotion render ...

# 分段渲染后合并
npx remotion render src/index.tsx MyComposition part1.mp4 --frames=0-500
npx remotion render src/index.tsx MyComposition part2.mp4 --frames=501-1000

# 合并视频片段
ffmpeg -f concat -safe 0 -i <(echo "file 'part1.mp4'"; echo "file 'part2.mp4'") \
  -c copy output.mp4
```

```tsx
// 在 remotion.config.ts 中配置
import { Config } from '@remotion/cli/config';

Config.setChromiumOpenGlRenderer('angle');
Config.setDelayRenderTimeoutInMilliseconds(60000);
```

**预防**
- 4K 渲染建议至少 16GB 内存
- 使用 SSD 存储临时文件
- 长视频考虑分段渲染

---

### 2.5 长视频性能问题

**症状**
- 渲染时间过长
- 中途崩溃
- 磁盘空间不足

**原因**
- 临时文件过多
- 内存累积泄漏
- 磁盘 I/O 瓶颈

**解决方案**
```bash
# 检查临时目录空间
df -h /tmp

# 清理 Remotion 临时文件
rm -rf /tmp/remotion-*

# 使用自定义临时目录
TMPDIR=/path/to/large/disk npx remotion render ...

# 分段渲染策略
#!/bin/bash
TOTAL_FRAMES=18000
CHUNK_SIZE=1000
OUTPUT_DIR="./chunks"

mkdir -p $OUTPUT_DIR

for ((i=0; i<TOTAL_FRAMES; i+=CHUNK_SIZE)); do
  END=$((i + CHUNK_SIZE - 1))
  if [ $END -ge $TOTAL_FRAMES ]; then
    END=$((TOTAL_FRAMES - 1))
  fi
  npx remotion render src/index.tsx MyComp "$OUTPUT_DIR/chunk_$i.mp4" \
    --frames=$i-$END --concurrency=4
done

# 合并所有片段
ls $OUTPUT_DIR/chunk_*.mp4 | sort -V | \
  sed "s/^/file '/" | sed "s/$/'/" > concat.txt
ffmpeg -f concat -safe 0 -i concat.txt -c copy final.mp4
```

**预防**
- 预估渲染时间和磁盘需求
- 设置监控告警
- 使用 CI/CD 服务器渲染长视频

---

### 2.6 timing.json 同步问题

**症状**
- 音频与画面不同步
- 字幕出现时间错误
- 段落切换突兀

**原因**
- timing.json 时间戳单位错误
- 帧率计算不匹配
- 音频文件时长与记录不符

**解决方案**
```python
# 验证 timing.json 格式
import json

def validate_timing(timing_path, fps=30):
    with open(timing_path) as f:
        timing = json.load(f)

    for i, segment in enumerate(timing['segments']):
        # 检查必需字段
        assert 'start' in segment, f"Segment {i}: missing 'start'"
        assert 'end' in segment, f"Segment {i}: missing 'end'"
        assert 'text' in segment, f"Segment {i}: missing 'text'"

        # 检查时间单位（应该是秒，不是毫秒）
        if segment['end'] > 10000:
            print(f"Warning: Segment {i} end={segment['end']}, might be in ms?")

        # 检查连续性
        if i > 0:
            prev_end = timing['segments'][i-1]['end']
            if abs(segment['start'] - prev_end) > 0.1:
                print(f"Gap between segment {i-1} and {i}: {segment['start'] - prev_end}s")

    print(f"Total duration: {timing['segments'][-1]['end']}s")
    print(f"Total frames at {fps}fps: {int(timing['segments'][-1]['end'] * fps)}")

validate_timing('timing.json')
```

```bash
# 获取实际音频时长
ffprobe -v quiet -show_entries format=duration -of csv=p=0 audio.mp3

# 对比 timing.json 中的总时长
python3 -c "
import json
with open('timing.json') as f:
    t = json.load(f)
print(f\"Timing total: {t['segments'][-1]['end']}s\")
"
```

```tsx
// Remotion 中正确使用 timing
const frame = useCurrentFrame();
const fps = useVideoConfig().fps;
const currentTime = frame / fps;

// 找到当前时间对应的段落
const currentSegment = timing.segments.find(
  s => currentTime >= s.start && currentTime < s.end
);
```

**预防**
- 统一使用秒作为时间单位
- TTS 生成后立即验证时长
- 在渲染前检查 timing 文件完整性

---

## 3. FFmpeg 后处理问题

### 3.1 BGM 混音问题

**症状**
- BGM 音量过大盖住人声
- BGM 结尾突然中断
- 音频爆音/失真

**原因**
- 音量比例设置不当
- 未做淡入淡出
- 采样率不匹配

**解决方案**
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

# 循环 BGM 到指定时长
ffmpeg -stream_loop -1 -i bgm.mp3 -i voice.mp3 \
  -filter_complex "
    [0:a]atrim=0:60,volume=0.15,afade=t=out:st=58:d=2[bgm];
    [1:a]volume=1.0[voice];
    [voice][bgm]amix=inputs=2:duration=shortest
  " output.mp3

# 统一采样率后混音
ffmpeg -i voice.mp3 -i bgm.mp3 \
  -filter_complex "
    [0:a]aresample=48000[voice];
    [1:a]aresample=48000,volume=0.15[bgm];
    [voice][bgm]amix=inputs=2:duration=first
  " \
  -ar 48000 output.mp3
```

**预防**
- 所有音频统一为 48kHz
- BGM 音量建议 0.1-0.2
- 始终添加淡入淡出

---

### 3.2 字幕烧录问题

**症状**
- 字幕位置不正确
- 字体不显示或显示方块
- 字幕颜色与背景混淆
- 中文字幕乱码

**原因**
- 字体文件缺失
- SRT/ASS 格式错误
- 字符编码问题

**解决方案**
```bash
# 检查系统可用字体
fc-list :lang=zh

# 使用 SRT 字幕（推荐用于简单样式）
ffmpeg -i input.mp4 -vf "subtitles=sub.srt:force_style='FontName=PingFang SC,FontSize=24,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=2,MarginV=50'" output.mp4

# 使用 ASS 字幕（复杂样式）
# 首先转换 SRT 到 ASS
ffmpeg -i sub.srt sub.ass

# 编辑 ASS 文件的 Style 部分
# Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
# Style: Default,PingFang SC,48,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2,1,2,20,20,50,1

# 烧录 ASS 字幕
ffmpeg -i input.mp4 -vf "ass=sub.ass" output.mp4

# 指定字体目录
ffmpeg -i input.mp4 -vf "subtitles=sub.srt:fontsdir=/path/to/fonts:force_style='FontName=MyFont'" output.mp4

# 解决中文乱码（确保 UTF-8）
file sub.srt  # 检查编码
iconv -f GBK -t UTF-8 sub_gbk.srt -o sub_utf8.srt
```

**预防**
- 字幕文件始终使用 UTF-8 编码
- 选择系统已安装的字体
- 添加描边确保可读性

---

### 3.3 视频质量下降

**症状**
- 处理后视频变模糊
- 色彩失真
- 文件体积过大或过小

**原因**
- 编码参数不当
- 二次编码损失
- 色彩空间转换错误

**解决方案**
```bash
# 高质量 H.264 编码
ffmpeg -i input.mp4 \
  -c:v libx264 \
  -preset slow \
  -crf 18 \
  -pix_fmt yuv420p \
  -c:a aac -b:a 192k \
  output.mp4

# 无损复制（仅添加字幕等）
ffmpeg -i input.mp4 -i sub.srt \
  -c:v copy -c:a copy \
  -c:s mov_text \
  output.mp4

# 保持原始色彩空间
ffmpeg -i input.mp4 \
  -c:v libx264 \
  -color_primaries bt709 \
  -color_trc bt709 \
  -colorspace bt709 \
  output.mp4

# 对比编码前后质量
ffmpeg -i input.mp4 -i output.mp4 \
  -filter_complex "[0:v][1:v]psnr" -f null -

# CRF 参考值
# 18: 视觉无损
# 23: 默认（较好质量）
# 28: 较低质量
# 51: 最低质量
```

**预防**
- 尽量减少编码次数
- CRF 值保持在 18-23
- 需要再编辑时使用 ProRes 等中间编码

---

### 3.4 分辨率不匹配

**症状**
- 输出视频有黑边
- 画面被裁切
- 画面被拉伸变形

**原因**
- 输入输出分辨率不同
- 宽高比不一致
- scale 滤镜设置错误

**解决方案**
```bash
# 查看输入分辨率
ffprobe -v quiet -select_streams v:0 -show_entries stream=width,height -of csv=p=0 input.mp4

# 缩放到指定分辨率（保持宽高比，添加黑边）
ffmpeg -i input.mp4 \
  -vf "scale=3840:2160:force_original_aspect_ratio=decrease,pad=3840:2160:(ow-iw)/2:(oh-ih)/2" \
  output.mp4

# 缩放并裁切（填满，可能丢失边缘）
ffmpeg -i input.mp4 \
  -vf "scale=3840:2160:force_original_aspect_ratio=increase,crop=3840:2160" \
  output.mp4

# 智能缩放（宽度固定，高度自适应）
ffmpeg -i input.mp4 \
  -vf "scale=3840:-2" \
  output.mp4

# 处理竖版视频（添加模糊背景）
ffmpeg -i vertical.mp4 \
  -filter_complex "
    [0:v]scale=3840:2160,boxblur=20:20[bg];
    [0:v]scale=-1:2160[fg];
    [bg][fg]overlay=(W-w)/2:(H-h)/2
  " \
  output.mp4
```

**预防**
- 确认项目标准分辨率
- 素材收集时统一规格
- 使用脚本自动检查分辨率

---

## 4. 布局和显示问题

### 4.1 内容居中过小

**症状**
- 主要内容只占据画面中央一小部分
- 四周大量空白
- 移动端观看时内容太小

**原因**
- 固定像素值而非百分比
- 容器尺寸限制
- transform scale 过小

**解决方案**
```tsx
// 错误: 固定尺寸
<div style={{ width: 800, height: 600 }}>
  <Img src={image} style={{ width: '100%' }} />
</div>

// 正确: 响应式布局
<AbsoluteFill>
  <Img
    src={image}
    style={{
      width: '100%',
      height: '100%',
      objectFit: 'cover'
    }}
  />
</AbsoluteFill>

// 带安全边距的全屏布局
<AbsoluteFill style={{ padding: '5%' }}>
  <div style={{
    width: '100%',
    height: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  }}>
    {/* 内容 */}
  </div>
</AbsoluteFill>
```

**预防**
- 使用 `AbsoluteFill` 作为根容器
- 优先使用百分比和 flex 布局
- 在不同分辨率下测试预览

---

### 4.2 空白区域问题

**症状**
- 画面边缘有未使用区域
- 背景色不统一
- 内容区域与预期不符

**原因**
- 容器未设置背景色
- 子元素未完全填充
- margin/padding 过大

**解决方案**
```tsx
// 确保根组件填满画布
export const MyComposition: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: '#1a1a1a' }}>
      {/* 背景层 */}
      <AbsoluteFill>
        <Img src={bgImage} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
      </AbsoluteFill>

      {/* 内容层 */}
      <AbsoluteFill style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        padding: '5%'
      }}>
        {/* 内容 */}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
```

```css
/* 调试布局问题 */
* {
  outline: 1px solid red !important;
}
```

**预防**
- 始终为根容器设置背景色
- 使用浏览器开发工具检查布局
- 建立布局模板复用

---

### 4.3 媒体未填满屏幕

**症状**
- 图片/视频四周有空隙
- 背景未完全覆盖
- 媒体元素对齐错误

**原因**
- objectFit 设置不当
- 未考虑原始宽高比
- 定位属性缺失

**解决方案**
```tsx
// 图片填满容器
<Img
  src={imageSrc}
  style={{
    position: 'absolute',
    width: '100%',
    height: '100%',
    objectFit: 'cover',      // 填满，可能裁切
    // objectFit: 'contain', // 完整显示，可能留白
    objectPosition: 'center center'
  }}
/>

// 视频填满容器
<OffthreadVideo
  src={videoSrc}
  style={{
    position: 'absolute',
    width: '100%',
    height: '100%',
    objectFit: 'cover'
  }}
/>

// 处理不同宽高比的媒体
const MediaFill: React.FC<{src: string, aspectRatio: number}> = ({src, aspectRatio}) => {
  const {width, height} = useVideoConfig();
  const canvasAspect = width / height;

  const style: React.CSSProperties = aspectRatio > canvasAspect
    ? { width: '100%', height: 'auto' }
    : { width: 'auto', height: '100%' };

  return (
    <AbsoluteFill style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
      <Img src={src} style={style} />
    </AbsoluteFill>
  );
};
```

**预防**
- 媒体素材尽量匹配输出比例
- 使用 objectFit: cover 确保填满
- 预览检查不同素材的显示效果

---

### 4.4 非 16:9 素材处理

**症状**
- 竖版视频/图片显示异常
- 超宽素材被压缩
- 正方形素材留白过多

**原因**
- 素材宽高比与画布不匹配
- 未使用适当的适配策略

**解决方案**
```tsx
// 方案1: 模糊背景 + 居中显示
const BlurredBackground: React.FC<{src: string}> = ({src}) => {
  return (
    <AbsoluteFill>
      {/* 模糊背景 */}
      <Img
        src={src}
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          filter: 'blur(30px) brightness(0.6)',
          transform: 'scale(1.1)'
        }}
      />
      {/* 清晰前景 */}
      <AbsoluteFill style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <Img
          src={src}
          style={{
            maxWidth: '100%',
            maxHeight: '100%',
            objectFit: 'contain'
          }}
        />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// 方案2: 智能裁切 + Ken Burns 效果
const KenBurnsEffect: React.FC<{src: string}> = ({src}) => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();

  const scale = interpolate(frame, [0, durationInFrames], [1, 1.2]);
  const x = interpolate(frame, [0, durationInFrames], [0, -50]);

  return (
    <AbsoluteFill>
      <Img
        src={src}
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          transform: `scale(${scale}) translateX(${x}px)`
        }}
      />
    </AbsoluteFill>
  );
};

// 方案3: 并排显示多个竖版素材
const SideBySide: React.FC<{images: string[]}> = ({images}) => {
  return (
    <AbsoluteFill style={{ display: 'flex' }}>
      {images.map((src, i) => (
        <div key={i} style={{ flex: 1, overflow: 'hidden' }}>
          <Img
            src={src}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover'
            }}
          />
        </div>
      ))}
    </AbsoluteFill>
  );
};
```

**预防**
- 在素材收集阶段记录宽高比
- 为不同比例素材准备对应模板
- 使用脚本自动分类素材

---

## 5. 文件和路径问题

### 5.1 文件缺失

**症状**
```
Error: ENOENT: no such file or directory
Cannot find file: ./assets/image.png
404 Not Found
```

**原因**
- 文件未创建或已删除
- 路径错误
- Git 未跟踪（大文件）

**解决方案**
```bash
# 检查文件是否存在
ls -la /path/to/expected/file

# 搜索文件
find . -name "image.png" 2>/dev/null

# 检查 Git LFS 文件
git lfs ls-files
git lfs pull

# 检查 .gitignore 是否排除了必要文件
grep -r "image.png" .gitignore

# 验证 Remotion 静态文件目录
ls -la public/
```

```tsx
// 在代码中检查文件存在性
import { staticFile, delayRender, continueRender } from 'remotion';

const MyComp: React.FC = () => {
  const [handle] = useState(() => delayRender('Checking files...'));
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const checkFiles = async () => {
      const files = ['image1.png', 'audio.mp3'];
      for (const file of files) {
        try {
          const response = await fetch(staticFile(file));
          if (!response.ok) {
            console.error(`Missing file: ${file}`);
          }
        } catch (e) {
          console.error(`Cannot access: ${file}`, e);
        }
      }
      setReady(true);
      continueRender(handle);
    };
    checkFiles();
  }, [handle]);

  if (!ready) return null;
  return <div>...</div>;
};
```

**预防**
- 使用 `staticFile()` 引用 public 目录文件
- 建立文件检查脚本在渲染前运行
- 大文件使用 Git LFS 管理

---

### 5.2 路径错误

**症状**
- 本地运行正常，部署后找不到文件
- Windows/Mac/Linux 路径不兼容
- 相对路径解析错误

**原因**
- 绝对路径硬编码
- 路径分隔符不一致
- 工作目录变化

**解决方案**
```bash
# 检查当前工作目录
pwd

# 使用相对于项目根目录的路径
# 错误: /Users/name/project/assets/image.png
# 正确: ./assets/image.png

# 在脚本中使用 dirname
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
```

```tsx
// Remotion 中使用 staticFile
import { staticFile } from 'remotion';

// 正确: 相对于 public 目录
const imagePath = staticFile('images/logo.png');

// 外部文件使用绝对 URL 或环境变量
const externalAsset = process.env.ASSET_BASE_URL + '/image.png';
```

```python
# Python 中使用 pathlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
ASSETS_DIR = PROJECT_ROOT / 'assets'
image_path = ASSETS_DIR / 'image.png'

# 确保路径存在
if not image_path.exists():
    raise FileNotFoundError(f"Missing: {image_path}")
```

**预防**
- 避免硬编码绝对路径
- 使用跨平台的路径处理库
- 在 CI 中测试路径正确性

---

### 5.3 命名规范错误

**症状**
- 文件名含特殊字符导致解析失败
- 空格导致命令行参数错误
- 中文文件名乱码

**原因**
- 文件名包含空格或特殊字符
- 编码不一致
- 命名风格不统一

**解决方案**
```bash
# 批量重命名（空格替换为下划线）
for f in *\ *; do mv "$f" "${f// /_}"; done

# 批量重命名（中文转拼音需要工具）
# pip install pypinyin
python3 -c "
import os
from pypinyin import lazy_pinyin

for f in os.listdir('.'):
    if any('\u4e00' <= c <= '\u9fff' for c in f):
        new_name = '_'.join(lazy_pinyin(os.path.splitext(f)[0])) + os.path.splitext(f)[1]
        os.rename(f, new_name)
        print(f'{f} -> {new_name}')
"

# 检查文件名规范
find . -name "*[[:space:]]*" -o -name "*[!a-zA-Z0-9._-]*"
```

```python
# 文件命名规范化函数
import re
import unicodedata

def normalize_filename(name):
    # 移除不安全字符
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    # 空格替换为下划线
    name = name.replace(' ', '_')
    # 移除连续下划线
    name = re.sub(r'_+', '_', name)
    # 转为小写（可选）
    name = name.lower()
    return name.strip('_')

# 项目文件命名约定
# 视频: video_001_intro.mp4
# 音频: audio_001_voice.mp3
# 图片: img_001_background.png
# 时间: timing_001.json
```

**预防**
- 建立项目文件命名规范
- 使用自动化脚本验证文件名
- 在上传/导入时自动规范化

---

## 附录

### A. 常用诊断命令

```bash
# 系统资源检查
top -l 1 | head -10                    # CPU/内存使用
df -h                                   # 磁盘空间
ulimit -a                              # 系统限制

# FFmpeg 信息
ffmpeg -version                        # 版本信息
ffprobe -v quiet -show_format file.mp4 # 文件信息

# Node.js/NPM
node -v && npm -v                      # 版本
npm ls --depth=0                       # 已安装包

# Remotion
npx remotion --version                 # 版本
npx remotion browser list              # 可用浏览器
```

### B. 常用环境变量

```bash
# TTS
export AZURE_TTS_KEY="your-key"
export AZURE_TTS_REGION="eastasia"

# Remotion
export REMOTION_LOG_LEVEL="verbose"
export NODE_OPTIONS="--max-old-space-size=8192"

# FFmpeg
export FFMPEG_PATH="/usr/local/bin/ffmpeg"
```

### C. 快速检查清单

渲染前检查：
- [ ] 所有素材文件存在
- [ ] timing.json 格式正确
- [ ] 音频时长与 timing 匹配
- [ ] 环境变量已设置
- [ ] 磁盘空间充足 (>20GB for 4K)
- [ ] 内存充足 (>8GB 可用)

渲染后检查：
- [ ] 视频时长正确
- [ ] 音画同步
- [ ] 字幕显示正常
- [ ] 无黑屏/空白帧
- [ ] 文件大小合理

---

## 更新日志

- 2024-01: 初始版本
- 持续更新中...

如有问题未涵盖，请提交 issue 或联系维护者。
