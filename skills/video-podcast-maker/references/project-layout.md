# Video Podcast Maker — Per-Video Layout

> **When to load:** When creating the per-video directory, running any Remotion command, or naming videos/sections/thumbnails.

```
project-root/                           # Remotion project root
├── src/remotion/                       # Remotion source (Root.tsx, compositions, index.ts)
├── videos/{video-name}/                # Per-video assets (the agent's working dir)
│   ├── topic_definition.md             # Step 1
│   ├── topic_research.md               # Step 2
│   ├── podcast.txt                     # Step 4: narration script
│   ├── phonemes.json                   # Step 4.5: zh-CN pronunciation overrides
│   ├── assets/manifest.json            # Step 5: per-section asset registry
│   ├── publish_info.md                 # Steps 6+13: title/description/tags
│   ├── podcast_audio.wav               # Step 8: TTS audio
│   ├── podcast_audio.srt               # Step 8: subtitles
│   ├── timing.json                     # Step 8: timeline (drives animations)
│   ├── thumbnail_*.png                 # Step 7
│   ├── output.mp4                      # Step 10: 4K render (no BGM)
│   ├── video_with_bgm.mp4              # Step 11
│   ├── final_video.mp4                 # Step 12: final output
│   └── bgm.mp3                         # Background music
└── remotion.config.ts
```

## `--public-dir` per video

Remotion commands MUST use `--public-dir videos/{name}/` — each video's assets stay in its own directory, no copy to `public/`. Enables parallel renders.

```bash
npx remotion studio src/remotion/index.ts --public-dir videos/{name}/
npx remotion render src/remotion/index.ts CompositionId videos/{name}/output.mp4 --public-dir videos/{name}/ --video-bitrate 16M
npx remotion still src/remotion/index.ts Thumbnail16x9 videos/{name}/thumbnail.png --public-dir videos/{name}/
```

## Naming

- **Video name `{video-name}`**: lowercase English, hyphen-separated (e.g. `reference-manager-comparison`)
- **Section name `{section}`**: lowercase English, underscore-separated, matches `[SECTION:xxx]`
- **Thumbnail naming** (16:9 AND 4:3 both required):

| Type | 16:9 | 4:3 |
|------|------|-----|
| Remotion | `thumbnail_remotion_16x9.png` | `thumbnail_remotion_4x3.png` |
| AI | `thumbnail_ai_16x9.png` | `thumbnail_ai_4x3.png` |
