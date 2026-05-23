# Kinetic Typography Preset

A bold, type-driven preset inspired by reference style: black-ish background, oversized Chinese typography, two-color accent system, character-pop and marker-reveal animations, ambient particle/glow background. No card layouts, no icons in body — text is the visual.

## When to use

- Topic is **opinion / argument / declaration** (not a tutorial or product walkthrough)
- Script is naturally short-sentence, punch-line driven
- You want a **distinctive look** that breaks out of the standard card-based design
- Audience is younger / video-platform-native (Bilibili, Douyin, TikTok)
- Each beat conveys a single idea in 1-3 short lines

Examples that fit:
- "AI 时代如何学专业知识" (this preset's origin)
- "为什么大公司都在做 X"
- "停止做 Y 的 5 个理由"
- Manifesto / culture / mindset videos

## When NOT to use

- Technical tutorials with code blocks, screenshots, diagrams
- Product comparisons with feature tables
- Long explanations needing detailed visual support
- News-anchor-style narration with B-roll
- Stories with characters, settings, scenes

## Files

| File | Purpose |
|---|---|
| `Video.tsx.template` | Main composition with KineticBeat + ParticleField + GlowOrbs + VerticalDecor |
| `Thumbnail.tsx.template` | Black BG + huge white title + mint marker subtitle |
| `colors.json` | Recommended palette + variants |
| `voice.json` | Recommended TTS settings |
| `motion.json` | Animation timing constants (entrance/exit, character delays) |

## Quick start

1. Plan your script as **8-15 short punch lines per section**, each fitting on screen as 1-3 lines (no paragraphs)
2. Generate TTS first (you NEED the SRT for accurate beat timing):
   ```bash
   AZURE_TTS_VOICE=zh-CN-XiaoxiaoNeural TTS_STYLE="" TTS_RATE=+5% \
     python3 ${SKILL_DIR}/scripts/generate_tts.py \
     -i videos/{name}/podcast.txt -o videos/{name}/
   ```
3. Copy templates:
   ```bash
   cp ${SKILL_DIR}/templates/presets/kinetic-typography/Video.tsx.template \
      src/remotion/{Name}Video.tsx
   cp ${SKILL_DIR}/templates/presets/kinetic-typography/Thumbnail.tsx.template \
      src/remotion/{Name}Thumbnail.tsx
   ```
4. **Use SRT timestamps as beat startSec** — open `videos/{name}/podcast_audio.srt` and pick the start of each phrase you want to land on screen at that moment. Fill into `SECTION_BEATS` arrays in the .tsx file.
5. Audit alignment before render:
   ```bash
   python3 ${SKILL_DIR}/scripts/audit_beat_sync.py \
     src/remotion/{Name}Video.tsx \
     videos/{name}/timing.json
   ```
   Iterate until all beats are within 1.5s of an SRT boundary.
6. Studio preview, then render 4K.

## Design rules specific to this preset

- **Background**: dark navy `#08091A` (NOT pure black — adds warmth and lets accent colours pop)
- **Two accent colours**: mint `#5EEAD4` for primary punch, yellow `#FACC15` for warnings/numbers/contrast
- **Typography**: 100-280px range. Most beats have a small line + a HUGE punch line (3-4× size delta)
- **Marker style**: secondary lines use `marker: true` for skewed mint/yellow handwritten-feel reveal
- **No flash strobe** — see `references/design-guide.md` Animation Safety. Soft pulses only.
- **Side decor**: persistent vertical-rl chapter markers and topic tag on left/right edges (low opacity)
- **One concept per beat** — never cram 4+ lines

## Common mistakes

- ❌ Using weight-based beat distribution → drift. Always use SRT-derived `startSec`.
- ❌ Cramming long sentences into one beat → text feels stuck while narrator finishes
- ❌ Skipping middle narration concepts → visual freezes for 5+ seconds while audio runs ahead
- ❌ Using Multilingual voice for an AI-mention-heavy script → vocoder artifacts (see `references/azure-tts-pitfalls.md`)
- ❌ Reusing same beat variant for entire section → monotonous; mix `pop`/`flash`/`numbered`/`quote`/`title`
