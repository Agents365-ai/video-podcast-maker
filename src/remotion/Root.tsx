import { Composition } from 'remotion'
import { z } from 'zod'
import { PodcastVideo } from './Video'
import { Thumbnail16x9, Thumbnail4x3 } from './Thumbnail'

// Import timing data - copy to public/ before running
// cp videos/{name}/timing.json public/
let timingData = { total_frames: 900, fps: 30 }
try {
  timingData = require('../../public/timing.json')
} catch {
  console.log('Using default timing (900 frames). Copy timing.json to public/ for actual sync.')
}

const videoSchema = z.object({
  primaryColor: z.string().default('#4f6ef7'),
  backgroundColor: z.string().default('#ffffff'),
  textColor: z.string().default('#1a1a2e'),
  titleSize: z.number().min(60).max(120).default(80),
  showProgressBar: z.boolean().default(true),
  bgmVolume: z.number().min(0).max(0.3).default(0.05),
})

export const RemotionRoot = () => (
  <>
    <Composition
      id="PodcastVideo"
      component={PodcastVideo}
      durationInFrames={timingData.total_frames}
      fps={timingData.fps}
      width={3840}
      height={2160}
      schema={videoSchema}
      defaultProps={{
        primaryColor: '#4f6ef7',
        backgroundColor: '#ffffff',
        textColor: '#1a1a2e',
        titleSize: 80,
        showProgressBar: true,
        bgmVolume: 0.05,
      }}
    />
    <Composition
      id="Thumbnail16x9"
      component={Thumbnail16x9}
      durationInFrames={1}
      fps={30}
      width={1920}
      height={1080}
    />
    <Composition
      id="Thumbnail4x3"
      component={Thumbnail4x3}
      durationInFrames={1}
      fps={30}
      width={1200}
      height={900}
    />
  </>
)
