---
name: audio-sync-guard
description: 强制约束 video-podcast-maker 项目的声画/字幕同步。在生成 TTS、Remotion 合成、渲染前必须调用，防止 timing.json 与真实音频脱节。触发词：声画同步、音画同步、字幕不同步、timing.json、audio sync、av sync。
argument-hint: "[video-dir like videos/<name>]"
effort: low
author: Kimi Code CLI
category: Quality Assurance
version: 1.0.0
updated: 2026-06-17
---

# Audio Sync Guard — 声画同步守门员

本 skill 是 `video-podcast-maker` 的**强制质量门**。无论主技能走到哪一步，只要涉及 `timing.json`、`Remotion 合成`、`最终渲染`，就必须先过这里的检查。

## 核心原则（不可违背）

1. **音频是主时钟（Audio is the master clock）**
   - 一切画面切换、字幕、进度条、动画，必须以 `podcast_audio.wav` + `podcast_audio.srt` 的真实时间为准。
   - `timing.json` 不准再由人眼估算文字字数生成。

2. **正确流水线顺序**
   ```
   podcast.txt（定稿）
     → generate_tts.py（真实 TTS）
     → podcast_audio.wav + podcast_audio.srt + timing.json
     → Remotion 合成
     → 渲染
   ```
   任何“先写 timing.json 再配音”的做法都是错的。

3. **TransitionSeries 重叠必须补偿**
   - `TransitionSeries` 会让总时长 = `sum(section.duration_frames) + (N-1) * transitionFrames`。
   - 为了和音频等长，要**把所有 section 等比放大**，而不是只把多余帧塞给第一节。
   - 公式：
     ```ts
     const target = originalTotal + transitionCount * transitionFrames;
     const scale = target / originalTotal;
     ```

## 触发时机

- 用户提到“声画不同步”“字幕超前/落后”“timing.json 不对”。
- 每次生成新视频，执行到 Step 8（TTS）之后、Step 9（Studio）之前。
- 每次最终渲染前。

## 强制检查清单

### Step 8 之后：TTS 输出检查

```bash
cd <project-root>
VIDEO_DIR="videos/<name>"

# 1. 三个文件必须同时存在
ls ${VIDEO_DIR}/podcast_audio.wav ${VIDEO_DIR}/podcast_audio.srt ${VIDEO_DIR}/timing.json

# 2. timing.json 的总时长必须来自真实音频
ffprobe -v error -show_entries format=duration -of csv=p=0 ${VIDEO_DIR}/podcast_audio.wav
# 与 timing.json 里的 total_duration 对比，差值必须 < 0.5s
python3 - <<'PY'
import json, subprocess, sys
base = "videos/<name>"
wav = subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f"{base}/podcast_audio.wav"],text=True).strip()
t = json.load(open(f"{base}/timing.json"))
drift = abs(float(wav) - t.get("total_duration",0))
print(f"WAV={float(wav):.3f}s  timing={t.get('total_duration',0):.3f}s  drift={drift:.3f}s")
if drift >= 0.5:
    sys.exit("❌ timing.json 与真实音频脱节，必须重新生成或对齐")
print("✅ timing.json 与音频对齐")
PY
```

### Step 9/10 之前：Remotion 合成检查

1. **Video.tsx 中的过渡补偿必须正确**
   - 禁止 `i === 0 ? s.duration_frames + transitionCount * transitionFrames : s.duration_frames`。
   - 必须使用**等比缩放 + 尾节吸收余数**。
   - 详见下方「模板修正代码」。

2. **composition 的 durationInFrames 必须等于 timing.total_frames**
   - 如果 `calculateMetadata` 从 timing.json 读取，要确认读取的是 `total_frames` 而不是自己估算。

3. ** subtitles 必须读取 `podcast_audio.srt`**
   - 字幕源必须是和 WAV 同一次 TTS 生成的 SRT，禁止用旧 SRT 或手写时间轴。

### 最终渲染后：输出文件检查

```bash
VIDEO_DIR="videos/<name>"

# 最终成片时长必须和 WAV 一致（允许 ±0.5s 容差）
VID_DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 ${VIDEO_DIR}/final_video.mp4)
WAV_DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 ${VIDEO_DIR}/podcast_audio.wav)
python3 - <<PY
v=float("${VID_DUR}")
w=float("${WAV_DUR}")
print(f"video={v:.3f}s audio={w:.3f}s diff={abs(v-w):.3f}s")
if abs(v-w) > 0.5:
    raise SystemExit("❌ 成片时长与音频不符，声画不同步")
print("✅ 成片时长与音频一致")
PY
```

## 模板修正代码（Video.tsx）

把这段替换进 `skills/video-podcast-maker/templates/Video.tsx` 以及任何自定义 Video 组件：

```tsx
export const Video = (props: VideoProps) => {
  const timing = useTiming();
  const sections = timing.sections;
  const transitionFrames = props.transitionDuration;
  const transitionCount = Math.max(0, sections.length - 1);

  // Audio-master-clock: scale every section so TransitionSeries total equals timing.total_frames.
  const originalTotal = sections.reduce((sum, s) => sum + s.duration_frames, 0);
  const targetTotal = timing.total_frames + transitionCount * transitionFrames;
  const scaleFactor = originalTotal > 0 ? targetTotal / originalTotal : 1;

  let scaled = sections.map((s) => ({
    ...s,
    duration_frames: Math.max(15, Math.round(s.duration_frames * scaleFactor)),
  }));

  // Absorb rounding error into the last section so total matches exactly.
  const scaledTotal = scaled.reduce((sum, s) => sum + s.duration_frames, 0);
  const diff = targetTotal - scaledTotal;
  if (scaled.length > 0) {
    const last = scaled[scaled.length - 1];
    last.duration_frames = Math.max(15, last.duration_frames + diff);
  }

  return (
    <AbsoluteFill style={{ backgroundColor: props.backgroundColor }}>
      <Scale4K orientation={props.orientation}>
        <TransitionSeries>
          {scaled.map((section, i) => (
            <React.Fragment key={section.name}>
              <TransitionSeries.Sequence durationInFrames={section.duration_frames}>
                <SectionComponent section={section} props={props} />
              </TransitionSeries.Sequence>
              {i < scaled.length - 1 && transitionFrames > 0 && props.transitionType !== "none" && (
                <TransitionSeries.Transition
                  presentation={getPresentation(props.transitionType)}
                  timing={linearTiming({ durationInFrames: transitionFrames })}
                />
              )}
            </React.Fragment>
          ))}
        </TransitionSeries>
      </Scale4K>
      <ChapterProgressBar props={props} chapters={timing.sections} />
      <Subtitles src={staticFile("podcast_audio.srt")} />
      {props.bgmVolume > 0 && <Audio src={staticFile("bgm.mp3")} volume={props.bgmVolume} />}
      <Audio src={staticFile("podcast_audio.wav")} />
    </AbsoluteFill>
  );
};
```

## 如果 timing.json 已经是手写/估算的（补救）

如果历史项目的 `timing.json` 不是由 `generate_tts.py` 生成的，必须先对齐，再渲染：

```bash
# 方案 A：重新跑 TTS，让 generate_tts.py 覆盖生成（推荐）
python3 skills/video-podcast-maker/scripts/generate_tts.py --input videos/<name>/podcast.txt --output-dir videos/<name>

# 方案 B：只对齐现有 timing.json（保留你手工设计的 slides，但把时间锚到真实 SRT）
python3 skills/video-podcast-maker/scripts/align_timing_from_srt.py videos/<name>
```

> `align_timing_from_srt.py` 会把每个 slide 的 headline/body 与 SRT 匹配，重新计算 `start_time`、`duration`、`start_frame`、`duration_frames`，并备份原文件。

## 常见错误

| 错误现象 | 根因 | 修复 |
|---------|------|------|
| 视频比音频提前结束 | timing.json 总时长 < WAV 时长；或 TransitionSeries 重叠没补偿 | 用音频重新对齐；等比放大 sections |
| 视频比音频长 | timing.json 总时长 > WAV 时长 | 运行 `reconcile_timing_with_wav` 或重新生成 |
| 前面同步，后面越来越偏 | 只把过渡重叠帧加给第一节 | 改为所有 section 等比缩放 |
| 字幕与画面不一致 | SRT 不是同一次 TTS 产物 | 重新生成 TTS，确认 `podcast_audio.srt` 时间戳来自真实音频 |

## 出口标准

在宣布“渲染完成”之前，必须同时满足：

1. `timing.json.total_duration` 与 `podcast_audio.wav` 时长差 `< 0.5s`。
2. `final_video.mp4` 时长与 `podcast_audio.wav` 时长差 `< 0.5s`。
3. Remotion `Video.tsx` 使用等比缩放补偿 TransitionSeries 重叠。
4. 字幕源是本次 TTS 生成的 `podcast_audio.srt`。

达不到以上任意一条，**不得进入发布流程**。
