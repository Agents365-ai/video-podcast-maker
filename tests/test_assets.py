"""Tests for assets.py — the per-video asset manifest manager."""
import json
import subprocess
import sys
from pathlib import Path

from assets import (
    SCHEMA_VERSION,
    load_manifest,
    manifest_path,
    save_manifest,
    validate_manifest,
)

SCRIPTS = Path(__file__).resolve().parent.parent / "skills" / "video-podcast-maker" / "scripts"


def run_cli(*argv):
    """Run assets.py as a subprocess with --format json. Returns (exit, envelope)."""
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "assets.py"), *argv, "--format", "json"],
        capture_output=True, text=True,
    )
    envelope = json.loads(proc.stdout) if proc.stdout.strip() else None
    return proc.returncode, envelope


# ---- validate_manifest (importable API used by verify_output.py) ------------

def test_missing_manifest_is_valid(tmp_path):
    errors, warnings, manifest = validate_manifest(tmp_path)
    assert errors == [] and warnings == [] and manifest is None


def test_valid_manifest_round_trip(tmp_path):
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "a.png").write_bytes(b"x")
    save_manifest(tmp_path, {"schema_version": SCHEMA_VERSION, "assets": [{
        "id": "a", "section": "hero", "type": "image", "role": "background",
        "source": "user", "status": "resolved", "path": "assets/a.png",
        "license": "user-owned",
    }]})
    errors, warnings, manifest = validate_manifest(tmp_path)
    assert errors == [] and warnings == []
    assert len(manifest["assets"]) == 1


def test_resolved_without_file_is_error(tmp_path):
    save_manifest(tmp_path, {"schema_version": SCHEMA_VERSION, "assets": [{
        "id": "a", "section": "hero", "type": "image", "role": "inline",
        "source": "seek", "status": "resolved", "path": "assets/missing.png",
        "license": "CC0",
    }]})
    errors, _, _ = validate_manifest(tmp_path)
    assert any("file not found" in e for e in errors)


def test_resolved_without_license_warns(tmp_path):
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "a.png").write_bytes(b"x")
    save_manifest(tmp_path, {"schema_version": SCHEMA_VERSION, "assets": [{
        "id": "a", "section": "hero", "type": "image", "role": "inline",
        "source": "seek", "status": "resolved", "path": "assets/a.png",
    }]})
    errors, warnings, _ = validate_manifest(tmp_path)
    assert errors == []
    assert any("license" in w for w in warnings)


def test_path_escape_is_error(tmp_path):
    save_manifest(tmp_path, {"schema_version": SCHEMA_VERSION, "assets": [{
        "id": "a", "section": "hero", "type": "image", "role": "inline",
        "source": "user", "status": "resolved", "path": "../outside.png",
        "license": "user-owned",
    }]})
    errors, _, _ = validate_manifest(tmp_path)
    assert any("escapes" in e for e in errors)


def test_duplicate_id_and_bad_enum_are_errors(tmp_path):
    save_manifest(tmp_path, {"schema_version": SCHEMA_VERSION, "assets": [
        {"id": "a", "section": "s", "type": "image", "role": "inline",
         "source": "user", "status": "planned"},
        {"id": "a", "section": "s", "type": "hologram", "role": "inline",
         "source": "user", "status": "planned"},
    ]})
    errors, _, _ = validate_manifest(tmp_path)
    assert any("duplicate id" in e for e in errors)
    assert any("hologram" in e for e in errors)


def test_role_type_mismatch_warns(tmp_path):
    save_manifest(tmp_path, {"schema_version": SCHEMA_VERSION, "assets": [{
        "id": "a", "section": "s", "type": "image", "role": "bgm",
        "source": "user", "status": "planned",
    }]})
    errors, warnings, _ = validate_manifest(tmp_path)
    assert errors == []
    assert any("unusual for role" in w for w in warnings)


# ---- CLI behaviour -----------------------------------------------------------

def test_cli_init_add_file_and_validate(tmp_path):
    src = tmp_path / "user_screenshot.png"
    src.write_bytes(b"png-bytes")
    video = tmp_path / "demo"
    video.mkdir()

    code, env = run_cli("init", str(video))
    assert code == 0 and env["ok"] and env["data"]["created"]

    code, env = run_cli("add", str(video), "--id", "hero_bg", "--section", "hero",
                        "--type", "image", "--role", "background", "--file", str(src))
    assert code == 0 and env["ok"]
    assert env["data"]["asset"]["status"] == "resolved"
    assert env["data"]["asset"]["license"] == "user-owned"
    assert (video / "assets" / "hero_bg.png").read_bytes() == b"png-bytes"

    code, env = run_cli("validate", str(video))
    assert code == 0 and env["data"]["valid"]


def test_cli_add_duplicate_requires_replace(tmp_path):
    video = tmp_path / "demo"
    video.mkdir()
    args = ("add", str(video), "--id", "x", "--section", "s",
            "--type", "overlay", "--role", "overlay", "--source", "hyperframes")
    code, env = run_cli(*args)
    assert code == 0 and env["data"]["asset"]["status"] == "planned"

    code, env = run_cli(*args)
    assert code == 1 and not env["ok"]
    assert env["error"]["code"] == "validation_failed"

    code, env = run_cli(*args, "--replace")
    assert code == 0 and env["data"]["replaced"]


def test_cli_add_cost_estimate_marks_pending(tmp_path):
    video = tmp_path / "demo"
    video.mkdir()
    code, env = run_cli("add", str(video), "--id", "broll", "--section", "intro",
                        "--type", "video", "--role", "broll", "--source", "videogen",
                        "--prompt", "city dusk", "--cost-estimate", "~1.2 RMB")
    assert code == 0
    assert env["data"]["asset"]["status"] == "pending_confirmation"


def test_cli_validate_broken_manifest_fails(tmp_path):
    video = tmp_path / "demo"
    video.mkdir()
    path = manifest_path(video)
    path.parent.mkdir(parents=True)
    path.write_text("{not json", encoding="utf-8")
    code, env = run_cli("validate", str(video))
    assert code == 1 and not env["ok"]
    assert load_manifest(video)[1] is not None
