#!/usr/bin/env bash
# Notify-only update check for video-podcast-maker.
#
# Throttled to once per 24h via .last_update_check. Compares the frontmatter
# `version` field in SKILL.md against the latest `v*` release tag on origin —
# release tags are the explicit "this is intended for users" signal, where
# every-commit comparison would fire on docs-only edits.
#
# Prints exactly one of:
#   MANUAL_INSTALL          (no .git directory — tarball/zip install; no auto-update path)
#   SKIPPED_RECENT_CHECK    (checked within the last 24h)
#   UP_TO_DATE              (current = latest, no tag yet, or local ahead of upstream)
#   UPDATE_AVAILABLE vX.Y.Z -> vA.B.C
#
# Never mutates the skill directory beyond touching .last_update_check.
# SKILL_DIR auto-resolves to the directory containing the parent of this script.

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAMP="${SKILL_DIR}/.last_update_check"
NOW=$(date +%s)
LAST=$(cat "$STAMP" 2>/dev/null || echo 0)

if [ ! -d "${SKILL_DIR}/.git" ]; then
  echo "MANUAL_INSTALL"
  exit 0
fi

if [ $((NOW - LAST)) -le 86400 ]; then
  echo "SKIPPED_RECENT_CHECK"
  exit 0
fi

echo "$NOW" > "$STAMP"
CURRENT=$(awk '/^version:/ {print $2; exit}' "${SKILL_DIR}/SKILL.md" | tr -d '"')

# `timeout` is GNU coreutils — not present on macOS by default (it ships
# `gtimeout` only when the user runs `brew install coreutils`). Without this
# fallback the bare `timeout` call fails with "command not found", 2>/dev/null
# swallows the error, and LATEST silently becomes empty → UP_TO_DATE for all
# Mac users regardless of how far behind they are.
fetch_latest() {
  if command -v timeout >/dev/null 2>&1; then
    timeout 5 git -C "${SKILL_DIR}" ls-remote --tags --refs origin 'v*' 2>/dev/null
  elif command -v gtimeout >/dev/null 2>&1; then
    gtimeout 5 git -C "${SKILL_DIR}" ls-remote --tags --refs origin 'v*' 2>/dev/null
  else
    git -C "${SKILL_DIR}" ls-remote --tags --refs origin 'v*' 2>/dev/null
  fi
}

# `--refs` excludes peeled annotated-tag entries (refs/tags/vX.Y.Z^{}) which
# would otherwise sort *after* the real tag and break the version comparison.
LATEST=$(fetch_latest | awk '{print $2}' | sed 's|refs/tags/||' | sort -V | tail -1 | sed 's/^v//')

if [ -z "$CURRENT" ] || [ -z "$LATEST" ] || [ "$CURRENT" = "$LATEST" ]; then
  echo "UP_TO_DATE"
elif [ "$(printf '%s\n%s\n' "$CURRENT" "$LATEST" | sort -V | tail -1)" = "$LATEST" ]; then
  echo "UPDATE_AVAILABLE v${CURRENT} -> v${LATEST}"
else
  echo "UP_TO_DATE"
fi
