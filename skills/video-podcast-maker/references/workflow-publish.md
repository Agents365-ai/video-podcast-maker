# Video Podcast Maker — Workflow Phase 3: Publish

> **When to load:** Load after the 4K video is rendered with BGM, or when the user asks about subtitles, publish info, cleanup, verification, or generating vertical shorts.
>
> **Covers:** Steps 12-15 (subtitles → publish info → verify + cleanup → optional vertical shorts).
>
> **Previous phase:** See `workflow-production.md` for Steps 6-11.

## Contents

- [Step 12: Finalize (optional legacy subtitle burn)](#step-12-finalize-optional-legacy-subtitle-burn)
- [Step 13: Complete Publish Info (Part 2)](#step-13-complete-publish-info-part-2)
- [Step 14: Verify Output & Cleanup](#step-14-verify-output--cleanup)
- [Step 15: Generate Vertical Shorts (Optional)](#step-15-generate-vertical-shorts-optional)

---

## Step 12: Finalize (optional legacy subtitle burn)

> **Decision point: pick subtitle approach BEFORE Step 10, not here.**
>
> Subtitles are normally baked into `output.mp4` during Step 10's Remotion
> render via `<Subtitles src={staticFile("podcast_audio.srt")} />` in
> `Video.tsx`. Once Step 10 runs with that component in place, subtitles are
> already inside the pixel stream — re-burning at Step 12 would double up.
>
> **Default (Remotion-native subtitles in Step 10):** Step 12 is a finalize/alias
> step. Copy `video_with_bgm.mp4` to `final_video.mp4` and move on.
>
> **Legacy FFmpeg burn (rare):** Only choose this if Step 10 was rendered
> *without* the `<Subtitles>` component (e.g. you removed it for a karaoke
> effect, or you're re-burning into an older render). In that case render
> Step 10 with subtitles disabled, then run the FFmpeg pass below.

**Auto mode:** Skip subtitles — copy `video_with_bgm.mp4` as `final_video.mp4`.
**Interactive mode:** Ask user: "Add burned-in subtitles? (Usually not needed — Remotion renders subtitles natively)"

### Subtitle Preferences

Read `subtitle` preferences. If `subtitle.enabled == false`, skip subtitle burning (copy video_with_bgm.mp4 as final_video.mp4).

If FFmpeg subtitle burn is explicitly requested (legacy/special cases only):

Resolve `fontName: "auto"` by `language`:
- zh-CN → `PingFang SC`
- en-US → `Arial`

```bash
# Alignment=2: bottom-center. MarginV uses ASS PlayResY (default 288), NOT video pixels.
# MarginV=6 ≈ 6/288 = ~2% from bottom edge, good for all resolutions.
# WARNING: Only burn from video_with_bgm.mp4, NEVER from final_video.mp4 (avoids double-burn).
ffmpeg -y -i videos/{name}/video_with_bgm.mp4 \
  -vf "subtitles=videos/{name}/podcast_audio.srt:force_style='FontName=PingFang SC,FontSize=20,PrimaryColour=&H00333333,OutlineColour=&H00FFFFFF,Bold=0,Outline=2,Shadow=0,Alignment=2,MarginV=6'" \
  -c:v libx264 -crf 18 -preset slow -s 3840x2160 \
  -c:a copy videos/{name}/final_video.mp4
```

If skipping (default for Remotion-native subtitle videos):
```bash
cp videos/{name}/video_with_bgm.mp4 videos/{name}/final_video.mp4
```

---

## Step 13: Complete Publish Info (Part 2)

Generate Bilibili chapters from `timing.json`:

```
00:00 Opening
00:23 Features
00:55 Demo
01:20 Summary
```

Format: `MM:SS Chapter Title`, each gap ≥5s.

### Publish Info Format by Platform

**Agent behavior:** Generate publish info matching `platform` preference.

**bilibili format:**
- 标题公式、标签、简介
- 章节时间戳 (if `content.chapters == true`)

**youtube format:**
- SEO-optimized title (<70 chars)
- Keyword-rich description with timestamps
- Tags and hashtags (#tag1 #tag2)
- Chapters (if `content.chapters == true`, first line must be `0:00`)

**xiaohongshu format:**
- 标题（≤20字）— short, punchy, emoji-friendly
- 正文（200-500字）— 种草/knowledge-sharing style with emoji
- 话题标签 5-10 个，格式 `#话题#`（双井号）
- 无章节时间戳（小红书不支持）

**douyin format:**
- 文案（100-200字）— casual, emoji-friendly, conversational tone
- 话题标签 3-8 个，格式 `#话题`（单井号）
- 无章节时间戳
- Note: Douyin is shorts-only — no horizontal long-form video

**weixin-channels format:**
- 文案（100-300字）— knowledge-sharing style, suitable for forwarding
- 话题标签 3-8 个，格式 `#话题`（单井号）
- 无章节时间戳
- Note: WeChat Channels is shorts-only — no horizontal long-form video

---

## Step 14: Verify Output & Cleanup

### 14.1 Verification

Run the unified verifier — it checks all required files, validates technical specs, audits audio/timing alignment, sanity-checks publish_info.md, AND **auto-fixes common omissions** (e.g. creates `final_video.mp4` from `video_with_bgm.mp4` when subtitles were skipped but the alias step was missed; disable with `--no-fix`).

```bash
python3 ${SKILL_DIR}/scripts/verify_output.py videos/{name}/
```

Exit codes (preserved across all output formats):
- `0` = all required files present and valid → ready to publish
- `1` = critical missing or invalid → fix before publishing
- `2` = warnings only → still publishable, review noted issues

**Flags:**
- `--strict` — treat any warning as a critical issue (exit 1 instead of 2)
- `--no-fix` — skip the auto-fix step; preview only (useful for diagnosing what *would* change before any mutation)
- `--format auto|json|prose` — `auto` (default) emits JSON when stdout is not a TTY; force with `--format json` for orchestrators that need to parse results programmatically; force prose with `--format prose`

Structured envelope on `--format json`:

```bash
python3 ${SKILL_DIR}/scripts/verify_output.py videos/{name}/ --format json
# Success: {"ok": true,  "data": {"final_video": {...}, "thumbnails": {...}, "audio_timing": {...}, "final_video_sync": {...}, "warnings": [...], "fixes_applied": [...]}, "meta": {...}}
# Failure: {"ok": false, "error": {"code": "validation_failed", "missing_required": [...], "errors": [...], "warnings": [...]}, "meta": {...}}
```

What it checks:
- Required files: podcast.txt, podcast_audio.{wav,srt}, timing.json, output.mp4, **final_video.mp4**, publish_info.md, both thumbnails
- Final video specs: 3840×2160 (or 2160×3840 vertical), h264 + aac, has audio track, duration plausible
- Thumbnail dimensions: 1920×1080 (16:9) and 1200×900 (4:3) — each aspect ratio accepts either `thumbnail_remotion_*.png` or `thumbnail_ai_*.png`, only flagged missing when both alternatives are absent
- Audio/timing drift: WAV duration matches timing.json within 0.5s (uses an audio-only ffprobe pass so .wav containers don't false-fail)
- Final video / audio sync: final_video.mp4 duration matches podcast_audio.wav within 0.5s — the rendered/mixed output must stay locked to the master clock
- publish_info.md: contains promo line + per-platform required section headers (bilibili: 标题/标签/简介/章节; youtube: Title/Tags/Description/Chapters; xiaohongshu/douyin/weixin-channels: shorter set without chapters) — resolved from `user_prefs.json` → `global.platform`, defaults to bilibili

What it auto-fixes:
- Creates `final_video.mp4` from `video_with_bgm.mp4` if missing (subtitles-skipped path)
- Falls back to `output.mp4` if no BGM mix exists yet (with warning to run Step 11)

### 14.2 Cleanup

**Both modes:** Only clean TTS temp files (part_*.wav, concat_list.txt) automatically. **NEVER delete output.mp4 or video_with_bgm.mp4** until the user has reviewed final_video.mp4 and explicitly confirmed it's acceptable. These files are needed to re-do BGM/subtitle steps without a full re-render (~8 min).

```bash
VIDEO_DIR="videos/{name}"
# Safe to auto-clean: TTS intermediate files only
rm -f "$VIDEO_DIR"/part_*.wav "$VIDEO_DIR"/concat_list.txt
echo "✓ TTS temp files cleaned"
echo ""
echo "Kept (delete manually after confirming final_video.mp4):"
echo "  output.mp4 — clean render without BGM/subtitles"
echo "  video_with_bgm.mp4 — render with BGM, no subtitles"
```

### 14.3 Final Report

```
=== Video Complete ===
✓ File: final_video.mp4
✓ Resolution: 3840x2160 (4K)
✓ Duration: XXs
✓ Size: XXX MB
✓ Thumbnails: thumbnail_remotion_16x9.png, thumbnail_remotion_4x3.png
✓ Publish info: publish_info.md
✓ Temp files cleaned
```

---

## Step 15: Generate Vertical Shorts (Optional)

**When:** After long-form video is complete (Step 14). Optional step.

**Agent behavior:** Offer to generate vertical shorts. If user agrees, run automatically.

### Generate shorts from sections

```bash
python3 ${SKILL_DIR}/scripts/generate_shorts.py --input-dir videos/{name}/ --title "视频标题"
```

This produces `videos/{name}/shorts/{section_name}/` for each qualifying section (>20s, not hero/outro) with:
- `short_audio.wav` — extracted audio slice
- `short_timing.json` — timing for intro (3s) + content + CTA (3s)
- `short_info.json` — composition metadata
- `register_snippet.tsx` — Root.tsx registration code

### Create short compositions

For each generated short:
1. Copy `templates/ShortVideo.tsx` as `src/remotion/{SectionName}ShortVideo.tsx`
2. Replace `SectionContent` placeholder with the actual section component from the long-form video
3. Update `SHORT_CONFIG` with values from `short_info.json`
4. Register composition in `Root.tsx` using `register_snippet.tsx`
5. Ensure `short_audio.wav` is in the short's directory (used via `--public-dir`)

### Render shorts

Each short renders from its own per-short directory because it has its own
`short_audio.wav` and `short_timing.json`. Match the convention used by
`generate_shorts.py --render`:

```bash
npx remotion render src/remotion/index.ts {CompId} \
  videos/{name}/shorts/{section}/{CompId}.mp4 \
  --video-bitrate 16M \
  --public-dir videos/{name}/shorts/{section}/
```

(Do **not** use `--public-dir videos/{name}/` for shorts — Remotion would
load the long-form `podcast_audio.wav`/`timing.json` instead of the short's
sliced assets and the render would drift.)

Each short is a standalone 9:16 4K video (2160×3840) with:
- 3-second intro title card
- Section content (vertical layout, all components auto-adapt)
- 3-second CTA card ("关注看完整版")
