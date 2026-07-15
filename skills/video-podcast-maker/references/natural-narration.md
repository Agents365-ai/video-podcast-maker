# Natural Narration — Anti-Slop Rules for Spoken Scripts

> **When to load:** During Step 4 (write narration script), and whenever you edit `podcast.txt`. Load before writing the first section.
>
> **Why:** A narration script is heard, not read. AI-generated prose has predictable "tells" that survive into narration and make it sound like a machine reading a press release. This guide removes those tells. It is distilled for **spoken narration** from two anti-slop guides — `op7418/Humanizer-zh` (24 Chinese AI-writing patterns, from Wikipedia's "Signs of AI writing") and `hardikpandya/stop-slop` — keeping only what transfers to the ear and dropping written-only rules (bold, emoji, curly quotes, inline headers, markdown, title case).
>
> This operationalizes the standing preferences "natural narration", "no metaphors", "no clickbait/rhetorical hooks", and "no middle-dot separators". If `user_prefs` conflicts, user_prefs wins.

---

## The 5 core rules (write for the ear)

1. **Cut the throat-clearing.** Delete opener filler and emphasis crutches. State the thing.
2. **Break formulaic structure.** No forced rule-of-three, no negative parallelism ("不是……而是……" / "not X, it's Y"), no rhetorical teaser setups, no binary drama.
3. **Vary rhythm.** Mix sentence lengths — short punch, then a longer one that unfolds. Same-length sentences in a row sound robotic when spoken. Two items beat three.
4. **Trust the listener.** State facts directly. Skip softening, over-qualifying, hand-holding, and explaining your own metaphor.
5. **Cut the quotable.** If a line sounds like a pull-quote or slogan, rewrite it plain.

---

## Kill list — words & phrases (spoken)

### zh-CN — AI vocabulary to avoid (rewrite or delete)
赋能、打造、深入探讨、值得一提的是、值得注意的是、不难发现、众所周知、总的来说、
综上所述、此外、然而（作连接拐杖时）、与此同时、在……的加持下、在……的浪潮下、
不断演变的格局、焦点、里程碑、标志着、见证了、是……的体现/证明/缩影、
至关重要、举足轻重、革命性、颠覆、震撼、令人叹为观止、必看、天花板、
无缝、丝滑（比喻义）、生态、闭环、抓手、拉满、遥遥领先、
从而彰显了……、进一步凸显了……、为……注入了新的活力。

### en-US — AI vocabulary to avoid
moreover, furthermore, it's worth noting, it's important to note, in today's
landscape, ever-evolving, delve into, leverage, seamless, robust, cutting-edge,
game-changer, revolutionize, unlock, empower, testament to, stands as, plays a
crucial/pivotal role, at the heart of, in the realm of, when it comes to.

### Filler → plain (both languages)
- "为了实现这一目标" → "为了这一点" / drop it
- "在这个时间点上" → "现在"
- "值得注意的是，数据显示" → "数据显示"
- "可以说是……的存在" → name the thing
- "in order to achieve this" → "to do this"
- "at this point in time" → "now"

---

## Structural tells to break

| Tell | Sounds like | Fix |
|------|-------------|-----|
| **Rule of three** | "更快、更强、更智能" every beat | Use two items, or four, or one specific one |
| **Negative parallelism** | "这不仅是X，更是Y" / "不是……而是……" | State Y directly |
| **Rhetorical teaser** | "但事情没那么简单" / "接下来才是重点" / "你绝对想不到" | Just say the next thing |
| **Vague attribution** | "业内普遍认为" / "有专家指出" / "据说" | Name the source + date, or drop the claim |
| **-ing / 从而 tail** | "……，从而彰显了其重要性" | End the sentence at the fact |
| **Fake range** | "从入门到精通，从原理到实战" | Say what it actually covers |
| **Generic uplift ending** | "未来可期" / "值得期待" / "让我们拭目以待" | End on a concrete fact or a plain question |
| **Synonym cycling** | 主角→主人公→中心人物 in one breath | Repeat the plain word; it's fine spoken |
| **Over-qualifying** | "可能大概或许在某种程度上" | Pick one hedge or none |

---

## Soul, calibrated for narration

Clean-but-soulless narration is still a tell: every sentence the same length, no
point of view, pure neutral reportage that reads like a press release. A little
humanity helps — but keep it **calm and factual**, not edgy or performative
(that would violate "no clickbait / no rhetorical hooks").

- **A light first person is honest, not unprofessional.** "我实测下来" / "我更在意的是" grounds a claim in a real person. Use sparingly.
- **Acknowledge complexity.** "这点很好用，但也有代价" beats a flat superlative.
- **Be concrete about the thing, not about feelings.** Prefer "同一个任务，42 美元降到 6 美元" over "省了非常多钱".
- Do **not** manufacture drama, suspense, or outrage to hold attention. Temporal and logical transitions only ("先看……，再看……，问题在于……").

---

## Spoken-only notes

- Write for the ear: a listener can't re-scan a sentence. Front-load the subject, keep one idea per sentence, avoid deep clause nesting.
- Numbers stay as digits per the Step 4 number-formatting table — this guide doesn't change that.
- No em-dash (—) or middle-dot (·) as connective punctuation; they don't get spoken and clutter the subtitle. Use a comma or a new sentence.
- Read every section aloud (or sub-vocalize) before moving on. If you stumble, the sentence is too long or too nested — split it.

---

## Expressiveness markers (backend-neutral)

`podcast.txt` may use two marker types; the pipeline renders or strips them per backend, and subtitles are always marker-free.

- **`[PAUSE:x]`** — pause of `x` seconds (0.01–99.99), e.g. `说完了。[PAUSE:0.8]然后呢?`
  Rendered as SSML `<break/>` on Azure, `<#x#>` on ttsCN/minimax, stripped elsewhere.
- **Sound tags** — `(laughs)` `(chuckle)` `(sighs)` `(breath)` `(inhale)` `(exhale)` `(coughs)`.
  Only spoken on ttsCN/minimax with a speech-2.8 model (`MINIMAX_MODEL=speech-2.8-hd`); stripped on every other backend. Other parenthesized text is left alone.

Usage rules:

- Use `[PAUSE:x]` for dramatic beats only (before a reveal, after a question). Normal pacing comes from punctuation — a script peppered with pauses reads as slow, not dramatic.
- Don't put markers inside a sentence's clause flow; place them at sentence boundaries.
- Polyphone fixes need no markers: `phonemes.json` entries apply automatically (SSML on Azure, pinyin annotation `字(zi4)` on ttsCN/minimax).

---

## Pre-delivery checklist (run on every `podcast.txt`)

- [ ] Any opener filler ("接下来我们来看看" / "总的来说" / "here's what")? Cut to the point.
- [ ] Any word from the kill list? Rewrite or delete.
- [ ] Any rule-of-three or "不是X而是Y"? Break it.
- [ ] Any rhetorical teaser / clickbait hook? Replace with the plain next fact.
- [ ] Any vague attribution ("业内认为")? Name the source or drop it.
- [ ] Three sentences in a row the same length? Break one.
- [ ] Any section ending on a generic uplift ("未来可期")? End on a fact.
- [ ] Any metaphor that needs explaining? Say it literally.
- [ ] Any em-dash or middle-dot as a separator? Remove it.
- [ ] Read aloud — does any sentence make you stumble? Split it.

---

## Quality scoring (optional, 1-10 each, /50)

| Dimension | Question |
|-----------|----------|
| Directness | States facts, or announces them with fanfare? |
| Rhythm | Sentence lengths varied, or metronomic? |
| Trust | Respects the listener, or over-explains? |
| Authenticity | Sounds like a person talking, or a machine reading? |
| Density | Anything left to cut? |

Below 35/50 → revise before TTS.

---

## Source & credit

Distilled and adapted for spoken narration from:
- `op7418/Humanizer-zh` (翻译自 blader/humanizer；based on
  [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)).
- `hardikpandya/stop-slop`.

Both target written prose; this file keeps only the patterns that survive into
spoken narration and drops the written-only ones.
