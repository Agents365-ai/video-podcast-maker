import { AbsoluteFill } from 'remotion'

const font = "'PingFang SC', 'Noto Sans SC', sans-serif"

const ThumbnailBase = ({
  title = '视频封面占满',
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
      background: 'linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%)',
      fontFamily: font,
    }}>
      <div style={{
        position: 'absolute',
        inset: 0,
        padding: '40px 50px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
      }}>
        {/* Row 1: Tags row */}
        <div style={{ display: 'flex', gap: 20, alignItems: 'center' }}>
          {tags.map((tag, i) => (
            <div key={i} style={{
              background: 'rgba(249,115,22,0.25)',
              border: '3px solid rgba(249,115,22,0.5)',
              borderRadius: 24,
              padding: '14px 36px',
              fontSize: 44,
              fontWeight: 700,
              color: '#fb923c',
            }}>{tag}</div>
          ))}
          {/* Icons on right side of tags row */}
          <div style={{ marginLeft: 'auto', display: 'flex', gap: 20 }}>
            {icons.map((icon, i) => (
              <span key={i} style={{ fontSize: 80 }}>{icon}</span>
            ))}
          </div>
        </div>

        {/* Row 2: Title — large, spanning full width */}
        <div style={{
          fontSize: titleSize,
          fontWeight: 900,
          letterSpacing: 8,
          color: '#fff',
          lineHeight: 1.2,
          textAlign: 'center',
        }}>
          {title}
        </div>

        {/* Row 3: Subtitle bar — full width colored band */}
        <div style={{
          background: 'rgba(255,255,255,0.08)',
          borderRadius: 20,
          padding: '20px 40px',
          textAlign: 'center',
        }}>
          <div style={{
            fontSize: subtitleSize,
            fontWeight: 700,
            color: 'rgba(255,255,255,0.75)',
            letterSpacing: 3,
          }}>
            {subtitle}
          </div>
        </div>
      </div>
    </AbsoluteFill>
  )
}

export const Thumbnail16x9 = () => <ThumbnailBase />

export const Thumbnail4x3 = () => (
  <ThumbnailBase
    title="视频封面占满"
    subtitle="副标题铺满整个画面宽度"
    compact
  />
)
