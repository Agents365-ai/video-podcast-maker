import { AbsoluteFill } from 'remotion'

const font = "'PingFang SC', 'Noto Sans SC', sans-serif"

const ThumbnailBase = ({
  title = '视频封面标题',
  subtitle = '副标题铺满整个画面宽度区域',
  tags = ['标签A', '标签B'],
  icons = ['🚀', '⚡', '🔥'],
  compact = false,
}: {
  title?: string
  subtitle?: string
  tags?: string[]
  icons?: string[]
  compact?: boolean
}) => {
  const titleSize = compact ? 150 : 160
  const subtitleSize = compact ? 56 : 60

  return (
    <AbsoluteFill style={{
      background: '#ffffff',
      fontFamily: font,
    }}>
      <div style={{
        position: 'absolute',
        inset: 0,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        padding: '40px 50px',
        gap: 24,
      }}>
        {/* Tags + Icons row */}
        <div style={{ display: 'flex', gap: 20, alignItems: 'center' }}>
          {tags.map((tag, i) => (
            <div key={i} style={{
              background: 'rgba(249,115,22,0.1)',
              border: '3px solid rgba(249,115,22,0.3)',
              borderRadius: 24,
              padding: '14px 36px',
              fontSize: 44,
              fontWeight: 700,
              color: '#f97316',
            }}>{tag}</div>
          ))}
          {icons.map((icon, i) => (
            <span key={i} style={{ fontSize: 80 }}>{icon}</span>
          ))}
        </div>

        {/* Title */}
        <div style={{
          fontSize: titleSize,
          fontWeight: 900,
          letterSpacing: 6,
          color: '#1a1a2e',
          lineHeight: 1.2,
          textAlign: 'center',
        }}>
          {title}
        </div>

        {/* Subtitle */}
        <div style={{
          fontSize: subtitleSize,
          fontWeight: 700,
          color: '#666',
          letterSpacing: 2,
          textAlign: 'center',
        }}>
          {subtitle}
        </div>
      </div>
    </AbsoluteFill>
  )
}

export const Thumbnail16x9 = () => <ThumbnailBase />

export const Thumbnail4x3 = () => (
  <ThumbnailBase
    title="视频封面标题"
    subtitle="副标题铺满整个画面宽度"
    compact
  />
)
