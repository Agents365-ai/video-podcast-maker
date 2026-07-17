"""Tests for scripts/align_timing_from_srt.py — anchor timing.json slides to SRT.

Covers the pure parsers/helpers (clean_text, parse_srt, parse_podcast_sections,
build_search_keys, find_all_in_srt) and the end-to-end align_timing() contract:
result-dict shape, slide monotonicity, explicit-section mapping, dry-run, and the
errors raised for missing/malformed inputs. ffprobe is monkeypatched so the suite
needs no ffmpeg binary.
"""
import json
import textwrap
from pathlib import Path

import pytest

# scripts/ is on sys.path via tests/conftest.py
import align_timing_from_srt as ali  # noqa: E402
from align_timing_from_srt import (  # noqa: E402
    build_search_keys,
    build_srt_index,
    clean_text,
    find_all_in_srt,
    parse_podcast_sections,
    parse_srt,
)


# --- Fixtures ----------------------------------------------------------------

PODCAST_TXT = textwrap.dedent("""\
    [SECTION:hero]
    大家好，欢迎来到本期视频。今天我们聊聊缓存。

    [SECTION:problem]
    缓存失效是计算机科学的两大难题之一。

    [SECTION:outro]
    感谢观看，下期再见。
""")

# SRT whose entry text matches the podcast so section anchors resolve.
SRT_TXT = textwrap.dedent("""\
    1
    00:00:00,000 --> 00:00:03,000
    大家好欢迎来到本期视频

    2
    00:00:03,000 --> 00:00:06,000
    今天我们聊聊缓存

    3
    00:00:06,000 --> 00:00:10,000
    缓存失效是计算机科学的两大难题之一

    4
    00:00:10,000 --> 00:00:13,000
    感谢观看下期再见
""")


def _timing(sections):
    return {"fps": 30, "total_duration": 0, "total_frames": 0, "sections": sections}


def _write_project(tmp_path: Path, timing: dict,
                   podcast: str = PODCAST_TXT, srt: str = SRT_TXT) -> Path:
    vdir = tmp_path / "demo"
    vdir.mkdir()
    (vdir / "podcast.txt").write_text(podcast, encoding="utf-8")
    (vdir / "podcast_audio.srt").write_text(srt, encoding="utf-8")
    (vdir / "podcast_audio.wav").write_bytes(b"RIFF....WAVE")  # presence only
    (vdir / "timing.json").write_text(
        json.dumps(timing, ensure_ascii=False), encoding="utf-8")
    return vdir


@pytest.fixture(autouse=True)
def _stub_ffprobe(monkeypatch):
    """align_timing calls ffprobe for the real WAV duration — stub it."""
    monkeypatch.setattr(ali, "ffprobe_duration", lambda _p: 13.0)


# --- Pure helpers ------------------------------------------------------------

def test_clean_text_strips_punct_and_lowercases():
    assert clean_text("Hello, 世界！123") == "hello世界123"
    assert clean_text("") == ""
    assert clean_text("。，、 \n") == ""


def test_parse_srt_extracts_start_times():
    entries = parse_srt_from_str(SRT_TXT)
    assert len(entries) == 4
    assert entries[0]["start"] == pytest.approx(0.0)
    assert entries[2]["start"] == pytest.approx(6.0)
    assert "缓存失效" in entries[2]["text"]


def test_parse_podcast_sections_names_and_first_text():
    secs = parse_podcast_sections_from_str(PODCAST_TXT)
    assert [s["name"] for s in secs] == ["hero", "problem", "outro"]
    assert secs[0]["first_text"].startswith("大家好")


def test_build_search_keys_dedupes_and_enforces_min_length():
    slide = {"headline": "缓存失效问题", "sub": "abc", "bullets": ["计算机科学难题", "计算机科学难题"]}
    keys = build_search_keys(slide)
    assert "缓存失效问题" in keys
    assert "abc" not in keys                       # shorter than 4 chars, dropped
    assert keys.count("计算机科学难题") == 1        # duplicate collapsed


def test_find_all_in_srt_locates_phrase():
    entries = parse_srt_from_str(SRT_TXT)
    concat, offsets = build_srt_index(entries)
    matches = find_all_in_srt("缓存失效", concat, offsets, entries, 0, len(entries))
    assert matches
    idx, start, length = matches[0]
    assert entries[idx]["start"] == pytest.approx(6.0)


# --- End-to-end align_timing -------------------------------------------------

def test_align_writes_timing_and_backup(tmp_path):
    sections = [
        {"name": "hero", "headline": "欢迎来到本期视频", "duration": 6.0, "start_frame": 0},
        {"name": "problem", "headline": "缓存失效是计算机科学的两大难题之一", "duration": 4.0, "start_frame": 180},
        {"name": "outro", "headline": "感谢观看下期再见", "duration": 3.0, "start_frame": 300},
    ]
    vdir = _write_project(tmp_path, _timing(sections))

    result = ali.align_timing(vdir, dry_run=False)

    assert result["written"] is True
    assert result["slides_total"] == 3
    assert result["audio_duration"] == pytest.approx(13.0)
    assert (vdir / "timing.json.bak").exists()

    out = json.loads((vdir / "timing.json").read_text(encoding="utf-8"))
    assert out["total_duration"] == pytest.approx(13.0)
    assert out["total_frames"] == int(13.0 * 30)
    starts = [s["start_time"] for s in out["sections"]]
    assert starts == sorted(starts)               # monotonic, non-decreasing
    assert out["sections"][0]["start_time"] == pytest.approx(0.0)


def test_align_dry_run_does_not_write(tmp_path):
    sections = [
        {"name": "hero", "headline": "欢迎来到本期视频", "duration": 6.0},
        {"name": "outro", "headline": "感谢观看下期再见", "duration": 3.0},
    ]
    vdir = _write_project(tmp_path, _timing(sections))
    before = (vdir / "timing.json").read_text(encoding="utf-8")

    result = ali.align_timing(vdir, dry_run=True)

    assert result["written"] is False
    assert result["dry_run"] is True
    assert not (vdir / "timing.json.bak").exists()
    assert (vdir / "timing.json").read_text(encoding="utf-8") == before


def test_align_counts_explicit_section_field(tmp_path):
    sections = [
        {"name": "s1", "section": "hero", "headline": "欢迎来到本期视频", "duration": 6.0},
        {"name": "s2", "section": "problem", "headline": "缓存失效", "duration": 4.0},
        {"name": "s3", "section": "outro", "headline": "感谢观看", "duration": 3.0},
    ]
    vdir = _write_project(tmp_path, _timing(sections))

    result = ali.align_timing(vdir, dry_run=True)

    assert result["slides_explicit_section"] == 3
    assert [s["section"] for s in result["slides"]] == ["hero", "problem", "outro"]


def test_align_missing_input_raises_filenotfound(tmp_path):
    vdir = _write_project(tmp_path, _timing([{"name": "hero", "duration": 6.0}]))
    (vdir / "podcast_audio.srt").unlink()
    with pytest.raises(FileNotFoundError):
        ali.align_timing(vdir, dry_run=True)


def test_align_no_section_markers_raises_valueerror(tmp_path):
    vdir = _write_project(
        tmp_path, _timing([{"name": "hero", "duration": 6.0}]),
        podcast="just narration, no markers at all",
    )
    with pytest.raises(ValueError):
        ali.align_timing(vdir, dry_run=True)


def test_align_empty_timing_raises_valueerror(tmp_path):
    vdir = _write_project(tmp_path, _timing([]))
    with pytest.raises(ValueError):
        ali.align_timing(vdir, dry_run=True)


# --- helpers that read from a string instead of a file -----------------------

def parse_srt_from_str(s: str):
    import tempfile
    p = Path(tempfile.mkstemp(suffix=".srt")[1])
    p.write_text(s, encoding="utf-8")
    return parse_srt(p)


def parse_podcast_sections_from_str(s: str):
    import tempfile
    p = Path(tempfile.mkstemp(suffix=".txt")[1])
    p.write_text(s, encoding="utf-8")
    return parse_podcast_sections(p)
