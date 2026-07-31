# Changelog

## 5.2.0

### Security

- **learn_design --delete / --show:** reference ids are now slug-validated and
  containment-checked at both the CLI boundary and the rmtree site — a crafted
  id like `../../target` could previously delete outside the reference library.
- **assets add --file:** asset ids must match a slug grammar — a crafted id could
  copy files outside the video directory. Non-object manifest roots now produce
  a clean validation error instead of an AttributeError traceback.

### Fixed

- **ShortVideo.tsx transition math:** each fade now compensates exactly one
  transition per sequence — previously every short's CTA card was truncated by
  10 frames and narration started 10 frames before the content visuals.
- **Silent sections:** `is_silent` is now honored by the Remotion templates —
  trailing outros get the documented 150-frame floor, are excluded from the
  proportional scale, and rounding lands on the last non-silent section. A
  middle silent section no longer squeezes the preceding section to ~0s.
- **verify_output.py acceptance gate:** required files and thumbnails are now
  platform-derived. The mandatory pre-publish gate was unpassable for
  xiaohongshu (3:4 thumbnail) and douyin/weixin-channels (shorts-only, no
  long-form render). The h264 + aac @ ~30fps render contract is now enforced,
  and WAV/timing drift beyond 0.5s is a hard error instead of a publishable
  warning. `--no-fix` preview no longer seeds `~/.video-podcast-maker/`.
- **ttscn chunk durations:** each part is measured with ffprobe instead of
  trusting the envelope's `duration_seconds` (e.g. Azure SSML under-reporting)
  — subtitles and section boundaries no longer drift after short-reported
  chunks.
- **Prefs migration:** learn_design's in-memory migration now applies the same
  structural transforms as migrate_prefs.py (single shared implementation) —
  it no longer deep-merges-and-stamps, which stranded old keys.
- **learn_design frame extraction:** a failed extraction (missing/oversized
  file, bad duration, ffmpeg missing/crash) is no longer indexed as a usable
  zero-frame reference.
- **audit_beat_sync:** unmapped/unparseable sections fail the gate (previously
  passed silently); beat text is compared against the narration overlapping
  its range; unexpected exceptions emit an envelope instead of a traceback.
- **phonemes merge path:** the template now resolves to the skill root, so
  existing global dictionaries actually receive newly bundled entries.
- **generate_shorts --render:** partial render failures now exit with an error
  envelope instead of success-as-long-as-one-short-rendered.
- **Read-as annotations:** the quote class matches curly quotes; section
  anchors are re-normalized with the same pinyin/read-as transforms as the
  narration text.
- **Rules of Hooks:** useEntrance/useBarFill/useCounter are no longer called
  inside `.map()` in CodeBlock, FeatureGrid, DataBar, StatCounter, and
  Timeline.
- **Template defaults:** schema minima and defaults raised to the design-guide
  floors (hero title ≥84px, body ≥32px).

### Docs

- All step-number drift fixed (retired steps 13/15, "Step 11" BGM mix →
  9.5, template copy step 9 → 8, "10 steps" → 11).
- Mutable state (`user_prefs.json`, `phonemes.json`) documented at
  `~/.video-podcast-maker/` everywhere; prefs version literals updated to 1.7.
- Added a doc-consistency regression test that validates every `Step N`
  mention across references/templates/scripts/READMEs against the canonical
  workflow step set.

## 5.1.0


### Added

- **Envelope schema assertion in the ttscn bridge.** The bridge now validates
  `meta.schema_version` on every ttscn JSON envelope (success and error)
  against the supported schema major (`1`). An incompatible major fails fast
  with an actionable message instead of silently misreading the envelope;
  an absent `schema_version` (pre-contract ttscn) is accepted. The contract
  is documented in ttscn's SKILL.md and the bridge module docstring.

## 5.0.0

### Breaking Changes

- **Removed the legacy `ttscn` backend alias and the `TTSCN_PLATFORM` env var.**
  Migration: set `TTS_BACKEND` to the platform id directly (e.g. `edge`,
  `azure`) — each backend id has routed 1:1 to the ttscn platform of the same
  name since v4.0.
- **Removed the six legacy per-backend voice env vars** (`AZURE_TTS_VOICE`,
  `EDGE_TTS_VOICE`, `VOLCENGINE_VOICE_TYPE`, `ELEVENLABS_VOICE_ID`,
  `OPENAI_TTS_VOICE`, `GOOGLE_TTS_VOICE`) **and `TTSCN_VOICE`.**
  Migration: use the generic `TTS_VOICE` env var, or persist per-backend
  voices in `user_prefs.json` under `global.tts.voices.<backend>`.
  Voice resolution precedence is now: `TTS_VOICE` > `user_prefs.json` >
  ttscn's per-platform default.
- **Renamed the four component skills to lowercase** for Pi compatibility
  (Pi requires lowercase skill names): `ttsCN` → `ttscn`, `imagenCN` →
  `imagencn`, `videogenCN` → `videogencn`, `assetSeeker` → `assetseeker`.
  Install/discovery dirs change accordingly (e.g. `~/.claude/skills/ttscn`);
  discovery matches directory names case-insensitively, so an existing
  `ttsCN`/`assetSeeker` install dir keeps working on case-sensitive
  filesystems too. The `*_HOME` env vars (`TTSCN_HOME`, `IMAGENCN_HOME`,
  `VIDEOGENCN_HOME`, `ASSETSEEKER_HOME`) are unchanged.

### Changed

- docs(tts): the bridge's consecutive-identical-token merge in
  `_merge_native_boundaries` is now framed as a generic normalization step —
  any platform may split one source token into per-syllable boundary entries;
  MiniMax is just the known example. No behavior change.
