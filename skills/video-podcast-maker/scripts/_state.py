"""Shared mutable state directory for video-podcast-maker.

user_prefs.json and phonemes.json are mutable per-user files that store
accumulated preferences and pronunciation corrections across projects.
Storing them in the skill install directory (SKILL_DIR) means every
plugin update or git-pull replaces the directory and wipes user data.

This module centralises state under ~/.video-podcast-maker/ with an
automatic migration path: on first access, if no state file exists in
the new location but one exists in SKILL_DIR, it is atomically copied.

Usage:
    from _state import get_state_dir, get_skill_dir

    state_dir = get_state_dir()          # ~/.video-podcast-maker/
    prefs = get_state_dir() / "user_prefs.json"
    phonemes = get_state_dir() / "phonemes.json"

State directory is created on first access. Templates are read-only and
stay in the skill install directory (SKILL_DIR/*.template.json).
"""

import os
import shutil
from pathlib import Path

_STATE_DIR_NAME = ".video-podcast-maker"

# SKILL_DIR: scripts/_state.py → scripts/ → SKILL_DIR (skill install root)
_SKILL_DIR = Path(__file__).resolve().parent.parent


def get_skill_dir() -> Path:
    """Return the skill install root (where SKILL.md lives)."""
    return _SKILL_DIR


def get_state_dir() -> Path:
    """Return ~/.video-podcast-maker/, creating it if needed."""
    state_dir = Path.home() / _STATE_DIR_NAME
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir


def _atomic_copy(src: Path, dst: Path) -> None:
    """Copy src to dst via a temp file so concurrent readers never see partial data."""
    tmp = dst.with_suffix(dst.suffix + ".tmp")
    shutil.copy2(src, tmp)
    os.replace(tmp, dst)


def resolve_state_file(filename: str, template_filename: str | None = None) -> Path:
    """Return the canonical path for a mutable state file.

    Resolution order:
      1. ~/.video-podcast-maker/{filename} — if it exists, return it
      2. SKILL_DIR/{filename} — if it exists, MIGRATE it atomically to
         ~/.video-podcast-maker/{filename} then return the new path
      3. If template_filename is provided and SKILL_DIR/{template} exists,
         copy it to ~/.video-podcast-maker/{filename} as a fresh start
      4. Return ~/.video-podcast-maker/{filename} (caller handles missing file)

    This is idempotent — once migrated, step 1 always hits.
    """
    state_dir = get_state_dir()
    state_path = state_dir / filename
    skill_path = _SKILL_DIR / filename

    if state_path.exists():
        return state_path

    # Migration: old location exists, move it to state dir
    if skill_path.exists():
        _atomic_copy(skill_path, state_path)
        # Keep the original for one version as a safety net;
        # it's gitignored so it won't be committed.
        return state_path

    # Fresh install: seed from template
    if template_filename:
        template_path = _SKILL_DIR / template_filename
        if template_path.exists():
            _atomic_copy(template_path, state_path)
            return state_path

    return state_path
