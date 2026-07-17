# Repository Guidelines

## Project Structure & Module Organization
This repository is a Codex/Claude skill plus supporting scripts and templates for Remotion-based video production. The runtime skill lives under `skills/video-podcast-maker/` (synced to the 365-skills marketplace on every push to `main`): core agent instructions in `skills/video-podcast-maker/SKILL.md`, workflow docs in `skills/video-podcast-maker/references/`, Python automation in `skills/video-podcast-maker/scripts/` (TTS backends under `scripts/tts/`), and reusable Remotion assets and starter files in `skills/video-podcast-maker/templates/` and `assets/`. User-facing setup docs (`README.md`, `README_CN.md`) and tests (`tests/`, focused on the Python helpers) stay at the repo root.

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

## Commit & Pull Request Guidelines
Recent history uses Conventional Commit style with optional scopes, for example `feat(cli): ...`, `fix(tts): ...`, and `docs: ...`. Follow that pattern. PRs should include a short summary, affected workflow stage(s), test evidence (`pytest -q`, preview, or render validation), and screenshots when UI or thumbnail output changes.

## Security & Configuration Tips
Do not commit real API keys or generated customer media. Keep secrets in shell env vars such as `OPENAI_API_KEY` or `AZURE_SPEECH_KEY`. Treat `user_prefs.json` and files under `videos/` as local state unless a change is intentionally part of the skill.
