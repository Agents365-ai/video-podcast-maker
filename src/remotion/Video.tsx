import { AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame, interpolate } from 'remotion'

// Import timing data
let timingData = { sections: [], fps: 30, total_frames: 900 }
try {
  timingData = require('../../public/timing.json')
} catch {
  // Use defaults
}

interface Section {
  name: string
  start_frame: number
  duration_frames: number
  is_silent?: boolean
}

interface VideoProps {
  primaryColor: string
  backgroundColor: string
  textColor: string
  titleSize: number
  showProgressBar: boolean
  bgmVolume: number
}

// Section component - customize per section
const SectionContent = ({ name, textColor, titleSize }: { name: string; textColor: string; titleSize: number }) => {
  const frame = useCurrentFrame()
  const opacity = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: 'clamp' })
  const translateY = interpolate(frame, [0, 15], [20, 0], { extrapolateRight: 'clamp' })

  const sectionTitles: Record<string, string> = {
    hero: 'Welcome',
    features: 'Features',
    demo: 'Demo',
    summary: 'Summary',
    outro: 'Thanks for watching!',
  }

  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
      <div style={{ opacity, transform: `translateY(${translateY}px)`, textAlign: 'center' }}>
        <h1 style={{ fontSize: titleSize, color: textColor, fontFamily: 'PingFang SC, sans-serif', fontWeight: 700 }}>
          {sectionTitles[name] || name}
        </h1>
      </div>
    </AbsoluteFill>
  )
}

export const PodcastVideo = ({ primaryColor, backgroundColor, textColor, titleSize, showProgressBar }: VideoProps) => {
  const sections = timingData.sections as Section[]

  return (
    <AbsoluteFill style={{ background: backgroundColor }}>
      {/* Audio track */}
      <Audio src={staticFile('podcast_audio.wav')} />

      {/* 4K wrapper with scale(2) for 1080p-style design */}
      <AbsoluteFill style={{ transform: 'scale(2)', transformOrigin: 'top left', width: '50%', height: '50%' }}>
        {/* Render sections from timing.json */}
        {sections.map((section) => (
          <Sequence key={section.name} from={section.start_frame} durationInFrames={section.duration_frames + (section.is_silent ? 150 : 0)}>
            <SectionContent name={section.name} textColor={textColor} titleSize={titleSize} />
          </Sequence>
        ))}

        {/* Progress bar */}
        {showProgressBar && (
          <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, height: 8, background: '#e0e0e0' }}>
            <ProgressBar color={primaryColor} />
          </div>
        )}
      </AbsoluteFill>
    </AbsoluteFill>
  )
}

const ProgressBar = ({ color }: { color: string }) => {
  const frame = useCurrentFrame()
  const progress = (frame / timingData.total_frames) * 100
  return <div style={{ width: `${progress}%`, height: '100%', background: color }} />
}
