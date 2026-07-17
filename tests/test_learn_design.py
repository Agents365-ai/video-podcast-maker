"""Tests for scripts/learn_design.py — pure helpers + prefs accounting.

Frame extraction (ffmpeg) and Playwright integration are deliberately
out-of-scope; these tests cover the parts that mutate user state:
reference-index/style-profile bookkeeping, delete preview, and ID gen.
"""
import json
from pathlib import Path

import pytest

# scripts/ is on sys.path via tests/conftest.py
from learn_design import (  # noqa: E402
    _compute_delete_preview,
    _id_from_url,
    add_reference_index,
    add_style_profile,
    cleanup_orphaned_references,
    detect_input_type,
    detect_orientation,
    generate_reference_id,
    remove_reference,
)


# --- detect_input_type ----------------------------------------------------

def test_detect_input_type_url():
    assert detect_input_type("https://example.com/video") == "url"
    assert detect_input_type("http://example.com/x") == "url"


def test_detect_input_type_unsupported(tmp_path):
    p = tmp_path / "doc.txt"
    p.write_text("x")
    assert detect_input_type(str(p)) == "unsupported"


def test_detect_input_type_image_and_video(tmp_path):
    img = tmp_path / "a.png"
    img.write_bytes(b"\x89PNG")
    vid = tmp_path / "b.mp4"
    vid.write_bytes(b"\x00")
    assert detect_input_type(str(img)) == "image"
    assert detect_input_type(str(vid)) == "local_video"


def test_detect_input_type_not_found():
    assert detect_input_type("/nope/missing.png") == "not_found"


# --- orientation ----------------------------------------------------------

def test_detect_orientation_buckets():
    assert detect_orientation(1920, 1080) == "horizontal"
    assert detect_orientation(1080, 1920) == "vertical"
    assert detect_orientation(1000, 1000) == "square"


# --- _id_from_url ---------------------------------------------------------

def test_id_from_url_bilibili():
    assert _id_from_url("https://www.bilibili.com/video/BV1xx411c7mD") == "bilibili-BV1xx411c7mD"


def test_id_from_url_youtube_watch():
    assert _id_from_url("https://www.youtube.com/watch?v=abc-123") == "youtube-abc-123"


def test_id_from_url_youtube_short():
    assert _id_from_url("https://youtu.be/xyz_456") == "youtube-xyz_456"


def test_id_from_url_fallback_is_deterministic():
    a = _id_from_url("https://example.com/random/path")
    b = _id_from_url("https://example.com/random/path")
    assert a == b
    assert a.startswith("ref-")


# --- generate_reference_id collision avoidance ----------------------------

def test_generate_reference_id_handles_collisions():
    existing = {"bilibili-BV1xx411c7mD", "bilibili-BV1xx411c7mD-2"}
    new_id = generate_reference_id(
        "https://www.bilibili.com/video/BV1xx411c7mD",
        existing_ids=existing,
    )
    assert new_id == "bilibili-BV1xx411c7mD-3"


# --- add_reference_index --------------------------------------------------

def test_add_reference_index_persists_tags():
    prefs = {}
    add_reference_index(prefs, ref_id="ref-1", title="T", source_url=None, tags=["a", "b"])
    assert prefs["design_references"]["ref-1"]["tags"] == ["a", "b"]
    assert prefs["design_references"]["ref-1"]["title"] == "T"


# --- add_style_profile ----------------------------------------------------

def test_add_style_profile_unions_layouts_and_merges_props():
    prefs = {}
    add_style_profile(
        prefs, name="tech-minimal", description="d",
        props_override={"primaryColor": "#000"},
        preferred_layouts=["hero", "grid"],
        references=["r1"],
    )
    add_style_profile(
        prefs, name="tech-minimal", description="d2",
        props_override={"primaryColor": "#111", "accentColor": "#222"},
        preferred_layouts=["grid", "stack"],
        references=["r1", "r2"],
    )
    p = prefs["style_profiles"]["tech-minimal"]
    assert p["description"] == "d2"
    assert p["preferred_layouts"] == ["hero", "grid", "stack"]
    assert p["props_override"] == {"primaryColor": "#111", "accentColor": "#222"}
    assert p["references"] == ["r1", "r2"]


# --- remove_reference / cleanup_orphaned_references -----------------------

def test_remove_reference_cleans_index_and_profiles(tmp_path):
    prefs = {
        "design_references": {"ref-1": {"path": "x", "title": "t"}},
        "style_profiles": {"prof-a": {"references": ["ref-1", "ref-2"]}},
    }
    ref_dir = tmp_path / "ref-1"
    ref_dir.mkdir()
    (ref_dir / "report.json").write_text("{}")
    remove_reference(prefs, "ref-1", str(tmp_path))
    assert "ref-1" not in prefs["design_references"]
    assert prefs["style_profiles"]["prof-a"]["references"] == ["ref-2"]
    assert not ref_dir.exists()


def test_cleanup_orphaned_references_drops_missing_dirs(tmp_path):
    prefs = {
        "design_references": {
            "kept":   {"path": "x"},
            "gone":   {"path": "y"},
        },
    }
    (tmp_path / "kept").mkdir()
    cleanup_orphaned_references(prefs, str(tmp_path))
    assert list(prefs["design_references"].keys()) == ["kept"]


# --- _compute_delete_preview ----------------------------------------------

def test_compute_delete_preview_reports_used_by_profiles(tmp_path):
    prefs = {
        "design_references": {"r1": {"title": "T"}},
        "style_profiles": {
            "p1": {"references": ["r1"]},
            "p2": {"references": ["other"]},
        },
    }
    ref_dir = tmp_path / "r1"
    ref_dir.mkdir()
    (ref_dir / "frames").mkdir()
    (ref_dir / "frames" / "frame_0001.jpg").write_bytes(b"x")
    preview = _compute_delete_preview(prefs, "r1", str(ref_dir))
    assert preview["ref_id"] == "r1"
    assert preview["on_disk"] is True
    assert preview["frame_count"] == 1
    assert preview["used_by_profiles"] == ["p1"]
