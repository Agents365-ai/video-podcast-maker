# Video Podcast Maker — Regenerating an Existing Video

> **When to load:** The user is iterating on a video this skill already produced — "regenerate", "re-render", "rebuild", "I edited the script/prompt", "update the video", "change the BGM".

If `videos/{name}/` **already exists** and the user is iterating on a finished or in-progress video, **reuse that directory**. Do NOT start a new project or a new `videos/{newname}/`; that is the **Single Project** rule (SKILL.md → Hard Rules) applied to iteration, and starting fresh is the most common mistake here.

Pick the **smallest** re-run for what actually changed. Every command targets the *same* `videos/{name}/`, and every Remotion command keeps `--public-dir videos/{name}/`:

| Changed | Re-run | Reuses (don't redo) |
| --------- | -------- | --------------------- |
| Narration script (`podcast.txt`) | Step 8 (`generate_tts.py --output-dir videos/{name}`) → Step 9 preview → Step 10 render (on explicit confirm) → Step 11 BGM | topic research + section design |
| Visuals only (components, layout, colors, props) | Step 9 preview → Step 10 render (on explicit confirm) | `podcast_audio.wav` / `timing.json` (audio unchanged) |
| Background music only | Step 11 mix | `output.mp4` (no re-render) |
| Subtitles only | Step 12 | `output.mp4` / `video_with_bgm.mp4` |

Any re-run that changes what the viewer **sees or hears** re-enters the Step 9 gate: apply the change, let Studio hot-reload (or relaunch it), and wait for a fresh explicit "render 4K" — the confirmation that started the previous render does **not** carry over to the adjusted version. Only the audio-untouched post-render steps (BGM mix, subtitles) skip the gate.

A **script** change shifts every downstream timestamp, so always regenerate `timing.json` through TTS — never hand-edit it (see [audio-sync.md](audio-sync.md)). After any re-run, re-verify:

```bash
python3 ${SKILL_DIR}/scripts/verify_output.py videos/{name}/
```

> Cleanup only removes TTS temp files, never `output.mp4` / `video_with_bgm.mp4` — so BGM/subtitle re-runs avoid a full ~8-min re-render.
