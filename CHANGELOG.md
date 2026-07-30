# Changelog

## 5.0.0

### Breaking Changes

- **Removed the legacy `ttscn` backend alias and the `TTSCN_PLATFORM` env var.**
  Migration: set `TTS_BACKEND` to the platform id directly (e.g. `edge`,
  `azure`) — each backend id has routed 1:1 to the ttsCN platform of the same
  name since v4.0.
- **Removed the six legacy per-backend voice env vars** (`AZURE_TTS_VOICE`,
  `EDGE_TTS_VOICE`, `VOLCENGINE_VOICE_TYPE`, `ELEVENLABS_VOICE_ID`,
  `OPENAI_TTS_VOICE`, `GOOGLE_TTS_VOICE`) **and `TTSCN_VOICE`.**
  Migration: use the generic `TTS_VOICE` env var, or persist per-backend
  voices in `user_prefs.json` under `global.tts.voices.<backend>`.
  Voice resolution precedence is now: `TTS_VOICE` > `user_prefs.json` >
  ttsCN's per-platform default.

### Changed

- docs(tts): the bridge's consecutive-identical-token merge in
  `_merge_native_boundaries` is now framed as a generic normalization step —
  any platform may split one source token into per-syllable boundary entries;
  MiniMax is just the known example. No behavior change.
