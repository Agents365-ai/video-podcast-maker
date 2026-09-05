# Repository Guidelines

## Project Structure & Module Organization
This repository is a Codex/Claude skill plus supporting scripts and templates for Remotion-based video production. The runtime skill lives under `skills/video-podcast-maker/` (synced to the 365-skills marketplace on every push to `main`): core agent instructions in `skills/video-podcast-maker/SKILL.md`, workflow docs in `skills/video-podcast-maker/references/`, Python automation in `skills/video-podcast-maker/scripts/` (TTS backends under `scripts/tts/`), and reusable Remotion assets and starter files in `skills/video-podcast-maker/templates/` and `assets/`. A minimal personal-use variant lives under `skills/video-podcast-maker-lite/` (single Azure SSML TTS script + SKILL.md composition contract; no bundled templates — the agent generates the Remotion composition). `skills/video-podcast-maker-nano/` is a standalone, tool-agnostic logic-only pipeline (any TTS backend / video tool; autonomous by default, oversight and tool bindings set per project via its `AGENTS.template.md`). User-facing setup docs (`README.md`, `README_CN.md`) and tests (`tests/`, focused on the Python helpers) stay at the repo root.

## Build, Test, and Development Commands
Use Node 18+ and Python 3.8+.

Script commands below run from `skills/video-podcast-maker/`; `pytest -q` runs from the repo root.

- `yarn install` or `npm install`: install Remotion and React dependencies.
- `yarn studio` or `npx remotion studio src/remotion/index.ts`: launch local preview UI.
- `yarn build`: bundle the Remotion entrypoint.
- `python3 scripts/check_prereqs.py`: verify required CLIs and backend env vars.
- `pytest -q`: run Python tests.
- `python3 scripts/verify_output.py videos/<name>/`: validate rendered outputs before publish.

Run commands from the Remotion project root when testing template integration.

## Coding Style & Naming Conventions
Use 4-space indentation in Python and standard TypeScript/TSX formatting in templates. Prefer descriptive snake_case for Python files and variables, and PascalCase for React components such as `Video.tsx` or `Thumbnail.tsx`. Keep scripts single-purpose and CLI-friendly. When adding workflow docs, keep steps explicit and command examples copy-pastable.

## Testing Guidelines
Python tests use `pytest`; place new tests in `tests/` and name them `test_*.py`. Add focused unit coverage for parsing, backend resolution, subtitle timing, and output validation logic. For template or workflow changes, pair code changes with at least one reproducible command path in docs or tests.

## zh-CN Script & Pronunciation Conventions
Hard-won rules for narration scripts (`videos/{name}/podcast.txt`) and on-screen text — the full rationale lives in `skills/video-podcast-maker-lite/SKILL.md` ("Script style"):

- Numbers are always Arabic digits (`86.1`, `1.5G`, `1200 万`), in scripts AND in Remotion component text — never spelled-out Chinese numerals. TTS spoken forms are derived by `tts.py`'s pronunciation layer (`pronounce()` + `PRONUNCIATION_ALIASES`); never write the spoken form into the script to fix a misreading.
- Brand/term readings that can't be derived mechanically (e.g. `Qwen`→千问, `MoE`→M-O-E, `FP8`→F-P-八) go into `aliases.json` (per-video or `~/.video-podcast-maker/`), not into the script.
- Do not use SSML `<sub alias>` for pronunciation overrides: Azure's word-boundary events for `<sub>` span raw markup and corrupt subtitles (tried, abandoned).
- Model-name runs use digits + 顿号 (`9B Dense、35B MoE、397B MoE`) so TTS breaks cleanly.
- When changing the pronunciation layer in `tts.py`, extend `tests/test_lite_pronounce.py` and run `pytest -q`.

## Commit & Pull Request Guidelines
Recent history uses Conventional Commit style with optional scopes, for example `feat(cli): ...`, `fix(tts): ...`, and `docs: ...`. Follow that pattern. PRs should include a short summary, affected workflow stage(s), test evidence (`pytest -q`, preview, or render validation), and screenshots when UI or thumbnail output changes.

## Security & Configuration Tips
Do not commit real API keys or generated customer media. Keep secrets in shell env vars such as `OPENAI_API_KEY` or `AZURE_SPEECH_KEY`. Treat `user_prefs.json` and files under `videos/` as local state unless a change is intentionally part of the skill.
