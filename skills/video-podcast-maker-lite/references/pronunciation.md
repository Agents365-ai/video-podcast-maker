# Pronunciation reference (zh-CN) — video-podcast-maker-lite

Loaded from SKILL.md Step 2. Everything here is about making Azure TTS say
Chinese tech content correctly. The spoken layer in `tts.py` does the mechanical
work; the author's job is to feed the dicts.

## Polyphone pre-flight (before TTS)

Scan the script for polyphone words — 命令行/一行 (háng), 同行 (háng), 重做/重新
(chóng), 增长 (zhǎng), 银行 (háng), etc. The global dict
`~/.video-podcast-maker/phonemes.json` already covers common tech terms — check
it first; add missing ones as **whole-word** entries (never single characters)
to `videos/{name}/phonemes.json`. `tts.py` turns them into SSML `<phoneme>`
tags automatically — don't wait for the preview listen to catch a misreading.

`tts.py` runs a polyphone pre-flight on every invocation; `--check` makes it
lint-only (no synthesis): it flags minority-reading shapes (计数+行 háng,
重做/重灌… chóng, 长会话/长上下文 cháng, …) that no phoneme-dict entry covers —
fix the dict before synthesizing, don't discover misreadings at the preview
listen.

## Known misreading shapes (auto-fixed by the spoken layer)

All of these are handled by `tts.py` automatically, except brand names — add
those to `aliases.json` yourself:

- Decimals that should read digit-by-digit after the point: `1.5` → 一点五,
  not English "one point five".
- Letter-by-letter acronyms: `MoE` → M-O-E, not "莫".
- Letter+digit combos: `FP8` → F-P-八.
- Model-name runs that TTS breaks wrongly: `9B Dense、35B MoE、397B MoE` —
  digits + 顿号 break cleanly; spelled-out `九B 稠密、三十五B MoE` mis-breaks
  into things like "9BMoe".

## Shapes that always need `aliases.json` entries

- Hyphenated model ids: `deepseek-v4-flash-vision-exp` → `DeepSeek V four
  Flash Vision E X P`.
- camelCase benchmark names: `DeepSWE` → `Deep S W E`.
- Code identifiers: `file_id` → `file I D`, `base64` → `base 六十四`.

Aliases may themselves contain hyphens — `pronounce()` matches them with
`startswith` at ASCII-letter positions, so a hyphenated alias still hits.

## Alias dict mechanics

Brand-name readings live in `aliases.json` (display → spoken, e.g.
`"Qwen": "千问"`):

- per-video entries: `videos/{name}/aliases.json`
- channel-wide: `~/.video-podcast-maker/aliases.json`
- merged over the built-ins in `tts.py` (`PRONUNCIATION_ALIASES` /
  `LETTER_WORD_ALIASES`)

## Built-in spoken-layer behaviors

- A spoken number followed by a single-Hanzi quantifier is glued into one unit
  (`10 倍` → 十倍, `57 分` → 五十七分) — otherwise Azure inserts a pause
  between the number word and the quantifier; extend `_CN_QUANTIFIERS` in
  `tts.py` if a new quantifier stumbles.
- `1M` is built in as 一兆 (so `1M token` reads "一兆", not letter M; other SI
  suffixes like `T` stay letter readings).

## Why not SSML `<sub alias>`

Tried and abandoned: Azure's word-boundary events for `<sub>` are buggy and
corrupt the SRT. The spoken layer + boundary mapping in `tts.py` is the
replacement.