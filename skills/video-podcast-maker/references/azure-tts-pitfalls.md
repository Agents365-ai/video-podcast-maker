# Azure TTS Pitfalls

> **When to load:** When choosing voice/style for the Azure backend, or when debugging hoarse / missing / glitchy audio. Skip for other backends.
>
> Since v4.0.0 Azure synthesis (SSML building, phoneme tags, English-term wrapping) runs inside the **ttsCN component skill** — but everything below still applies: voice choice, `TTS_STYLE`, and phoneme behavior ride through the bridge via env vars and `phonemes_resolved.json`.

The Azure neural-TTS engine is excellent in the common path but has several deterministic failure modes that have wasted hours of iteration. This file documents the known traps and how to avoid them.

---

## Voice selection

### Default: `zh-CN-XiaoxiaoNeural` (standard)

Use this for **content that is mostly Chinese with rare English abbreviations** (AI, ML, GPT, CLI, API, etc.). Chinese listeners read these abbreviations as letter-by-letter Chinese phonetics ("ei-ai", "em-el") in normal conversation — the standard voice produces exactly that, with no language switch and no artifacts.

### Use `zh-CN-XiaoxiaoMultilingualNeural` ONLY when:

- The script contains **substantial English passages** (sentences, paragraphs, dialogue)
- Heavy technical content with **proper nouns that genuinely need English pronunciation** (e.g. "Visual Studio Code", "Final Cut Pro", spoken URLs)
- Mixed bilingual narration where English flow matters

### Multilingual voice known issues:

| Issue | Manifestation | Workaround |
|---|---|---|
| **Vocoder artifact at lang switch** | Hoarse / strained sound when going Chinese-tone → English-letter → Chinese-consonant. E.g. "观点是，AI让答案" → "AI" sounds glitched | Switch to standard voice. Or rewrite phrase to avoid bare English token after Chinese tonal particle. |
| **SAPI phoneme tags are silently dropped** | `<phoneme alphabet="sapi" ph="ka 3 zhu 4">卡住</phoneme>` — surrounding text gets eaten, only tag content survives | Use standard voice (better SAPI support). Or remove inline phoneme markers — Azure usually pronounces common multi-character words correctly without override. |
| **Style support is inconsistent** | `style="serious"` / `"newscast"` may produce strained/hoarse output | Use empty `TTS_STYLE=""` to disable express-as wrapper; or stick to `gentle` / `cheerful`. |
| **Word boundary timing** | `result.audio_duration` may under-report when `<break>` / `<phoneme>` present | Reconciled automatically by `reconcile_timing_with_wav` in `srt.py` |

### Picking voice from content

The `tts/voice_advisor.py` module analyses your script and prints a recommendation at TTS startup. Heed its warnings. Override via `AZURE_TTS_VOICE` env var if you disagree.

---

## SSML pitfalls

### `<phoneme>` for Chinese with multilingual voice → text loss

**Symptom**: A line like "你没有被细节卡住" plays as only "卡住" — the preceding "你没有被细节" is missing from the audio.

**Cause**: Inline `卡住[kǎ zhù]` becomes `<phoneme alphabet="sapi" ph="ka 3 zhu 4">卡住</phoneme>`. Multilingual voice's SSML parser doesn't fully support SAPI Chinese phonemes; it silently drops the surrounding text in the same prosody block.

**Fix**:
1. Switch to standard `zh-CN-XiaoxiaoNeural` (better SAPI support), OR
2. Remove the `[pinyin]` annotation — Azure usually gets common compounds (重新, 卡住, 好的, 还是) right by default.

### `<break>` and `<phoneme>` skew duration accounting

**Symptom**: After regen, `timing.json` total is ~250s but the actual WAV is ~258s. Last sections get truncated in Remotion render.

**Cause**: Azure's `result.audio_duration` may exclude `<break>` time and under-report `<phoneme>` duration.

**Fix**: Already automated. `generate_tts.py` calls `reconcile_timing_with_wav` after concat, ffprobing the actual file and rescaling sections proportionally if drift > 0.5s.

### `<say-as interpret-as="characters">` nested in `<lang>` — undefined behaviour

**Symptom**: `<say-as>` appears to have no effect or produces unexpected output.

**Cause**: Under Multilingual voice, `mark_english_terms` runs in `aggressive` mode and wraps single English words in `<lang xml:lang="en-US">`. Pre-writing `<say-as>` around the same word produces `<say-as><lang>Word</lang></say-as>` — Azure picks one or the other unpredictably.

**Fix**: Avoid `<say-as>` for English tokens — let voice selection (above) handle it.

---

## How English-term wrapping works

English-term wrapping (`<lang xml:lang="en-US">` around brand phrases and, on Multilingual voices, longer English words) is performed by the ttsCN azure adapter, not by this skill. The behavior to expect:

| Voice | What gets wrapped |
|---|---|
| Standard `zh-CN-XiaoxiaoNeural` | Brand / proper-noun phrases only (Visual Studio Code, Andrew Ng, Apple Intelligence, …). Bare abbreviations (AI, ML, GPT, CLI, API) are left alone — standard voice reads them as natural Chinese letter pronunciations. |
| `zh-CN-XiaoxiaoMultilingualNeural` | Brand phrases + single English words that look like real words (≥5 chars, lowercase letters, not common abbreviations like JSON/HTTPS). Bare abbreviations still skipped. |
| Non-azure platforms | Nothing — they consume plain text; ttsCN strips or ignores SSML for them. |

To force a one-off proper-noun pronunciation in a single script, hand-write `<lang xml:lang="en-US">…</lang>` directly in `podcast.txt` (azure platform only), or prefer an inline `[pinyin]` marker / `phonemes.json` entry, which works through the phoneme path.

---

## Style support matrix

These styles are reliably supported on `zh-CN-XiaoxiaoNeural`:

| Style | Use for | Note |
|---|---|---|
| `gentle` (default) | General narration | Safe default |
| `cheerful` | Light/positive tone | Energetic |
| `serious` | News, professional | Punchy |
| `newscast` | Reporting style | Steady cadence |
| `calm` | Slow-paced explainer | Soothing |
| `chat` | Casual conversation | Natural pause |
| (empty `""`) | Disable wrapper | When any style produces artifacts |

For Multilingual voice, restrict to `gentle` or `""`. Other styles are inconsistent.

Set per-run via env: `TTS_STYLE=cheerful python3 generate_tts.py ...` or persist in `user_prefs.json` → `global.tts.style`.

---

## Quick triage checklist

Hearing weird audio at a specific timestamp?

1. **Locate the bad word in `podcast_audio.srt`** (timestamp ranges → words said when)
2. **Check the surrounding context** — Chinese tonal particle + bare English letter is the #1 hoarse trigger on Multilingual voice
3. **Run voice advisor** — if it suggests standard voice and you're on Multilingual, switch
4. **Inspect inline phoneme markers near the bad word** — remove if any
5. **Try `TTS_STYLE=""`** — disable express-as wrapper as a low-risk first try
6. **Last resort**: substitute that one Chinese homophone for the bare English token (e.g. `AI` → `诶艾`). Surgical, audible difference is zero for Chinese listeners.
