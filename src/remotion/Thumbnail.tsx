import { AbsoluteFill } from 'remotion'

const ThumbnailBase = ({ title = 'Video Title', subtitle = 'Subtitle here' }) => (
  <AbsoluteFill style={{
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 60,
  }}>
    <div style={{ textAlign: 'center', color: '#fff' }}>
      <h1 style={{
        fontSize: 72,
        fontWeight: 800,
        fontFamily: 'PingFang SC, sans-serif',
        margin: 0,
        textShadow: '0 4px 20px rgba(0,0,0,0.3)',
      }}>
        {title}
      </h1>
      <p style={{
        fontSize: 36,
        marginTop: 24,
        opacity: 0.9,
        fontFamily: 'PingFang SC, sans-serif',
      }}>
        {subtitle}
      </p>
    </div>
  </AbsoluteFill>
)

export const Thumbnail16x9 = () => <ThumbnailBase />
export const Thumbnail4x3 = () => <ThumbnailBase />
