# Design Learning

Extract visual design patterns from reference videos or images, store them in a searchable library, and apply them to new video compositions.

> **When to load:** Only when the user runs `/design-learn`, provides a reference video/image, or asks to save/list/delete style profiles. Skip for normal video creation flow.

---

## Commands

```bash
# Learn from images (use your agent's image analysis capability to analyze design patterns)
python3 scripts/learn_design.py ./screenshot1.png ./screenshot2.png

# Learn from a local video (ffmpeg extracts frames automatically)
python3 scripts/learn_design.py ./reference.mp4

# Learn from a URL (NOT implemented — creates a placeholder ref_id only;
# add screenshots manually to <output-dir>/<ref_id>/frames/ afterwards)
python3 scripts/learn_design.py https://www.bilibili.com/video/BV1xx411c7mD

# Save with a named profile and tags (--tags is persisted in design_references
# index, --profile attaches the new ref_ids to the named style profile,
# auto-creating the profile if it doesn't exist yet)
python3 scripts/learn_design.py ./reference.mp4 --profile "tech-minimal" --tags "tech,minimal,dark"
```

## Reference Library Commands

All reference-library management goes through `learn_design.py`. The library
lives at `${SKILL_DIR}/design_references/` (next to `user_prefs.json`) so it is
shared across projects and independent of the invoking directory; pass
`--output-dir` only to override. If you have an old project-local
`design_references/` directory, move its contents into the skill-root one.

```bash
python3 scripts/learn_design.py --list                  # List all stored references (auto-cleans orphaned entries)
python3 scripts/learn_design.py --show <REF_ID>         # Show report.json for a specific reference

# --delete is gated: without --yes it prints a preview and exits 3 (confirmation_required).
# Re-run with --yes after reviewing the preview to actually remove the entry and its files.
python3 scripts/learn_design.py --delete <REF_ID>           # Preview only (no deletion)
python3 scripts/learn_design.py --delete <REF_ID> --yes     # Confirm and delete
```

`<REF_ID>` is the id printed by `--list` (e.g. `bilibili-BV1xx411c7mD`, or an md5-derived id for image sets).

## Style Profile Management

Style profiles live under `user_prefs.json` → `style_profiles`. There is no dedicated CLI — manage them by editing the JSON directly, or ask the agent to do it for you in conversation:

- "list my style profiles" → agent reads and prints `user_prefs.style_profiles`
- "show profile tech-minimal" → agent prints that entry
- "delete profile tech-minimal" → agent removes that key and saves
- "create profile tech-minimal from this video" → agent extracts current visual props into a new profile entry

To attach references to a profile when learning, pass `--profile <name>` and `--tags <csv>` to `learn_design.py`.

---

## Pre-Workflow Usage

When the user provides a reference video or image alongside a video creation request, extract design patterns **before Step 1** and apply them as session overrides.

See `references/workflow-script.md` → Pre-workflow section for the full extraction flow.

## Step 9 Integration

Before choosing visual design in Step 9, check for matching style profiles or reference library entries. Apply the best match as a starting point for Remotion composition props.

See `references/workflow-production.md` → Step 9 Style Profile Integration for the priority chain.

---

## Troubleshooting

Common issues (ffmpeg not found, Playwright fails, orphaned references, style profile not applied) are covered in **`references/troubleshooting.md`** → "Design Learning Troubleshooting" section.
