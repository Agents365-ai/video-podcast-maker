"""Tests for scripts/generate_shorts.py — pure helpers + filter logic.

The pipeline calls ffmpeg / npx, but the section selection and per-section
metadata generation are pure functions worth covering. These tests stay
ffmpeg-free.
"""
import json
import os
import sys
from pathlib import Path

import pytest

# scripts/ is on sys.path via tests/conftest.py
from generate_shorts import (  # noqa: E402
    DEFAULT_MIN_DURATION,
    DEFAULT_SKIP,
    INTRO_FRAMES,
    CTA_FRAMES,
    filter_sections,
    generate_composition_stub,
    generate_timing,
    load_script,
    to_pascal_case,
)


# --- to_pascal_case --------------------------------------------------------

def test_pascal_case_handles_hyphens_underscores_and_plain():
    assert to_pascal_case("content-1") == "Content1"
    assert to_pascal_case("pipeline") == "Pipeline"
    assert to_pascal_case("my_section") == "MySection"
    assert to_pascal_case("arch-v2") == "ArchV2"


# --- filter_sections -------------------------------------------------------

def _timing(*sections):
    return {"sections": list(sections)}


def test_filter_skips_default_hero_outro():
    timing = _timing(
        {"name": "hero",    "duration": 30, "is_silent": False},
        {"name": "outro",   "duration": 30, "is_silent": False},
        {"name": "content", "duration": 30, "is_silent": False},
    )
    kept = filter_sections(timing, DEFAULT_MIN_DURATION, DEFAULT_SKIP)
    assert [s["name"] for s in kept] == ["content"]


def test_filter_drops_silent_sections():
    timing = _timing(
        {"name": "content", "duration": 30, "is_silent": True},
    )
    assert filter_sections(timing, DEFAULT_MIN_DURATION, "") == []


def test_filter_drops_sections_below_min_duration():
    timing = _timing(
        {"name": "short", "duration": 5,  "is_silent": False},
        {"name": "long",  "duration": 30, "is_silent": False},
    )
    kept = filter_sections(timing, min_duration=20, skip_names="")
    assert [s["name"] for s in kept] == ["long"]


# --- load_script -----------------------------------------------------------

def test_load_script_extracts_first_line_per_section(tmp_path):
    (tmp_path / "podcast.txt").write_text(
        "[SECTION:hero]\n你好，这是开场。\n\n[SECTION:demo]\n演示一下功能！更多说明。\n",
        encoding="utf-8",
    )
    titles = load_script(str(tmp_path))
    assert titles["hero"].startswith("你好")
    assert titles["demo"].startswith("演示一下功能")


def test_load_script_missing_file_returns_empty(tmp_path):
    assert load_script(str(tmp_path)) == {}


# --- generate_timing -------------------------------------------------------

def test_generate_timing_layout(tmp_path):
    section = {
        "name": "content",
        "label": "Content",
        "duration": 30.0,
        "duration_frames": 900,
        "start_time": 0.0,
    }
    timing = generate_timing(section, str(tmp_path))
    saved = json.loads((tmp_path / "short_timing.json").read_text())
    assert saved == timing
    assert timing["total_frames"] == INTRO_FRAMES + 900 + CTA_FRAMES
    names = [s["name"] for s in timing["sections"]]
    assert names == ["intro", "content", "cta"]
    assert timing["sections"][0]["is_silent"] is True
    assert timing["sections"][2]["is_silent"] is True


# --- generate_composition_stub --------------------------------------------

def test_composition_stub_writes_info_and_snippet(tmp_path):
    section = {"name": "demo", "duration": 30.0, "duration_frames": 900}
    timing = generate_timing(section, str(tmp_path))
    comp_id = generate_composition_stub(
        section, "Video Title", str(tmp_path), timing, "Demo Title",
    )
    assert comp_id == "DemoShort"
    info = json.loads((tmp_path / "short_info.json").read_text())
    assert info["comp_id"] == "DemoShort"
    assert info["section_name"] == "demo"
    assert info["width"] == 2160 and info["height"] == 3840
    snippet = (tmp_path / "register_snippet.tsx").read_text()
    assert "DemoShort" in snippet
    assert "DemoShortVideo" in snippet
