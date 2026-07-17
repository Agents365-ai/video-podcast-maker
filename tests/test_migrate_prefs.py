"""Tests for scripts/migrate_prefs.py — version migration + --yes gating.

The script's contract is:
  - create from template when no file exists (safe, no --yes)
  - no-op when already current (safe, no --yes)
  - emit confirmation_required when an older file needs structural rewrite
    (must NOT mutate unless --yes is passed)

These tests exercise the pure `migrate()` function plus the dry-run preview
that drives the --yes gate.
"""
import json
import os
import sys
from pathlib import Path

import pytest

# scripts/ is on sys.path via tests/conftest.py
import migrate_prefs  # noqa: E402
from migrate_prefs import migrate, PREFS_VERSION  # noqa: E402


# --- create / noop -------------------------------------------------------

def test_creates_from_template_when_missing(tmp_path):
    prefs_path = tmp_path / "user_prefs.json"
    result = migrate(str(prefs_path), dry_run=False)
    assert result["action"] == "created"
    assert result["from"] is None
    assert result["to"] == PREFS_VERSION
    assert prefs_path.exists()
    with open(prefs_path) as f:
        prefs = json.load(f)
    assert prefs["version"] == PREFS_VERSION


def test_dry_run_does_not_create_file(tmp_path):
    prefs_path = tmp_path / "user_prefs.json"
    result = migrate(str(prefs_path), dry_run=True)
    assert result["action"] == "would_create"
    assert not prefs_path.exists()


def test_noop_when_already_current(tmp_path):
    prefs_path = tmp_path / "user_prefs.json"
    migrate(str(prefs_path), dry_run=False)  # create
    result = migrate(str(prefs_path), dry_run=False)
    assert result["action"] == "noop"
    assert result["from"] == PREFS_VERSION


# --- structural migration ------------------------------------------------

def test_v1_1_voice_string_migrates_to_voices_object(tmp_path):
    prefs_path = tmp_path / "user_prefs.json"
    prefs_path.write_text(json.dumps({
        "version": "1.1",
        "global": {"tts": {"voice": "zh-CN-YunyangNeural"}},
    }))
    # Dry-run first — the script's main() gate uses this to decide --yes
    preview = migrate(str(prefs_path), dry_run=True)
    assert preview["action"] == "would_migrate"
    assert preview["from"] == "1.1"
    assert preview["to"] == PREFS_VERSION
    assert any("voice" in c for c in preview["changes"])
    # File still untouched
    with open(prefs_path) as f:
        assert json.load(f)["version"] == "1.1"

    # Real run mutates
    result = migrate(str(prefs_path), dry_run=False)
    assert result["action"] == "migrated"
    with open(prefs_path) as f:
        migrated = json.load(f)
    assert migrated["version"] == PREFS_VERSION
    voices = migrated["global"]["tts"]["voices"]
    # The user's old voice should be preserved for azure + edge.
    assert voices["azure"] == "zh-CN-YunyangNeural"
    assert voices["edge"] == "zh-CN-YunyangNeural"


def test_v1_2_progress_bar_bool_migrates_to_object(tmp_path):
    prefs_path = tmp_path / "user_prefs.json"
    prefs_path.write_text(json.dumps({
        "version": "1.2",
        "global": {"visual": {"progressBar": False}},
    }))
    preview = migrate(str(prefs_path), dry_run=True)
    assert preview["action"] == "would_migrate"
    assert any("progressBar" in c for c in preview["changes"])

    result = migrate(str(prefs_path), dry_run=False)
    assert result["action"] == "migrated"
    with open(prefs_path) as f:
        migrated = json.load(f)
    assert isinstance(migrated["global"]["visual"]["progressBar"], dict)
    assert migrated["global"]["visual"]["progressBar"]["enabled"] is False
