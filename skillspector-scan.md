# SkillSpector Security Report

**Skill:** video-podcast-maker  
**Source:** `/Users/niehu/myagents/myskills/video-podcast-maker/skills/video-podcast-maker`  
**Scanned:** 2026-07-17 13:08:32 UTC  

## Risk Assessment

| Metric | Value |
|--------|-------|
| Score | 100/100 |
| Severity | CRITICAL |
| Recommendation | DO NOT INSTALL |

## Components (102)

| File | Type | Lines | Executable |
|------|------|-------|------------|
| `AGENTS.md` | markdown | 38 | No |
| `LICENSE` | other | 28 | No |
| `SKILL.md` | markdown | 200 | No |
| `assets/bilibili-triple-black.mp4` | other | 37836 | No |
| `assets/bilibili-triple-white.mp4` | other | 38860 | No |
| `assets/perfect-beauty-191271.mp3` | other | 213139 | No |
| `assets/snow-stevekaldes-piano-397491.mp3` | other | 74941 | No |
| `package.json` | json | 33 | No |
| `phonemes.json` | json | 320 | No |
| `phonemes.template.json` | json | 320 | No |
| `prefs_schema.json` | json | 507 | No |
| `references/audio-sync.md` | markdown | 40 | No |
| `references/azure-tts-pitfalls.md` | markdown | 111 | No |
| `references/design-guide.md` | markdown | 397 | No |
| `references/design-learning.md` | markdown | 73 | No |
| `references/hyperframes-overlays.md` | markdown | 99 | No |
| `references/natural-narration.md` | markdown | 146 | No |
| `references/platform-matrix.md` | markdown | 67 | No |
| `references/project-layout.md` | markdown | 45 | No |
| `references/regeneration.md` | markdown | 24 | No |
| `references/script-polish.md` | markdown | 356 | No |
| `references/troubleshooting.md` | markdown | 360 | No |
| `references/visual-taste.md` | markdown | 124 | No |
| `references/workflow-assets.md` | markdown | 218 | No |
| `references/workflow-production.md` | markdown | 516 | No |
| `references/workflow-publish.md` | markdown | 229 | No |
| `references/workflow-script.md` | markdown | 333 | No |
| `references/zh-polyphones.md` | markdown | 50 | No |
| `requirements.txt` | text | 7 | No |
| `scripts/align_timing_from_srt.py` | python | 572 | Yes |
| `scripts/assets.py` | python | 362 | Yes |
| `scripts/audit_beat_sync.py` | python | 306 | Yes |
| `scripts/check_prereqs.py` | python | 169 | Yes |
| `scripts/cli.py` | python | 379 | Yes |
| `scripts/cli_envelope.py` | python | 127 | Yes |
| `scripts/components.py` | python | 186 | Yes |
| `scripts/generate_shorts.py` | python | 430 | Yes |
| `scripts/generate_tts.py` | python | 417 | Yes |
| `scripts/get_pref.py` | python | 67 | Yes |
| `scripts/learn_design.py` | python | 858 | Yes |
| `scripts/migrate_prefs.py` | python | 222 | Yes |
| `scripts/resolve_backend.py` | python | 9 | Yes |
| `scripts/resolve_bgm_path.py` | python | 40 | Yes |
| `scripts/tts/__init__.py` | python | 1 | Yes |
| `scripts/tts/backends/__init__.py` | python | 196 | Yes |
| `scripts/tts/backends/base.py` | python | 21 | Yes |
| `scripts/tts/backends/ttscn.py` | python | 166 | Yes |
| `scripts/tts/markers.py` | python | 38 | Yes |
| `scripts/tts/phonemes.py` | python | 99 | Yes |
| `scripts/tts/sections.py` | python | 173 | Yes |
| `scripts/tts/srt.py` | python | 190 | Yes |
| `scripts/tts/voice_advisor.py` | python | 115 | Yes |
| `scripts/verify_output.py` | python | 615 | Yes |
| `templates/README.md` | markdown | 88 | No |
| `templates/Root.tsx` | other | 199 | No |
| `templates/ShortVideo.tsx` | other | 140 | No |
| `templates/Thumbnail.tsx` | other | 105 | No |
| `templates/Video.tsx` | other | 377 | No |
| `templates/components/AnimatedBackground.tsx` | other | 242 | No |
| `templates/components/AssetImage.tsx` | other | 83 | No |
| `templates/components/AssetVideo.tsx` | other | 77 | No |
| `templates/components/AudioWaveform.tsx` | other | 126 | No |
| `templates/components/ChapterProgressBar.tsx` | other | 112 | No |
| `templates/components/CodeBlock.tsx` | other | 50 | No |
| `templates/components/ComparisonCard.tsx` | other | 71 | No |
| `templates/components/DataBar.tsx` | other | 54 | No |
| `templates/components/DataTable.tsx` | other | 79 | No |
| `templates/components/DiagramReveal.tsx` | other | 465 | No |
| `templates/components/ErrorBoundary.tsx` | other | 62 | No |
| `templates/components/FeatureGrid.tsx` | other | 58 | No |
| `templates/components/FlowChart.tsx` | other | 165 | No |
| `templates/components/Icon.tsx` | other | 80 | No |
| `templates/components/IconCard.tsx` | other | 56 | No |
| `templates/components/LottieAnimation.tsx` | other | 105 | No |
| `templates/components/MediaSection.tsx` | other | 117 | No |
| `templates/components/OverlayLayer.tsx` | other | 41 | No |
| `templates/components/QuoteBlock.tsx` | other | 57 | No |
| `templates/components/SectionLayouts.tsx` | other | 656 | No |
| `templates/components/ShortCTACard.tsx` | other | 48 | No |
| `templates/components/ShortIntroCard.tsx` | other | 60 | No |
| `templates/components/StatCounter.tsx` | other | 57 | No |
| `templates/components/Subtitles.tsx` | other | 189 | No |
| `templates/components/Timeline.tsx` | other | 130 | No |
| `templates/components/animations.tsx` | other | 246 | No |
| `templates/components/iconMap.ts` | typescript | 31 | Yes |
| `templates/components/index.ts` | typescript | 58 | Yes |
| `templates/components/layouts.tsx` | other | 60 | No |
| `templates/components/useAssets.ts` | typescript | 99 | Yes |
| `templates/components/useTiming.ts` | typescript | 86 | Yes |
| `templates/podcast.txt` | text | 64 | No |
| `templates/podcast_en.txt` | text | 63 | No |
| `templates/podcast_zh.txt` | text | 66 | No |
| `templates/presets/kinetic-typography/README.md` | markdown | 79 | No |
| `templates/presets/kinetic-typography/Thumbnail.tsx.template` | other | 78 | No |
| `templates/presets/kinetic-typography/Video.tsx.template` | other | 331 | No |
| `templates/presets/kinetic-typography/colors.json` | json | 54 | No |
| `templates/presets/kinetic-typography/motion.json` | json | 37 | No |
| `templates/presets/kinetic-typography/voice.json` | json | 21 | No |
| `templates/remotion.config.ts` | typescript | 4 | Yes |
| `tsconfig.json` | json | 15 | No |
| `tsconfig.templates.json` | json | 9 | No |
| `user_prefs.template.json` | json | 113 | No |

## Issues (77)

### 🟡 MEDIUM: AST4

**Location:** `scripts/align_timing_from_srt.py:38–42`  
**Confidence:** 70%  

**Message:** subprocess module call

**Remediation:** Use subprocess.run() with shell=False and an explicit argument list. Validate all inputs and avoid passing user-controlled data to commands.

---

### 🟢 LOW: AST7

**Location:** `scripts/assets.py:224`  
**Confidence:** 50%  

**Message:** Dynamic attribute access via getattr()

**Remediation:** Replace dynamic getattr() with explicit attribute access or a dictionary lookup with an allowlist of permitted attributes.

---

### 🟢 LOW: AST7

**Location:** `scripts/cli.py:282`  
**Confidence:** 50%  

**Message:** Dynamic attribute access via getattr()

**Remediation:** Replace dynamic getattr() with explicit attribute access or a dictionary lookup with an allowlist of permitted attributes.

---

### 🟡 MEDIUM: AST4

**Location:** `scripts/cli.py:231`  
**Confidence:** 70%  

**Message:** subprocess module call

**Remediation:** Use subprocess.run() with shell=False and an explicit argument list. Validate all inputs and avoid passing user-controlled data to commands.

---

### 🟡 MEDIUM: AST4

**Location:** `scripts/components.py:100`  
**Confidence:** 70%  

**Message:** subprocess module call

**Remediation:** Use subprocess.run() with shell=False and an explicit argument list. Validate all inputs and avoid passing user-controlled data to commands.

---

### 🟡 MEDIUM: AST4

**Location:** `scripts/generate_shorts.py:125`  
**Confidence:** 70%  

**Message:** subprocess module call

**Remediation:** Use subprocess.run() with shell=False and an explicit argument list. Validate all inputs and avoid passing user-controlled data to commands.

---

### 🟡 MEDIUM: AST4

**Location:** `scripts/generate_shorts.py:241`  
**Confidence:** 70%  

**Message:** subprocess module call

**Remediation:** Use subprocess.run() with shell=False and an explicit argument list. Validate all inputs and avoid passing user-controlled data to commands.

---

### 🟡 MEDIUM: AST4

**Location:** `scripts/generate_tts.py:370–374`  
**Confidence:** 70%  

**Message:** subprocess module call

**Remediation:** Use subprocess.run() with shell=False and an explicit argument list. Validate all inputs and avoid passing user-controlled data to commands.

---

### 🟡 MEDIUM: AST4

**Location:** `scripts/learn_design.py:170–180`  
**Confidence:** 70%  

**Message:** subprocess module call

**Remediation:** Use subprocess.run() with shell=False and an explicit argument list. Validate all inputs and avoid passing user-controlled data to commands.

---

### 🟡 MEDIUM: AST4

**Location:** `scripts/learn_design.py:189–200`  
**Confidence:** 70%  

**Message:** subprocess module call

**Remediation:** Use subprocess.run() with shell=False and an explicit argument list. Validate all inputs and avoid passing user-controlled data to commands.

---

### 🟡 MEDIUM: AST4

**Location:** `scripts/learn_design.py:247`  
**Confidence:** 70%  

**Message:** subprocess module call

**Remediation:** Use subprocess.run() with shell=False and an explicit argument list. Validate all inputs and avoid passing user-controlled data to commands.

---

### 🟡 MEDIUM: AST4

**Location:** `scripts/tts/backends/base.py:14–16`  
**Confidence:** 70%  

**Message:** subprocess module call

**Remediation:** Use subprocess.run() with shell=False and an explicit argument list. Validate all inputs and avoid passing user-controlled data to commands.

---

### 🟡 MEDIUM: AST4

**Location:** `scripts/tts/backends/ttscn.py:122`  
**Confidence:** 70%  

**Message:** subprocess module call

**Remediation:** Use subprocess.run() with shell=False and an explicit argument list. Validate all inputs and avoid passing user-controlled data to commands.

---

### 🟡 MEDIUM: AST4

**Location:** `scripts/tts/backends/ttscn.py:129–131`  
**Confidence:** 70%  

**Message:** subprocess module call

**Remediation:** Use subprocess.run() with shell=False and an explicit argument list. Validate all inputs and avoid passing user-controlled data to commands.

---

### 🟡 MEDIUM: AST4

**Location:** `scripts/tts/srt.py:142–145`  
**Confidence:** 70%  

**Message:** subprocess module call

**Remediation:** Use subprocess.run() with shell=False and an explicit argument list. Validate all inputs and avoid passing user-controlled data to commands.

---

### 🟡 MEDIUM: AST4

**Location:** `scripts/verify_output.py:102–105`  
**Confidence:** 70%  

**Message:** subprocess module call

**Remediation:** Use subprocess.run() with shell=False and an explicit argument list. Validate all inputs and avoid passing user-controlled data to commands.

---

### 🟡 MEDIUM: AST4

**Location:** `scripts/verify_output.py:132–135`  
**Confidence:** 70%  

**Message:** subprocess module call

**Remediation:** Use subprocess.run() with shell=False and an explicit argument list. Validate all inputs and avoid passing user-controlled data to commands.

---

### 🟡 MEDIUM: LP3

**Location:** `SKILL.md:1`  
**Confidence:** 70%  

**Message:** Skill has no declared permissions but code capabilities were detected: env, file_read, file_write, network, shell.

**Remediation:** Add a 'permissions' field to SKILL.md listing the capabilities this skill requires.

---

### 🟡 MEDIUM: RP1

**Location:** `SKILL.md:120`  
**Confidence:** 70%  

**Message:** MCP server referenced without pinned version: 'npx remotion'.

**Remediation:** Pin the version: npx @scope/server@1.2.3

---

### 🟡 MEDIUM: RP1

**Location:** `references/hyperframes-overlays.md:42`  
**Confidence:** 70%  

**Message:** MCP server referenced without pinned version: 'npx hyperframes'.

**Remediation:** Pin the version: npx @scope/server@1.2.3

---

### 🟡 MEDIUM: RP1

**Location:** `references/hyperframes-overlays.md:58`  
**Confidence:** 70%  

**Message:** MCP server referenced without pinned version: 'npx hyperframes'.

**Remediation:** Pin the version: npx @scope/server@1.2.3

---

### 🟡 MEDIUM: RP1

**Location:** `references/hyperframes-overlays.md:59`  
**Confidence:** 70%  

**Message:** MCP server referenced without pinned version: 'npx hyperframes'.

**Remediation:** Pin the version: npx @scope/server@1.2.3

---

### 🟡 MEDIUM: RP1

**Location:** `references/hyperframes-overlays.md:61`  
**Confidence:** 70%  

**Message:** MCP server referenced without pinned version: 'npx hyperframes'.

**Remediation:** Pin the version: npx @scope/server@1.2.3

---

### 🟡 MEDIUM: RP1

**Location:** `references/project-layout.md:31`  
**Confidence:** 70%  

**Message:** MCP server referenced without pinned version: 'npx remotion'.

**Remediation:** Pin the version: npx @scope/server@1.2.3

---

### 🟡 MEDIUM: RP1

**Location:** `references/project-layout.md:32`  
**Confidence:** 70%  

**Message:** MCP server referenced without pinned version: 'npx remotion'.

**Remediation:** Pin the version: npx @scope/server@1.2.3

---

### 🟡 MEDIUM: RP1

**Location:** `references/project-layout.md:33`  
**Confidence:** 70%  

**Message:** MCP server referenced without pinned version: 'npx remotion'.

**Remediation:** Pin the version: npx @scope/server@1.2.3

---

### 🟡 MEDIUM: RP1

**Location:** `references/troubleshooting.md:79`  
**Confidence:** 70%  

**Message:** MCP server referenced without pinned version: 'npx remotion'.

**Remediation:** Pin the version: npx @scope/server@1.2.3

---

### 🟡 MEDIUM: RP1

**Location:** `references/troubleshooting.md:82`  
**Confidence:** 70%  

**Message:** MCP server referenced without pinned version: 'npx remotion'.

**Remediation:** Pin the version: npx @scope/server@1.2.3

---

### 🟡 MEDIUM: RP1

**Location:** `references/troubleshooting.md:94`  
**Confidence:** 70%  

**Message:** MCP server referenced without pinned version: 'npx remotion'.

**Remediation:** Pin the version: npx @scope/server@1.2.3

---

### 🟡 MEDIUM: RP1

**Location:** `references/troubleshooting.md:96`  
**Confidence:** 70%  

**Message:** MCP server referenced without pinned version: 'npx remotion'.

**Remediation:** Pin the version: npx @scope/server@1.2.3

---

### 🟡 MEDIUM: RP1

**Location:** `references/troubleshooting.md:110`  
**Confidence:** 70%  

**Message:** MCP server referenced without pinned version: 'npx remotion'.

**Remediation:** Pin the version: npx @scope/server@1.2.3

---

### 🟡 MEDIUM: RP1

**Location:** `references/workflow-production.md:60`  
**Confidence:** 70%  

**Message:** MCP server referenced without pinned version: 'npx remotion'.

**Remediation:** Pin the version: npx @scope/server@1.2.3

---

### 🟡 MEDIUM: RP1

**Location:** `references/workflow-production.md:61`  
**Confidence:** 70%  

**Message:** MCP server referenced without pinned version: 'npx remotion'.

**Remediation:** Pin the version: npx @scope/server@1.2.3

---

### 🟡 MEDIUM: RP1

**Location:** `references/workflow-production.md:67`  
**Confidence:** 70%  

**Message:** MCP server referenced without pinned version: 'npx remotion'.

**Remediation:** Pin the version: npx @scope/server@1.2.3

---

### 🟡 MEDIUM: RP1

**Location:** `references/workflow-production.md:354`  
**Confidence:** 70%  

**Message:** MCP server referenced without pinned version: 'npx remotion'.

**Remediation:** Pin the version: npx @scope/server@1.2.3

---

### 🟡 MEDIUM: RP1

**Location:** `references/workflow-production.md:357`  
**Confidence:** 70%  

**Message:** MCP server referenced without pinned version: 'npx remotion'.

**Remediation:** Pin the version: npx @scope/server@1.2.3

---

### 🟡 MEDIUM: RP1

**Location:** `references/workflow-production.md:394`  
**Confidence:** 70%  

**Message:** MCP server referenced without pinned version: 'npx remotion'.

**Remediation:** Pin the version: npx @scope/server@1.2.3

---

### 🟡 MEDIUM: RP1

**Location:** `references/workflow-production.md:421`  
**Confidence:** 70%  

**Message:** MCP server referenced without pinned version: 'npx remotion'.

**Remediation:** Pin the version: npx @scope/server@1.2.3

---

### 🟡 MEDIUM: RP1

**Location:** `references/workflow-production.md:422`  
**Confidence:** 70%  

**Message:** MCP server referenced without pinned version: 'npx remotion'.

**Remediation:** Pin the version: npx @scope/server@1.2.3

---

### 🟡 MEDIUM: RP1

**Location:** `references/workflow-publish.md:216`  
**Confidence:** 70%  

**Message:** MCP server referenced without pinned version: 'npx remotion'.

**Remediation:** Pin the version: npx @scope/server@1.2.3

---

### 🟡 MEDIUM: RP1

**Location:** `scripts/components.py:108`  
**Confidence:** 70%  

**Message:** MCP server referenced without pinned version: 'npx tool'.

**Remediation:** Pin the version: npx @scope/server@1.2.3

---

### 🟡 MEDIUM: RP1

**Location:** `scripts/components.py:120`  
**Confidence:** 70%  

**Message:** MCP server referenced without pinned version: 'npx hyperframes'.

**Remediation:** Pin the version: npx @scope/server@1.2.3

---

### 🟡 MEDIUM: RP1

**Location:** `scripts/generate_shorts.py:231`  
**Confidence:** 70%  

**Message:** MCP server referenced without pinned version: 'npx remotion'.

**Remediation:** Pin the version: npx @scope/server@1.2.3

---

### 🟡 MEDIUM: RP1

**Location:** `scripts/generate_shorts.py:265`  
**Confidence:** 70%  

**Message:** MCP server referenced without pinned version: 'npx remotion'.

**Remediation:** Pin the version: npx @scope/server@1.2.3

---

### 🟡 MEDIUM: RP1

**Location:** `scripts/generate_shorts.py:422`  
**Confidence:** 70%  

**Message:** MCP server referenced without pinned version: 'npx remotion'.

**Remediation:** Pin the version: npx @scope/server@1.2.3

---

### 🔴 HIGH: E2

**Location:** `scripts/tts/backends/ttscn.py:77`  
**Confidence:** 60%  

**Message:** Env Variable Harvesting

**Remediation:** Avoid reading sensitive env vars (API keys, tokens) unless strictly required. Use secrets managers or secure config. Never log or transmit credentials.

---

### 🟡 MEDIUM: EA2

**Location:** `scripts/migrate_prefs.py:139`  
**Confidence:** 75%  

**Message:** Autonomous Decision Making

**Remediation:** Add human-in-the-loop confirmation for destructive, irreversible, or high-impact operations. Never auto-execute commands that modify files, send data, or alter system state.

---

### 🟡 MEDIUM: MP2

**Location:** `scripts/align_timing_from_srt.py:272`  
**Confidence:** 80%  

**Message:** Context Window Stuffing

**Remediation:** Implement context-window management that detects and rejects padding or stuffing attempts. Prioritize system instructions over user-injected content.

---

### 🔴 HIGH: OH1

**Location:** `scripts/generate_shorts.py:125`  
**Confidence:** 95%  

**Message:** Unvalidated Output Injection

**Remediation:** Validate and sanitize all model output before using it in downstream contexts. Use parameterized queries for SQL, shell quoting for commands, and HTML encoding for web output.

---

### 🔴 HIGH: OH1

**Location:** `scripts/generate_shorts.py:241`  
**Confidence:** 95%  

**Message:** Unvalidated Output Injection

**Remediation:** Validate and sanitize all model output before using it in downstream contexts. Use parameterized queries for SQL, shell quoting for commands, and HTML encoding for web output.

---

### 🔴 HIGH: OH1

**Location:** `scripts/learn_design.py:170`  
**Confidence:** 95%  

**Message:** Unvalidated Output Injection

**Remediation:** Validate and sanitize all model output before using it in downstream contexts. Use parameterized queries for SQL, shell quoting for commands, and HTML encoding for web output.

---

### 🔴 HIGH: OH1

**Location:** `scripts/learn_design.py:189`  
**Confidence:** 95%  

**Message:** Unvalidated Output Injection

**Remediation:** Validate and sanitize all model output before using it in downstream contexts. Use parameterized queries for SQL, shell quoting for commands, and HTML encoding for web output.

---

### 🔴 HIGH: OH1

**Location:** `scripts/learn_design.py:247`  
**Confidence:** 95%  

**Message:** Unvalidated Output Injection

**Remediation:** Validate and sanitize all model output before using it in downstream contexts. Use parameterized queries for SQL, shell quoting for commands, and HTML encoding for web output.

---

### 🔴 HIGH: OH1

**Location:** `scripts/tts/backends/base.py:14`  
**Confidence:** 95%  

**Message:** Unvalidated Output Injection

**Remediation:** Validate and sanitize all model output before using it in downstream contexts. Use parameterized queries for SQL, shell quoting for commands, and HTML encoding for web output.

---

### 🔴 HIGH: OH1

**Location:** `scripts/tts/backends/ttscn.py:122`  
**Confidence:** 95%  

**Message:** Unvalidated Output Injection

**Remediation:** Validate and sanitize all model output before using it in downstream contexts. Use parameterized queries for SQL, shell quoting for commands, and HTML encoding for web output.

---

### 🔴 HIGH: OH1

**Location:** `scripts/tts/backends/ttscn.py:129`  
**Confidence:** 95%  

**Message:** Unvalidated Output Injection

**Remediation:** Validate and sanitize all model output before using it in downstream contexts. Use parameterized queries for SQL, shell quoting for commands, and HTML encoding for web output.

---

### 🔴 HIGH: OH1

**Location:** `scripts/tts/srt.py:142`  
**Confidence:** 95%  

**Message:** Unvalidated Output Injection

**Remediation:** Validate and sanitize all model output before using it in downstream contexts. Use parameterized queries for SQL, shell quoting for commands, and HTML encoding for web output.

---

### 🔴 HIGH: PE3

**Location:** `references/troubleshooting.md:359`  
**Confidence:** 21%  

**Message:** Credential Access

**Remediation:** Remove references to credential paths. Use environment variables or secrets managers. For docs, use placeholder paths (e.g., /path/to/config). Never load .env or token files in production code paths.

---

### 🟢 LOW: SC1

**Location:** `package.json:14`  
**Confidence:** 40%  

**Message:** Unpinned Dependencies

**Remediation:** Pin all dependency versions in requirements.txt or pyproject.toml. Use exact versions (==) or compatible ranges. Run pip-audit regularly.

---

### 🟢 LOW: SC1

**Location:** `package.json:15`  
**Confidence:** 40%  

**Message:** Unpinned Dependencies

**Remediation:** Pin all dependency versions in requirements.txt or pyproject.toml. Use exact versions (==) or compatible ranges. Run pip-audit regularly.

---

### 🟢 LOW: SC1

**Location:** `package.json:16`  
**Confidence:** 40%  

**Message:** Unpinned Dependencies

**Remediation:** Pin all dependency versions in requirements.txt or pyproject.toml. Use exact versions (==) or compatible ranges. Run pip-audit regularly.

---

### 🟢 LOW: SC1

**Location:** `package.json:17`  
**Confidence:** 40%  

**Message:** Unpinned Dependencies

**Remediation:** Pin all dependency versions in requirements.txt or pyproject.toml. Use exact versions (==) or compatible ranges. Run pip-audit regularly.

---

### 🟢 LOW: SC1

**Location:** `package.json:18`  
**Confidence:** 40%  

**Message:** Unpinned Dependencies

**Remediation:** Pin all dependency versions in requirements.txt or pyproject.toml. Use exact versions (==) or compatible ranges. Run pip-audit regularly.

---

### 🟢 LOW: SC1

**Location:** `package.json:19`  
**Confidence:** 40%  

**Message:** Unpinned Dependencies

**Remediation:** Pin all dependency versions in requirements.txt or pyproject.toml. Use exact versions (==) or compatible ranges. Run pip-audit regularly.

---

### 🟢 LOW: SC1

**Location:** `package.json:20`  
**Confidence:** 40%  

**Message:** Unpinned Dependencies

**Remediation:** Pin all dependency versions in requirements.txt or pyproject.toml. Use exact versions (==) or compatible ranges. Run pip-audit regularly.

---

### 🟢 LOW: SC1

**Location:** `package.json:21`  
**Confidence:** 40%  

**Message:** Unpinned Dependencies

**Remediation:** Pin all dependency versions in requirements.txt or pyproject.toml. Use exact versions (==) or compatible ranges. Run pip-audit regularly.

---

### 🟢 LOW: SC1

**Location:** `package.json:22`  
**Confidence:** 40%  

**Message:** Unpinned Dependencies

**Remediation:** Pin all dependency versions in requirements.txt or pyproject.toml. Use exact versions (==) or compatible ranges. Run pip-audit regularly.

---

### 🟢 LOW: SC1

**Location:** `package.json:23`  
**Confidence:** 40%  

**Message:** Unpinned Dependencies

**Remediation:** Pin all dependency versions in requirements.txt or pyproject.toml. Use exact versions (==) or compatible ranges. Run pip-audit regularly.

---

### 🟢 LOW: SC1

**Location:** `package.json:24`  
**Confidence:** 40%  

**Message:** Unpinned Dependencies

**Remediation:** Pin all dependency versions in requirements.txt or pyproject.toml. Use exact versions (==) or compatible ranges. Run pip-audit regularly.

---

### 🟢 LOW: SC1

**Location:** `package.json:25`  
**Confidence:** 40%  

**Message:** Unpinned Dependencies

**Remediation:** Pin all dependency versions in requirements.txt or pyproject.toml. Use exact versions (==) or compatible ranges. Run pip-audit regularly.

---

### 🟢 LOW: SC1

**Location:** `package.json:26`  
**Confidence:** 40%  

**Message:** Unpinned Dependencies

**Remediation:** Pin all dependency versions in requirements.txt or pyproject.toml. Use exact versions (==) or compatible ranges. Run pip-audit regularly.

---

### 🟢 LOW: SC1

**Location:** `package.json:29`  
**Confidence:** 40%  

**Message:** Unpinned Dependencies

**Remediation:** Pin all dependency versions in requirements.txt or pyproject.toml. Use exact versions (==) or compatible ranges. Run pip-audit regularly.

---

### 🟢 LOW: SC1

**Location:** `package.json:30`  
**Confidence:** 40%  

**Message:** Unpinned Dependencies

**Remediation:** Pin all dependency versions in requirements.txt or pyproject.toml. Use exact versions (==) or compatible ranges. Run pip-audit regularly.

---

### 🟢 LOW: SC4

**Location:** `package.json:26`  
**Confidence:** 60%  

**Message:** Known Vulnerable Dependency: zod==3.22.0 — 1 advisory(ies): CVE-2023-4316 (Zod denial of service vulnerability)

**Remediation:** Update the dependency to a patched version that addresses the known CVE. Check OSV (osv.dev) or NVD for details on the vulnerability.

---

### 🔴 HIGH: TM1

**Location:** `references/workflow-assets.md:112`  
**Confidence:** 26%  

**Message:** Tool Parameter Abuse

**Remediation:** Validate all tool parameters against an allowlist. Reject dangerous parameter values (shell=True, --force, -rf /) and use safe defaults.

---

### 🔴 HIGH: TM1

**Location:** `references/workflow-production.md:72`  
**Confidence:** 26%  

**Message:** Tool Parameter Abuse

**Remediation:** Validate all tool parameters against an allowlist. Reject dangerous parameter values (shell=True, --force, -rf /) and use safe defaults.

---

### 🔴 HIGH: YR4

**Location:** `package.json:4`  
**Confidence:** 80%  

**Message:** YARA rule 'agent_skill_mcp_tool_poisoning_metadata': MCP/tool metadata poisoning indicators in tool schemas or skill manifests [agent_skills]

**Remediation:** Remove offensive tool references and exploit code. Legitimate agent skills should not contain penetration testing tools, exploit frameworks, or reconnaissance utilities.

---

## Metadata

- **Executable Scripts:** Yes

*Generated by SkillSpector v2.3.11*