import { AbsoluteFill, Audio, Sequence, useCurrentFrame, interpolate, Easing, spring, useVideoConfig, staticFile } from 'remotion'
import timingData from '../../public/timing.json'

const font = '-apple-system, "SF Pro Display", "Noto Sans SC", sans-serif'
const colors = {
  bg: '#fff',
  text: '#1a1a1a',
  textMuted: 'rgba(0,0,0,0.5)',
  accent: '#2563eb',
  green: '#059669',
  purple: '#7c3aed',
}

const FadeIn = ({ children, delay = 0, y = 30, dur = 25 }: { children: React.ReactNode, delay?: number, y?: number, dur?: number }) => {
  const frame = useCurrentFrame()
  const progress = interpolate(frame - delay, [0, dur], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  })
  return <div style={{ opacity: progress, transform: `translateY(${interpolate(progress, [0, 1], [y, 0])}px)` }}>{children}</div>
}

const SpringPop = ({ children, delay = 0 }: { children: React.ReactNode, delay?: number }) => {
  const frame = useCurrentFrame()
  const { fps } = useVideoConfig()
  const scale = spring({ fps, frame: frame - delay, config: { stiffness: 200, damping: 12 } })
  return <div style={{ transform: `scale(${scale})` }}>{children}</div>
}

// Hero: 一行命令，从话题到4K成片
const HeroSection = () => (
  <AbsoluteFill style={{ background: colors.bg, fontFamily: font, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
    <FadeIn delay={0}>
      <div style={{ fontSize: 56, fontWeight: 600, color: colors.textMuted, marginBottom: 20 }}>一行命令</div>
    </FadeIn>
    <SpringPop delay={15}>
      <div style={{ fontSize: 100, fontWeight: 800, color: colors.accent, marginBottom: 20 }}>话题 → 4K成片</div>
    </SpringPop>
    <FadeIn delay={30}>
      <div style={{ fontSize: 48, color: colors.green, fontWeight: 700 }}>全自动 · 十分钟</div>
    </FadeIn>
    <FadeIn delay={50}>
      <div style={{ fontSize: 72, fontWeight: 800, color: colors.text, marginTop: 50 }}>Video Podcast Maker</div>
    </FadeIn>
  </AbsoluteFill>
)

// Workflow: 14步工作流
const WorkflowSection = () => {
  const steps = [
    { name: '定义话题', icon: '🎯' },
    { name: '上网调研', icon: '🔍' },
    { name: '设计章节', icon: '📋' },
    { name: '撰写脚本', icon: '✍️' },
    { name: '收集素材', icon: '🖼️' },
    { name: '生成发布信息', icon: '📝' },
    { name: '制作封面', icon: '🎨' },
    { name: 'TTS配音', icon: '🎙️' },
    { name: '创建组件', icon: '⚡' },
    { name: '实时预览', icon: '👁️' },
    { name: '渲染4K', icon: '🎬' },
    { name: '混合BGM', icon: '🎵' },
    { name: '烧录字幕', icon: '💬' },
    { name: '补全章节', icon: '✅' },
  ]
  const frame = useCurrentFrame()
  const { fps } = useVideoConfig()

  // 柔和彩色（降低饱和度）
  const stepColors = [
    '#4b6cb7', '#5a7fc4', '#4a90a4', '#4a9e96', '#4a9e7e', '#5a9e6a', '#6a9e5a',
    '#8a9e4a', '#a89a4a', '#b8904a', '#c8804a', '#c86a5a', '#b85a8a', '#7a5ab8'
  ]

  return (
    <AbsoluteFill style={{ background: colors.bg, fontFamily: font, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '40px 40px 100px 40px' }}>
      <FadeIn delay={0}>
        <div style={{ fontSize: 80, fontWeight: 800, color: colors.text, textAlign: 'center', marginBottom: 40 }}>14 步全自动流程</div>
      </FadeIn>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 20, maxWidth: 1600 }}>
        {steps.map((step, i) => {
          const delay = 15 + i * 6
          const scale = spring({ fps, frame: frame - delay, config: { stiffness: 180, damping: 14 } })

          return (
            <div key={i} style={{ transform: `scale(${Math.min(scale, 1)})`, opacity: scale }}>
              <div style={{
                background: stepColors[i],
                color: '#fff',
                padding: '20px 24px',
                borderRadius: 20,
                textAlign: 'center',
                boxShadow: `0 6px 20px ${stepColors[i]}1C`,
              }}>
                <div style={{ fontSize: 40, marginBottom: 8 }}>{step.icon}</div>
                <div style={{ fontSize: 20, fontWeight: 700, opacity: 0.9 }}>{i + 1}</div>
                <div style={{ fontSize: 26, fontWeight: 600, marginTop: 4 }}>{step.name}</div>
              </div>
            </div>
          )
        })}
      </div>
      <FadeIn delay={120}>
        <div style={{
          textAlign: 'center',
          marginTop: 30,
          fontSize: 34,
          color: colors.text,
          display: 'flex',
          gap: 20,
          alignItems: 'center',
        }}>
          <span style={{ fontWeight: 700, color: '#4b6cb7' }}>话题输入</span>
          <span style={{ color: colors.textMuted }}>→</span>
          <span style={{ fontWeight: 700, color: '#4a9e7e' }}>Claude 引导</span>
          <span style={{ color: colors.textMuted }}>→</span>
          <span style={{ fontWeight: 700, color: '#b8904a' }}>交互式调整</span>
          <span style={{ color: colors.textMuted }}>→</span>
          <span style={{ fontWeight: 700, color: '#7a5ab8' }}>一键完成</span>
        </div>
      </FadeIn>
    </AbsoluteFill>
  )
}

// Studio: Remotion Studio 可视化编辑
const StudioSection = () => (
  <AbsoluteFill style={{ background: colors.bg, fontFamily: font, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: 50 }}>
    <FadeIn delay={0}>
      <div style={{ fontSize: 72, fontWeight: 800, color: colors.purple, marginBottom: 40 }}>Remotion Studio</div>
    </FadeIn>
    <FadeIn delay={20}>
      <div style={{ fontSize: 48, color: colors.text, marginBottom: 40 }}>可视化编辑 · 所见即所得</div>
    </FadeIn>
    <div style={{ display: 'flex', gap: 30, marginTop: 20 }}>
      {['颜色主题', '字体大小', '进度条样式', 'BGM音量'].map((item, i) => (
        <FadeIn key={i} delay={40 + i * 15}>
          <div style={{
            background: 'linear-gradient(135deg, #7c3aed 0%, #2563eb 100%)',
            color: '#fff',
            padding: '24px 36px',
            borderRadius: 20,
            fontSize: 32,
            fontWeight: 600,
          }}>{item}</div>
        </FadeIn>
      ))}
    </div>
    <FadeIn delay={120}>
      <div style={{ fontSize: 36, color: colors.textMuted, marginTop: 50 }}>
        自然语言调教 · 一边改一边预览 · 满意后再渲染
      </div>
    </FadeIn>
  </AbsoluteFill>
)

// Features: 六大核心功能
const FeaturesSection = () => {
  const features = [
    { icon: '🎙️', title: '中英混读 TTS', desc: '自动切换语音 · 多音字校正' },
    { icon: '4K', title: '4K 输出', desc: '3840×2160 高清' },
    { icon: '📊', title: '章节进度条', desc: '实时显示当前章节' },
    { icon: '📺', title: 'B站深度优化', desc: '时间戳 · 双比例封面' },
    { icon: '🌐', title: '双语 TTS', desc: '中英混排自动切换' },
    { icon: '🎵', title: '内置 BGM', desc: '一行命令混音' },
  ]
  return (
    <AbsoluteFill style={{ background: colors.bg, fontFamily: font, padding: 50 }}>
      <FadeIn delay={0}>
        <div style={{ fontSize: 72, fontWeight: 800, color: colors.text, textAlign: 'center', marginBottom: 50 }}>六大核心功能</div>
      </FadeIn>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 30 }}>
        {features.map((f, i) => (
          <FadeIn key={i} delay={20 + i * 15}>
            <div style={{
              background: 'rgba(0,0,0,0.03)',
              padding: 36,
              borderRadius: 24,
              textAlign: 'center',
            }}>
              <div style={{ fontSize: 64, marginBottom: 16 }}>{f.icon}</div>
              <div style={{ fontSize: 36, fontWeight: 700, color: colors.text, marginBottom: 12 }}>{f.title}</div>
              <div style={{ fontSize: 28, color: colors.textMuted }}>{f.desc}</div>
            </div>
          </FadeIn>
        ))}
      </div>
    </AbsoluteFill>
  )
}

// Quickstart: 快速上手
const QuickstartSection = () => (
  <AbsoluteFill style={{ background: colors.bg, fontFamily: font, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: 50 }}>
    <FadeIn delay={0}>
      <div style={{ fontSize: 72, fontWeight: 800, color: colors.text, marginBottom: 50 }}>快速上手</div>
    </FadeIn>
    <div style={{ display: 'flex', gap: 40, marginBottom: 50 }}>
      {['Claude Code / Opencode', 'Remotion 项目', 'Azure Speech API'].map((item, i) => (
        <FadeIn key={i} delay={20 + i * 15}>
          <div style={{
            background: colors.accent,
            color: '#fff',
            padding: '20px 32px',
            borderRadius: 16,
            fontSize: 32,
            fontWeight: 600,
          }}>{item}</div>
        </FadeIn>
      ))}
    </div>
    <FadeIn delay={80}>
      <div style={{
        background: '#1a1a1a',
        color: '#4ade80',
        padding: '30px 50px',
        borderRadius: 20,
        fontSize: 36,
        fontFamily: 'monospace',
      }}>
        "帮我制作一个关于 [话题] 的视频"
      </div>
    </FadeIn>
    <FadeIn delay={100}>
      <div style={{ fontSize: 40, color: colors.green, marginTop: 40, fontWeight: 700 }}>
        不需要写代码 · 不需要会剪辑 · 十分钟出片
      </div>
    </FadeIn>
  </AbsoluteFill>
)

// Summary: 总结
const SummarySection = () => (
  <AbsoluteFill style={{ background: colors.bg, fontFamily: font, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
    <FadeIn delay={0}>
      <div style={{ fontSize: 80, fontWeight: 800, color: colors.accent, marginBottom: 40 }}>Video Podcast Maker</div>
    </FadeIn>
    <div style={{ display: 'flex', gap: 30, marginBottom: 50 }}>
      {['开源免费', '14步自动流程', 'Studio可视化', 'B站深度优化'].map((item, i) => (
        <FadeIn key={i} delay={20 + i * 12}>
          <div style={{
            background: 'rgba(37, 99, 235, 0.1)',
            color: colors.accent,
            padding: '16px 28px',
            borderRadius: 12,
            fontSize: 32,
            fontWeight: 600,
          }}>{item}</div>
        </FadeIn>
      ))}
    </div>
    <FadeIn delay={80}>
      <div style={{ fontSize: 44, color: colors.text, marginBottom: 30 }}>
        GitHub: <span style={{ color: colors.accent, fontWeight: 700 }}>Agents365-ai/video-podcast-maker</span>
      </div>
    </FadeIn>
    <FadeIn delay={100}>
      <div style={{ fontSize: 48, color: colors.green, fontWeight: 700 }}>
        ⭐ 给个 Star 支持一下
      </div>
    </FadeIn>
  </AbsoluteFill>
)

// Outro
const OutroSection = () => (
  <AbsoluteFill style={{ background: colors.bg, fontFamily: font, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
    <SpringPop delay={0}>
      <div style={{ fontSize: 100, fontWeight: 800, color: colors.accent }}>下期再见！</div>
    </SpringPop>
  </AbsoluteFill>
)

// 一键三连独立页面 (学习自 superpowers 风格)
const TripleTapSection = () => (
  <AbsoluteFill style={{ background: colors.bg, fontFamily: font }}>
    <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
      <FadeIn delay={0}>
        <div style={{ fontSize: 80, fontWeight: 700, color: colors.text }}>感谢观看！</div>
      </FadeIn>
      <FadeIn delay={20}>
        <div style={{ display: 'flex', gap: 60, marginTop: 48 }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 80 }}>👍</div>
            <div style={{ fontSize: 32, color: colors.textMuted, marginTop: 12 }}>点赞</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 80 }}>🪙</div>
            <div style={{ fontSize: 32, color: colors.textMuted, marginTop: 12 }}>投币</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 80 }}>⭐</div>
            <div style={{ fontSize: 32, color: colors.textMuted, marginTop: 12 }}>收藏</div>
          </div>
        </div>
      </FadeIn>
      <FadeIn delay={40}>
        <div style={{ fontSize: 36, color: colors.accent, marginTop: 48 }}>下期再见！</div>
      </FadeIn>
    </div>
  </AbsoluteFill>
)

// 章节进度条 (学习自 superpowers 风格)
const ChapterProgressBar = () => {
  const frame = useCurrentFrame()
  const sections = (timingData as any).sections.filter((s: any) => s.duration_frames > 0)
  const totalFrames = (timingData as any).total_frames
  const progress = frame / totalFrames

  const sectionNamesCN: Record<string, string> = {
    hero: '开场', workflow: '流程', studio: 'Studio', features: '功能',
    quickstart: '上手', summary: '总结', outro: '结语',
  }

  return (
    <div style={{
      position: 'absolute',
      bottom: 0,
      left: 0,
      right: 0,
      height: 130,
      background: '#fff',
      borderTop: '2px solid #e5e7eb',
      display: 'flex',
      alignItems: 'center',
      padding: '0 60px',
      gap: 20,
      fontFamily: font,
    }}>
      {sections.map((section: any) => {
        const chStart = section.start_frame / totalFrames
        const chEnd = (section.start_frame + section.duration_frames) / totalFrames
        const isActive = progress >= chStart && progress < chEnd
        const isPast = progress >= chEnd
        const chProgress = isActive ? (progress - chStart) / (chEnd - chStart) : isPast ? 1 : 0
        const sectionName = sectionNamesCN[section.name] || section.name

        return (
          <div key={section.name} style={{
            flex: section.duration_frames,
            height: 76,
            borderRadius: 38,
            position: 'relative',
            overflow: 'hidden',
            background: isActive ? colors.accent : isPast ? '#f3f4f6' : '#f9fafb',
            border: isActive ? 'none' : '2px solid #e5e7eb',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            {isActive && (
              <div style={{
                position: 'absolute',
                left: 0,
                top: 0,
                bottom: 0,
                width: `${chProgress * 100}%`,
                background: 'rgba(255,255,255,0.25)',
                borderRadius: 38,
              }} />
            )}
            <span style={{
              position: 'relative',
              zIndex: 1,
              color: isActive ? '#fff' : isPast ? '#374151' : '#9ca3af',
              fontSize: 38,
              fontWeight: isActive ? 700 : 500,
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              padding: '0 20px',
            }}>{sectionName}</span>
          </div>
        )
      })}
      <div style={{
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        height: 5,
        background: '#e5e7eb',
      }}>
        <div style={{ height: '100%', width: `${progress * 100}%`, background: colors.accent }} />
      </div>
    </div>
  )
}

const sectionComponents: Record<string, React.FC> = {
  hero: HeroSection,
  workflow: WorkflowSection,
  studio: StudioSection,
  features: FeaturesSection,
  quickstart: QuickstartSection,
  summary: SummarySection,
  outro: TripleTapSection,
}

export const VideoPodcastMakerV2Video = () => {
  const sections = (timingData as any).sections
  return (
    <AbsoluteFill style={{ background: '#fff' }}>
      <Audio src={staticFile('podcast_audio.wav')} />
      <AbsoluteFill style={{ transform: 'scale(2)', transformOrigin: 'top left', width: '50%', height: '50%' }}>
        {sections.map((section: any) => {
          const Component = sectionComponents[section.name]
          if (!Component || section.duration_frames === 0) return null
          return (
            <Sequence key={section.name} from={section.start_frame} durationInFrames={section.duration_frames}>
              <Component />
            </Sequence>
          )
        })}
      </AbsoluteFill>
      {/* 进度条放在 scale(2) 容器外部 */}
      <ChapterProgressBar />
    </AbsoluteFill>
  )
}

export const VideoPodcastMakerV2Thumbnail16x9 = () => (
  <AbsoluteFill style={{ background: '#fff', fontFamily: font, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: 24, marginBottom: 30 }}>
      <div style={{ fontSize: 120, fontWeight: 800, color: colors.accent }}>Video Podcast Maker</div>
      <div style={{ background: colors.green, color: '#fff', padding: '12px 24px', borderRadius: 12, fontSize: 48, fontWeight: 700 }}>V2 New</div>
    </div>
    <div style={{ fontSize: 64, color: colors.text, marginBottom: 40 }}>一行命令 · 话题到4K成片</div>
    <div style={{ display: 'flex', gap: 24 }}>
      {['14步自动', '中英TTS', '4K输出', 'B站优化'].map((t, i) => (
        <div key={i} style={{ background: colors.accent, color: '#fff', padding: '16px 28px', borderRadius: 12, fontSize: 36, fontWeight: 600 }}>{t}</div>
      ))}
    </div>
  </AbsoluteFill>
)

export const VideoPodcastMakerV2Thumbnail4x3 = () => (
  <AbsoluteFill style={{ background: '#fff', fontFamily: font, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 20 }}>
      <div style={{ fontSize: 100, fontWeight: 800, color: colors.accent }}>Video Podcast Maker</div>
      <div style={{ background: colors.green, color: '#fff', padding: '10px 20px', borderRadius: 10, fontSize: 40, fontWeight: 700 }}>V2</div>
    </div>
    <div style={{ fontSize: 56, color: colors.text, marginBottom: 30 }}>话题 → 4K成片</div>
    <div style={{ fontSize: 48, color: colors.green, fontWeight: 700 }}>全自动 · 十分钟</div>
  </AbsoluteFill>
)
