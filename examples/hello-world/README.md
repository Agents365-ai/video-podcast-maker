# Hello World Example

A minimal example demonstrating the video-podcast-maker workflow.

## Files

- `podcast.txt` - Example narration script with section markers
- `timing.json` - Example timing data (simulated TTS output)

## Usage

1. Generate TTS audio:
```bash
cd /path/to/video-podcast-maker
python3 generate_tts.py --input examples/hello-world/podcast.txt --output-dir examples/hello-world
```

2. Copy files to public for Remotion:
```bash
cp examples/hello-world/podcast_audio.wav examples/hello-world/timing.json public/
```

3. Preview in Remotion Studio:
```bash
npm run studio
```

4. Render video:
```bash
npx remotion render src/remotion/index.ts PodcastVideo examples/hello-world/output.mp4 --video-bitrate 16M
```

## Output

After running the workflow, you'll have:
- `podcast_audio.wav` - TTS audio
- `podcast_audio.srt` - Subtitles
- `output.mp4` - Final video
