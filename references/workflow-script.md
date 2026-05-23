# Video Podcast Maker — Workflow Phase 1: Scripting

> **When to load:** Load at workflow start, or when the user asks about research, topic definition, or narration script writing.
>
> **Covers:** Pre-workflow (optional design reference extraction) → Startup (load user preferences) → Steps 1-4 (topic → research → sections → script).
>
> **Next phase:** See `workflow-production.md` for Steps 5-11 (media, TTS, Remotion, render, BGM).

---

## Pre-workflow: Design Reference (Optional)

When the user provides a reference video/image with their video creation request:

1. Run extraction: `python3 scripts/learn_design.py <input>`
2. Read extracted frames using your agent's image/file inspection capability
3. Analyze against design-guide.md component vocabulary
4. Present design analysis report to user
5. User confirms/adjusts extracted attributes
6. Apply as session overrides for this video (do NOT save to library unless user asks)

---

## Startup: Load User Preferences

**Agent behavior:** Run the migrator before Step 1. It creates `user_prefs.json` from the template if absent, deep-merges any new template fields into existing prefs, and applies structural rewrites for old versions. Idempotent (no-op when already current).

```bash
SKILL_DIR="${SKILL_DIR:-${CLAUDE_SKILL_DIR}}"
python3 "${SKILL_DIR}/scripts/migrate_prefs.py"
```

**Three paths the migrator can take** — only the third needs user consent:

1. **No prefs file** → creates `user_prefs.json` from the template (safe, no existing data to rewrite). Runs without `--yes`.
2. **Already current version** → no-op. Runs without `--yes`.
3. **Existing prefs at older version** → exits with `confirmation_required` (exit 3) because a v1.x → current rewrite would mutate the file in place.

**For path 3, do NOT silently retry with `--yes`.** Instead:

```bash
# Preview the planned changes (always safe, no writes)
python3 "${SKILL_DIR}/scripts/migrate_prefs.py" --dry-run

# Show the user the per-change list, then ask "Apply migration? [y/N]"
# Only after explicit user confirmation:
python3 "${SKILL_DIR}/scripts/migrate_prefs.py" --yes
```

Then read `${SKILL_DIR}/user_prefs.json` and apply settings in subsequent steps.

The script prints one of: `already at v1.6 — no migration needed`, `Created user_prefs.json at v1.6 from template`, or `Migrated from v{old} to v1.6` with a per-change list. To inspect what each version added, see the inline `_structural_migrate` table in `scripts/migrate_prefs.py`.

At Step 1 start, inform the user of active preferences (if customized):

```
"Based on your preferences:
 - Platform: [platform] | Language: [language]
 - TTS: [tts.backend] / [tts.voices[backend]]
 - Speech rate: [tts.rate]
 - BGM: [bgm.track] at volume [bgm.volume]
 - Subtitles: [enabled/disabled] | CTA: [cta.type]

Say 'set platform youtube' or 'set language en-US' to change.
Say 'show preferences' to see all details."
```

---

## Step 1: Define Topic Direction

**Auto mode:** Infer all decisions from the user's topic description. Use sensible defaults (audience: general, style: educational intro, tone: professional-casual, duration: medium 3-7min). Save directly to `videos/{name}/topic_definition.md`.

**Interactive mode:** Confirm each item (use `brainstorming` skill if available, otherwise ask directly):
1. **Target audience**: developers / general / students / professionals
2. **Video style**: educational intro / deep analysis / news brief / hands-on tutorial
3. **Content scope**: background / technical principles / usage / comparison
4. **Tone**: serious / casual / fast-paced
5. **Duration**: short (1-3min) / medium (3-7min) / long (7-15min)

Save to `videos/{name}/topic_definition.md`

---

## Step 2: Research Topic

Use your agent's web search and fetch capabilities. Save to `videos/{name}/topic_research.md`.

---

## Step 3: Design Video Sections

Design 5-7 sections:
- Hero/Intro (15-25s)
- Core concepts (30-45s each)
- Demo/Examples (30-60s)
- Comparison/Analysis (30-45s)
- Summary (20-30s)

### Content Density Selection

Assign each section a density tier:

| Tier | Items | Best For |
|------|-------|----------|
| **Impact** | 1 | Hook, hero, CTA, brand moment — largest text |
| **Standard** | 2-3 | Features, comparison, demo |
| **Compact** | 4-6 | Feature grid, ecosystem |
| **Dense** | 6+ | Data tables, detailed comparisons — smallest text |

### Topic Type Detection

> **Planned feature.** Currently, topic-specific styles are applied manually via `user_prefs.json` under `topic_patterns`. Auto-detection from keywords is not yet implemented.

### Title Position

**Auto mode:** Use `top-center` (default).
**Interactive mode:** Ask user: top-center (recommended) / top-left / full-center.

**Rule:** Keep title position consistent within a single video.

---

## Step 4: Write Narration Script

**Preference application:** Adjust script style from `user_prefs.content`:
- `tone: professional` → formal language
- `tone: casual` → conversational, interjections ok
- `verbosity: concise` → 50-80 chars per paragraph
- `verbosity: detailed` → 100-150 chars per paragraph
- `heroOpening` (if set) → use as fixed hero opening line
- `outroClosing` (if set) → use as fixed outro closing line

Create `videos/{name}/podcast.txt` with section markers:

```text
[SECTION:hero]
{heroOpening}（话题引入）...

[SECTION:features]
它有以下功能...

[SECTION:demo]
让我演示一下...

[SECTION:summary]
总结一下，xxx是目前最xxx的xxx。

[SECTION:references]
本期视频参考了官方文档和技术博客。

[SECTION:outro]
{outroClosing}
```

**Number formatting for TTS**

Write numbers the way you'd naturally type them in a chat message — `2025年`, `18个月`, `90%`, `128GB`. Modern TTS (Azure, Edge, Doubao, CosyVoice) reads digit+unit combinations correctly on its own; pre-converting to Chinese characters like `二零二五年` or `十八个月` just makes the script awkward to read and edit. Only spell out in Chinese for the few forms TTS engines genuinely get wrong (see the second table).

**✅ Keep as digits** (TTS reads naturally — do NOT convert to Chinese):

| Type | Example | Read as |
|------|---------|---------|
| Year | `2025年`, `1998年` | 二零二五年 / 一九九八年 |
| Date | `2025年1月15日`, `1月15日` | 二零二五年一月十五日 / 一月十五日 |
| Duration with unit | `18个月`, `3年`, `45天`, `2小时` | 十八个月 / 三年 / 四十五天 / 两小时 |
| Integer with Chinese unit | `2900万`, `5亿`, `300块` | 二千九百万 / 五亿 / 三百块 |
| Simple percentage | `15%`, `90%`, `-10%` | 百分之十五 / 百分之九十 / 负百分之十 |
| Simple decimal | `1.2`, `3.5` | 一点二 / 三点五 |
| English unit (tech) | `128GB`, `16核`, `4K` | 一百二十八G / 十六核 / 四K |
| Small integer (<100) | `29`, `50` | 二十九 / 五十 |

**⚠ Must spell out in Chinese** (TTS reads ambiguously or wrong):

| Type | Wrong | Correct |
|------|-------|---------|
| ISO date with dashes | `2025-01-15` | 2025年1月15日 (or 二零二五年一月十五日) |
| Multi-dot version | `v1.2.3` | v一点二点三 |
| Phone / ID string | `400-123-4567` | 四零零 一二三 四五六七 |
| Long bare integer (no unit) | `3999999` | 三百九十九万九千九百九十九 (or rewrite with `万`) |

**Rule of thumb:** prefer digits. Years, dates with `年/月/日`, and any number followed by a Chinese unit (`年`/`月`/`日`/`个月`/`天`/`小时`/`万`/`亿`/`%`/`GB`/`块`…) should stay as digits — Azure/Edge/Doubao all read them correctly. Only spell out in Chinese when the form is genuinely ambiguous (dash-separated dates, dotted version numbers, phone/ID digit-by-digit, or unitless 7+ digit integers).

**Section notes**:
- **hero**: MUST start with `content.heroOpening` if set in user_prefs, followed by the topic hook
- **summary**: Pure content summary, no interaction prompts
- **references** (optional): One sentence about sources
- **outro**: MUST use `content.outroClosing` if set in user_prefs. Fallback: platform-specific CTA
- Empty `[SECTION:xxx]` = silent section

### Script Template Selection

Copy the script template based on `language`:
- `zh-CN` → `${SKILL_DIR}/templates/podcast_zh.txt`
- `en-US` → `${SKILL_DIR}/templates/podcast_en.txt`

### Outro Text by Platform + Language

| Platform | zh-CN | en-US |
|----------|-------|-------|
| bilibili | "一键三连！评论区留言，下期再见！" | "Like, coin, and favorite! Leave a comment, see you next time!" |
| youtube | "点赞订阅转发！评论区留言，下期再见！" | "Like, subscribe, and share! Leave a comment, see you next time!" |
| xiaohongshu | "点赞收藏加关注，评论区见！" | "Like, save & follow! See you in comments!" |
| douyin | "点赞关注，评论区见！" | "Like & follow! See you in comments!" |
| weixin-channels | "点赞关注，转发给朋友！" | "Like, follow & share with friends!" |

### Duration Estimation (Dry Run)

After writing `podcast.txt`, automatically run:

```bash
python3 ${SKILL_DIR}/scripts/generate_tts.py --input videos/{name}/podcast.txt --output-dir videos/{name} --dry-run
```

Report estimated duration. If >12min or <3min, suggest adjustments.

---

## Step 4.5: Pronunciation Pre-Flight (zh-CN only)

**Skip if `user_prefs.global.language != "zh-CN"`.**

**Why an LLM step, not code:** Polyphone disambiguation needs sentence-level context (`一行` → `háng` for "a line", `xíng` for "execute"). A regex or static dict can't substitute for reading the script. The `phonemes.json` system is the output channel; *choosing* entries is the LLM's job.

### Inputs
1. `videos/{name}/podcast.txt` — the script just written
2. `${SKILL_DIR}/phonemes.json` — global dict (already-covered words; do NOT duplicate). Auto-created from `${SKILL_DIR}/phonemes.template.json` on the first run of `scripts/generate_tts.py`, so it always exists by the time TTS executes. To pre-create before the first TTS call: `cp "${SKILL_DIR}/phonemes.template.json" "${SKILL_DIR}/phonemes.json"`.
3. `videos/{name}/phonemes.json` — project dict (create if missing; takes precedence over global)

### Pass 1 — Polyphone scan

Read podcast.txt sentence by sentence. For every Chinese polyphone risk, pick the pronunciation from context.

**Reference table:** the common-polyphone checklist and pinyin format rules live in **[references/zh-polyphones.md](zh-polyphones.md)** — load that file now if this is your first pre-flight pass, then return here for Pass 2.

### Pass 2 — English term review

`mark_english_terms` (in `scripts/tts/ssml.py`) auto-wraps ASCII runs in `<lang xml:lang="en-US">`, but has known gaps:
- **Hyphenated names**: `tldraw-cli` → only `cli` may get wrapped; `tldraw` reads through the voice's default Chinese pronunciation of letters.
- **Initialisms**: `API`, `URL`, `MCP` are wrapped as words. If you intend letter-by-letter reading, add an **inline marker** in podcast.txt: `配置 API[ei pi ai] 后...`
- **Versioned names**: `GPT-4`, `Claude 4.6` — verify the digit reads as digit and the dash reads as space.

For each risky term, prefer editing `podcast.txt`:
- Inline marker form: `tldraw-cli[tldraw c l i]` or rewrite as `tldraw 命令行工具`
- Multi-word phrases already covered by allowlist: `Claude Code`, `Final Cut Pro`, `Visual Studio Code`, `VS Code`, `Google Chrome`, `Open AI`, `OpenAI`, `GPT 4`, `GPT-4`

### Pass 3 — English brand names with Chinese pronunciation

Some products are spelled in English in scripts/code/papers but have an established Chinese pronunciation that listeners expect. The phoneme system handles this cleanly: SSML `<phoneme>` tag overrides voice pronunciation while leaving the **subtitle text unchanged** (still shows "Qwen", audio says "千问").

Add to `videos/{name}/phonemes.json` (or global if it's a stable choice):

```json
{
  "Qwen": "qiān wèn",
  "Bilibili": "bì lì bì lì"
}
```

**Decision rule:**
- Has a widely-recognized Chinese name **and** the script says it in a Chinese-language sentence → add phoneme entry to read it in Chinese.
- Is a code identifier, paper title term, or quoted English brand → leave it as English (don't add).
- Examples to **leave alone**: `Claude`, `Gemini`, `Llama`, `Mistral`, `OpenAI`, `Anthropic`, `GitHub`, `Docker`, `Python` — these are read in English in Chinese tech speech.

Use judgment per script. Don't over-translate.

### Output

1. Updated `videos/{name}/phonemes.json` — pretty-printed JSON, longest-key entries first.
2. (Optional) Edits to `videos/{name}/podcast.txt` for inline English markers or rewrites.
3. **Console summary**: `Pronunciation pre-flight: N polyphone entries added, M English terms flagged.` If both 0: `No issues found.`

### Re-run behavior

Always re-scan when this step runs. Existing project-level entries that are still correct should be preserved; new findings get appended. Stale entries (word no longer in podcast.txt) can be left as-is — unused entries cost nothing.
