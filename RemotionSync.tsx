/**
 * Remotion 音视频同步示例
 *
 * 使用 timing.json 来驱动视频章节切换，确保与音频完美同步
 */
import { AbsoluteFill, Sequence, Audio, staticFile, useVideoConfig } from 'remotion'

// 从 timing.json 导入（需要在 Remotion 配置中允许）
// 或者直接在渲染时传入 props
import timingData from '../public/timing.json'

// 章节组件映射
const SectionComponents: Record<string, React.FC> = {
  hero: HeroSection,
  features: FeaturesSection,
  demo: DemoSection,
  comparison: ComparisonSection,
  summary: SummarySection,
  // 添加更多章节...
}

// 主视频组件 - 自动同步版本
export const SyncedVideo: React.FC = () => {
  const { fps } = useVideoConfig()

  return (
    <AbsoluteFill>
      {/* 音频轨道 */}
      <Audio src={staticFile('podcast_audio.wav')} />

      {/* 根据 timing.json 自动生成章节序列 */}
      {timingData.sections.map((section) => {
        const Component = SectionComponents[section.name]
        if (!Component) {
          console.warn(`No component found for section: ${section.name}`)
          return null
        }

        return (
          <Sequence
            key={section.name}
            from={section.start_frame}
            durationInFrames={section.duration_frames}
          >
            <Component />
          </Sequence>
        )
      })}
    </AbsoluteFill>
  )
}

// Root 组件 - 使用 timing.json 的总时长
export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="SyncedPodcast"
      component={SyncedVideo}
      durationInFrames={timingData.total_frames}
      fps={timingData.fps}
      width={1920}
      height={1080}
    />
  )
}

// ============ 使用方法 ============
//
// 1. 在 podcast.txt 中添加章节标记:
//
//    [SECTION:hero]
//    今天给大家介绍一款工具...
//
//    [SECTION:features]
//    它有以下功能...
//
//    [SECTION:demo]
//    让我演示一下...
//
//    [SECTION:summary]
//    总结一下...
//
// 2. 运行 TTS 脚本:
//    python3 generate_tts.py
//
// 3. 将 timing.json 复制到 public 目录:
//    cp timing.json public/
//    cp podcast_audio.wav public/
//
// 4. 创建对应的章节组件 (HeroSection, FeaturesSection, etc.)
//
// 5. 渲染:
//    npx remotion render src/remotion/index.ts SyncedPodcast output.mp4
//
// ================================

// 章节组件示例 (占位符 - 需要实现具体内容)
function HeroSection() {
  return (
    <AbsoluteFill style={{ backgroundColor: '#fafafa', justifyContent: 'center', alignItems: 'center' }}>
      <h1 style={{ fontSize: 120, fontWeight: 'bold' }}>Hero Section</h1>
    </AbsoluteFill>
  )
}

function FeaturesSection() {
  return (
    <AbsoluteFill style={{ backgroundColor: '#fff', justifyContent: 'center', alignItems: 'center' }}>
      <h1 style={{ fontSize: 100, fontWeight: 'bold' }}>Features</h1>
    </AbsoluteFill>
  )
}

function DemoSection() {
  return (
    <AbsoluteFill style={{ backgroundColor: '#f5f5f5', justifyContent: 'center', alignItems: 'center' }}>
      <h1 style={{ fontSize: 100, fontWeight: 'bold' }}>Demo</h1>
    </AbsoluteFill>
  )
}

function ComparisonSection() {
  return (
    <AbsoluteFill style={{ backgroundColor: '#fafafa', justifyContent: 'center', alignItems: 'center' }}>
      <h1 style={{ fontSize: 100, fontWeight: 'bold' }}>Comparison</h1>
    </AbsoluteFill>
  )
}

function SummarySection() {
  return (
    <AbsoluteFill style={{ backgroundColor: '#1d1d1f', justifyContent: 'center', alignItems: 'center' }}>
      <h1 style={{ fontSize: 100, fontWeight: 'bold', color: 'white' }}>Summary</h1>
    </AbsoluteFill>
  )
}
