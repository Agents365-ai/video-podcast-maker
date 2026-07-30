# Changelog

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
  discovery looks for the lowercase dir names only. The `*_HOME` env vars
  (`TTSCN_HOME`, `IMAGENCN_HOME`, `VIDEOGENCN_HOME`, `ASSETSEEKER_HOME`) are
  unchanged. Linux users with an old capitalized install dir should rename
  the dir or set the corresponding `*_HOME` env var.

### Changed

- docs(tts): the bridge's consecutive-identical-token merge in
  `_merge_native_boundaries` is now framed as a generic normalization step —
  any platform may split one source token into per-syllable boundary entries;
  MiniMax is just the known example. No behavior change.
