# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Language

Write all code, comments, commit messages, and documentation in English. Exception: `README.md` (Chinese documentation, default for GitHub display).

## Git Commits

Do NOT add "Co-Authored-By: Claude" to commit messages.

## What This Is

A Claude Code skill for automated video podcast creation targeting **B站横屏视频 (16:9)** with optional **竖屏精华片段 (9:16)**. The 14-step workflow is defined in `SKILL.md`.

### Documentation Structure

| File | Purpose | When Claude Loads |
|------|---------|-------------------|
| `SKILL.md` | Core workflow overview, execution modes, resume, technical rules | Always (skill invocation) |
| `references/workflow-steps.md` | Detailed step-by-step instructions (Steps 1-14) | At workflow start |
| `references/design-guide.md` | Visual minimums, typography, layout patterns, checklists | Step 9 (Remotion composition) |
| `references/troubleshooting.md` | Error fixes, preference commands, BGM options, preference learning | On error or user request |

## Key Commands

```bash
# TTS audio generation (3 backends)
python3 generate_tts.py --input videos/{name}/podcast.txt --output-dir videos/{name}                    # Azure (default)
TTS_BACKEND=cosyvoice python3 generate_tts.py --input videos/{name}/podcast.txt --output-dir videos/{name}  # CosyVoice
TTS_BACKEND=edge python3 generate_tts.py --input videos/{name}/podcast.txt --output-dir videos/{name}       # Edge TTS (free)

# TTS utilities
python3 generate_tts.py --input videos/{name}/podcast.txt --output-dir videos/{name} --dry-run   # Estimate duration, no API call
python3 generate_tts.py --input videos/{name}/podcast.txt --output-dir videos/{name} --resume    # Skip already-synthesized parts
TTS_RATE="+15%" python3 generate_tts.py ...                                                      # Control speech rate

# Remotion
npx remotion studio src/remotion/index.ts                                                         # Preview (always use before render)
npx remotion render src/remotion/index.ts CompositionId videos/{name}/output.mp4 --video-bitrate 16M  # 4K render
npx remotion render src/remotion/index.ts CompositionId videos/{name}/preview.mp4 --scale 0.33 --crf 28  # Quick 720p preview
npx remotion still src/remotion/index.ts Thumbnail16x9 videos/{name}/thumbnail_remotion_16x9.png  # Thumbnail
npx remotion render src/remotion/index.ts MyVideoVertical videos/{name}/output_vertical.mp4 --video-bitrate 16M  # Vertical 9:16
npx remotion still src/remotion/index.ts Thumbnail9x16 videos/{name}/thumbnail_remotion_9x16.png  # Vertical thumbnail

# Post-processing (FFmpeg)
ffmpeg -y -i videos/{name}/output.mp4 -stream_loop -1 -i videos/{name}/bgm.mp3 \
  -filter_complex "[0:a]volume=1.0[a1];[1:a]volume=0.05[a2];[a1][a2]amix=inputs=2:duration=first[aout]" \
  -map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 192k videos/{name}/video_with_bgm.mp4

ffmpeg -y -i videos/{name}/video_with_bgm.mp4 \
  -vf "subtitles=videos/{name}/podcast_audio.srt:force_style='FontName=PingFang SC,FontSize=14,PrimaryColour=&H00333333,OutlineColour=&H00FFFFFF,Bold=1,Outline=2'" \
  -c:v libx264 -crf 18 -preset slow -s 3840x2160 -c:a copy videos/{name}/final_video.mp4 \
|| ffmpeg -y -i videos/{name}/video_with_bgm.mp4 \
  -vf "subtitles=videos/{name}/podcast_audio.srt:fontsdir=skills/video-podcast-maker/assets/fonts:force_style='FontName=Source Han Sans SC,FontSize=14,PrimaryColour=&H00333333,OutlineColour=&H00FFFFFF,Bold=1,Outline=2'" \
  -c:v libx264 -crf 18 -preset slow -s 3840x2160 -c:a copy videos/{name}/final_video.mp4

# Vertical shorts generation
python3 generate_shorts.py --input-dir videos/{name}/ --title "视频标题"           # Generate short compositions
python3 generate_shorts.py --input-dir videos/{name}/ --title "视频标题" --render   # Generate + render all shorts
```

## Architecture

```
generate_tts.py                  # TTS (Azure/CosyVoice/Edge) + SRT + timing.json
generate_shorts.py               # Vertical shorts: section filtering, audio extraction, composition generation
SKILL.md                         # Core workflow overview (<500 lines)
references/
  workflow-steps.md              # Detailed step instructions (Steps 1-14)
  design-guide.md                # Visual design minimums, checklists
  troubleshooting.md             # Error fixes, BGM, preferences
templates/
  Video.tsx                      # Main composition — section renderer + audio + transitions
  Root.tsx                       # Remotion root, Zod schema for Studio props
  Thumbnail.tsx                  # Cover image component (16:9 + 4:3 + 9:16)
  ShortVideo.tsx                 # Short video composition template (intro + content + cta)
  podcast.txt                    # Script template with [SECTION:xxx] markers
  components/                    # Reusable visual building blocks
    index.ts                     # Barrel export
    layouts.tsx                  # Scale4K, FullBleedLayout, PaddedLayout
    animations.tsx               # useEntrance, useExit, useCounter, useBarFill, useDrawOn, useStaggeredDrawOn, getPresentation
    ComparisonCard.tsx           # Two-column VS layout with shadow depth
    Timeline.tsx                 # Vertical timeline with glowing nodes
    CodeBlock.tsx                # Dark terminal code display
    QuoteBlock.tsx               # Large quote with accent line and gradient bg
    FeatureGrid.tsx              # 2-3 column icon grid with layered shadows
    DataBar.tsx                  # Animated horizontal bar chart
    StatCounter.tsx              # Animated number tickers
    FlowChart.tsx                # Horizontal arrow-connected steps
    IconCard.tsx                 # Large icon emphasis card
    MediaSection.tsx             # Image/media display (full, card, grid layouts)
    ChapterProgressBar.tsx       # Bottom progress bar (renders outside Scale4K)
    AnimatedBackground.tsx       # MovingGradient, FloatingShapes, GridPattern, GlowOrb, AccentLine
    SectionLayouts.tsx           # SplitLayout, StatHighlight, ZigzagCards, CenteredShowcase, MetricsRow, StepProgress
    ShortIntroCard.tsx           # Full-screen title card for short video intros (3s)
    ShortCTACard.tsx             # End CTA card "关注看完整版" for shorts (3s)
    DiagramReveal.tsx            # General-purpose animated SVG diagram with draw-on effect (nodes + edges)
    AudioWaveform.tsx            # Real-time audio frequency visualization (bars, wave, dots modes)
    LottieAnimation.tsx          # After Effects animation player via @remotion/lottie (staticFile or URL)
assets/                          # BGM tracks, bilibili triple-click animations
```

### Data Flow

```
podcast.txt → generate_tts.py → podcast_audio.wav + podcast_audio.srt + timing.json
                                        ↓
                              copy to public/ directory
                                        ↓
                    Video.tsx reads timing.json → drives <TransitionSeries> timing
                                        ↓
                         npx remotion render → 4K MP4 (3840×2160)
                                        ↓
                         FFmpeg: mix BGM → burn subtitles → final_video.mp4
```

### generate_tts.py Internals

- **Backend dispatch**: `synth_azure()`, `synth_cosyvoice()`, `synth_edge()` — each returns `(part_files, word_boundaries, accumulated_duration)`
- **Phoneme system** (3-tier priority): inline markers `执行器[zhí xíng qì]` > project `phonemes.json` > built-in `BUILTIN_POLYPHONES` dict
- **Section matching**: sliding-window algorithm matches `[SECTION:xxx]` first_text against word_boundaries to compute precise timestamps
- **Resume**: `--resume` skips parts where `part_{i}.wav` already exists, uses ffprobe for duration
- **Output**: chunks text into ≤400 char segments, synthesizes each, merges with ffmpeg concat

### Template Architecture

- `templates/Video.tsx` is the **template** — copied as `{PascalCaseName}Video.tsx` per video, NEVER overwrite shared `Video.tsx`
- Each video gets its own composition file (e.g., `AiAgentsVideo.tsx`) with customized sections
- `Root.tsx` defines Zod schema for all Studio-editable props; shared across all videos, copy only if not present
- `Root.tsx` registers compositions — add per-video entries alongside `MyVideo` / `MyVideoVertical`
- `ChapterProgressBar` renders **outside** the `Scale4K` wrapper at native 4K resolution
- `TransitionSeries` compensates for overlap by adding lost frames to the first section
- All components are orientation-aware via `props.orientation` — vertical mode adapts layouts, font sizes, and spacing

### Icon System

- **Semantic names**: Use `"rocket"`, `"check"`, `"lightbulb"` — auto-resolved to Lucide SVG
- **Emoji fallback**: `"🚀"` still works — detected and rendered directly
- **Available icons**: See `templates/components/iconMap.ts` for full list (~80 icons)
- **Props**: `iconStyle` ("lucide"/"emoji"/"mixed"), `iconAnimation` ("entrance"/"none")

Common semantic names:
| Category | Names |
|----------|-------|
| Actions | rocket, check, x, plus, play, pause |
| Objects | lightbulb, target, star, heart, trophy, zap |
| Tech | code, terminal, database, server, cloud, cpu |
| Media | video, music, mic, camera |
| Social | thumbs-up, star, bell, share, bookmark |

## Critical Rules

- **Always 4K output** — horizontal 3840×2160, vertical 2160×3840 — use `transform: scale(2)` wrapper in Remotion
- **Use `npx remotion studio` for preview** — real-time debugging before final render
- **Silent sections** (`[SECTION:outro]` with empty content) get `is_silent: true` — Remotion adds 150 extra frames
- **Section markers** in `podcast.txt` must match Remotion component names exactly
- **Content width** ≥85% of screen, bottom 100px reserved for subtitles
- **Visual minimums** (MUST): hero ≥84px, section ≥72px, card title ≥40px, body ≥32px, any text ≥24px (see `references/design-guide.md` for full table)

## Environment Variables

```bash
export AZURE_SPEECH_KEY="..."      # Required for Azure TTS (default backend)
export AZURE_SPEECH_REGION="eastasia"
export DASHSCOPE_API_KEY="..."     # Required for CosyVoice TTS + AI thumbnails (imagenty)
export TTS_BACKEND="azure"         # Or "cosyvoice" or "edge" (free, no key needed)
export GEMINI_API_KEY="..."        # Optional: AI thumbnails (imagen)
export EDGE_TTS_VOICE="zh-CN-XiaoxiaoNeural"  # Optional: Edge TTS voice override
```

## User Preference System

Files: `user_prefs.json` (learned), `user_prefs.template.json` (defaults), `prefs_schema.json` (schema). See `references/troubleshooting.md` for preference commands, learning triggers, and troubleshooting.
