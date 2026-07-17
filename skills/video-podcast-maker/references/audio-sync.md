# Video Podcast Maker — Audio-Master Clock & Sync

> **When to load:** Before generating TTS (Step 8) or building the Remotion composition (Step 9), and whenever audio/video durations disagree.

## Golden rules

1. **Audio is the master clock.** Every slide start, subtitle, progress-bar chapter, and animation beat is derived from `podcast_audio.wav` and `podcast_audio.srt`.
2. **Generate timing from TTS, not from text estimates.** The canonical pipeline is:

   ```
   podcast.txt (final)
     → generate_tts.py
     → podcast_audio.wav + podcast_audio.srt + timing.json
     → Remotion composition
     → render
   ```

3. **Never hand-write `timing.json` before audio exists.** If you already have curated slides, run `align_timing_from_srt.py` to anchor them to the real SRT, or add a `"section"` field to each slide and then run it.
4. **Compensate TransitionSeries overlap.** `TransitionSeries` renders `sum(section.duration_frames) - (N-1) * transitionFrames` frames. To keep the rendered length equal to `timing.total_frames`, scale every section proportionally; do **not** stuff all overlap frames into the first section. The corrected pattern is in `templates/Video.tsx`.

## Mandatory sync checkpoints

| When | Check | Command / Action |
| ------ | ------- | ------------------ |
| After Step 8 | `timing.json.total_duration` matches `podcast_audio.wav` within ±0.5s | `ffprobe -show_entries format=duration podcast_audio.wav` |
| Before Step 10 | `Video.tsx` scales all sections for transition overlap | Inspect the `compensatedSections` calculation |
| After Step 10/12 | `final_video.mp4` duration matches `podcast_audio.wav` within ±0.5s | `ffprobe -show_entries format=duration final_video.mp4` |
| Step 14 | `verify_output.py` exits 0 and reports green on audio/timing | `python3 ${SKILL_DIR}/scripts/verify_output.py videos/<name>/` |

If any checkpoint fails, stop. Do not publish.

## Output Specs

| Parameter | Horizontal (16:9) | Vertical (9:16) |
| ----------- | ------------------- | ----------------- |
| Resolution | 3840×2160 (4K) | 2160×3840 (4K) |
| Frame rate | 30 fps | 30 fps |
| Encoding | H.264, 16Mbps | H.264, 16Mbps |
| Audio | AAC, 192kbps | AAC, 192kbps |
| Duration | 1-15 min | 60-90s (highlight) |
