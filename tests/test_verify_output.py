"""Tests for scripts/verify_output.py — acceptance gate logic.

ffprobe is mocked out so these tests don't need real video bytes; the goal is
to lock down the structural contract verify() promises to agents (exit codes,
result dict shape, auto-fix behavior, drift threshold).
"""
import json
import struct
from pathlib import Path

import pytest

# scripts/ is on sys.path via tests/conftest.py
import verify_output  # noqa: E402
from verify_output import auto_fix, png_size, verify  # noqa: E402


# --- Fixtures ----------------------------------------------------------------

REQUIRED_NON_VIDEO = [
    'podcast.txt',
    'podcast_audio.srt',
    'publish_info.md',
]
VIDEO_FILES = ['podcast_audio.wav', 'output.mp4', 'video_with_bgm.mp4', 'final_video.mp4']


def _make_png(path: Path, width: int, height: int):
    """Write 24 bytes that satisfy png_size()'s header parser."""
    sig = b'\x89PNG\r\n\x1a\n'
    ihdr_len = struct.pack('>I', 13)
    ihdr_type = b'IHDR'
    dims = struct.pack('>II', width, height)
    path.write_bytes(sig + ihdr_len + ihdr_type + dims)


def _make_publish_info(path: Path, with_promo: bool = True):
    promo = 'github.com/Agents365-ai/video-podcast-maker' if with_promo else 'no-promo'
    path.write_text(
        f"{promo}\n\n"
        "## 标题\nT\n## 标签\nx\n## 简介\nd\n## 章节\n0:00 a\n",
        encoding='utf-8',
    )


def _make_timing(path: Path, total_duration: float, sections=None):
    path.write_text(
        json.dumps({
            'total_duration': total_duration,
            'sections': sections or [{'name': 'hero', 'start_time': 0, 'duration': total_duration}],
        }),
        encoding='utf-8',
    )


def _populate_full_dir(d: Path):
    """Create every required file as plausible content. Caller still mocks ffprobe."""
    (d / 'podcast.txt').write_text('hi', encoding='utf-8')
    (d / 'podcast_audio.srt').write_text('1\n00:00:00,000 --> 00:00:01,000\nhi\n', encoding='utf-8')
    _make_publish_info(d / 'publish_info.md', with_promo=True)
    _make_timing(d / 'timing.json', total_duration=60.0)
    for name in VIDEO_FILES:
        (d / name).write_bytes(b'\x00' * 16)
    _make_png(d / 'thumbnail_remotion_16x9.png', 1920, 1080)
    _make_png(d / 'thumbnail_remotion_4x3.png', 1200, 900)


def _stub_ffprobe(width=3840, height=2160, duration=60.0, audio='aac'):
    def stub(path):
        return {
            'width': width,
            'height': height,
            'duration': duration,
            'video_codec': 'h264',
            'audio_codec': audio,
        }
    return stub


def _stub_ffprobe_audio(duration=60.0, audio='pcm_s16le'):
    def stub(path):
        return {'duration': duration, 'audio_codec': audio}
    return stub


# --- png_size ----------------------------------------------------------------

def test_png_size_valid_header_returns_dimensions(tmp_path):
    p = tmp_path / 't.png'
    _make_png(p, 1920, 1080)
    assert png_size(p) == (1920, 1080)


def test_png_size_corrupt_signature_returns_none(tmp_path):
    p = tmp_path / 'bad.png'
    p.write_bytes(b'GIF89a' + b'\x00' * 32)
    assert png_size(p) is None


def test_png_size_missing_file_returns_none(tmp_path):
    assert png_size(tmp_path / 'nope.png') is None


# --- auto_fix ----------------------------------------------------------------

def test_auto_fix_creates_final_from_bgm_mix(tmp_path):
    (tmp_path / 'video_with_bgm.mp4').write_bytes(b'BGM')
    fixes = auto_fix(tmp_path)
    final = tmp_path / 'final_video.mp4'
    assert final.exists()
    assert final.read_bytes() == b'BGM'
    assert any('video_with_bgm' in f for f in fixes)


def test_auto_fix_falls_back_to_output_when_no_bgm(tmp_path):
    (tmp_path / 'output.mp4').write_bytes(b'RAW')
    fixes = auto_fix(tmp_path)
    final = tmp_path / 'final_video.mp4'
    assert final.exists()
    assert final.read_bytes() == b'RAW'
    assert any('output.mp4' in f for f in fixes)


def test_auto_fix_noop_when_final_already_exists(tmp_path):
    (tmp_path / 'final_video.mp4').write_bytes(b'KEEP')
    (tmp_path / 'video_with_bgm.mp4').write_bytes(b'IGNORE')
    fixes = auto_fix(tmp_path)
    assert fixes == []
    assert (tmp_path / 'final_video.mp4').read_bytes() == b'KEEP'


# --- verify ------------------------------------------------------------------

def test_verify_missing_directory_exits_1(tmp_path):
    exit_code, result = verify(tmp_path / 'does-not-exist', strict=False, do_auto_fix=True)
    assert exit_code == 1
    assert result['errors']
    assert 'Directory not found' in result['errors'][0]


def test_verify_all_clean_exits_0(tmp_path, monkeypatch):
    _populate_full_dir(tmp_path)
    monkeypatch.setattr(verify_output, 'ffprobe_video', _stub_ffprobe())
    monkeypatch.setattr(verify_output, 'ffprobe_audio', _stub_ffprobe_audio())
    exit_code, result = verify(tmp_path, strict=False, do_auto_fix=True)
    assert exit_code == 0
    assert result['required_files']['missing'] == []
    assert result['errors'] == []
    assert result['warnings'] == []
    assert result['final_video']['resolution_ok'] is True
    assert result['audio_timing']['ok'] is True


def test_verify_missing_required_files_exits_1(tmp_path, monkeypatch):
    _populate_full_dir(tmp_path)
    (tmp_path / 'podcast.txt').unlink()
    monkeypatch.setattr(verify_output, 'ffprobe_video', _stub_ffprobe())
    monkeypatch.setattr(verify_output, 'ffprobe_audio', _stub_ffprobe_audio())
    exit_code, result = verify(tmp_path, strict=False, do_auto_fix=True)
    assert exit_code == 1
    assert 'podcast.txt' in result['required_files']['missing']
    assert 'podcast.txt' in result['errors']


def test_verify_resolution_mismatch_records_error(tmp_path, monkeypatch):
    _populate_full_dir(tmp_path)
    monkeypatch.setattr(verify_output, 'ffprobe_video', _stub_ffprobe(width=1920, height=1080))
    monkeypatch.setattr(verify_output, 'ffprobe_audio', _stub_ffprobe_audio())
    exit_code, result = verify(tmp_path, strict=False, do_auto_fix=True)
    assert exit_code == 1
    assert result['final_video']['resolution_ok'] is False
    assert any('Resolution' in e for e in result['errors'])


def test_verify_drift_emits_warning_and_exits_2(tmp_path, monkeypatch):
    _populate_full_dir(tmp_path)
    # WAV reports 60s, timing.json says 65s → drift -5s, well over 0.5s threshold.
    _make_timing(tmp_path / 'timing.json', total_duration=65.0)
    monkeypatch.setattr(verify_output, 'ffprobe_video', _stub_ffprobe(duration=60.0))
    monkeypatch.setattr(verify_output, 'ffprobe_audio', _stub_ffprobe_audio(duration=60.0))
    exit_code, result = verify(tmp_path, strict=False, do_auto_fix=True)
    assert exit_code == 2
    assert result['audio_timing']['ok'] is False
    assert any('drift' in w.lower() for w in result['warnings'])


def test_verify_strict_promotes_warnings_to_failure(tmp_path, monkeypatch):
    _populate_full_dir(tmp_path)
    _make_publish_info(tmp_path / 'publish_info.md', with_promo=False)
    monkeypatch.setattr(verify_output, 'ffprobe_video', _stub_ffprobe())
    monkeypatch.setattr(verify_output, 'ffprobe_audio', _stub_ffprobe_audio())
    exit_code, result = verify(tmp_path, strict=True, do_auto_fix=True)
    assert exit_code == 1
    assert result['warnings']
    assert result['publish_info']['promo_present'] is False


def test_verify_no_fix_skips_autofix(tmp_path, monkeypatch):
    _populate_full_dir(tmp_path)
    (tmp_path / 'final_video.mp4').unlink()
    monkeypatch.setattr(verify_output, 'ffprobe_video', _stub_ffprobe())
    monkeypatch.setattr(verify_output, 'ffprobe_audio', _stub_ffprobe_audio())
    exit_code, result = verify(tmp_path, strict=False, do_auto_fix=False)
    assert result['fixes_applied'] == []
    assert 'final_video.mp4' in result['required_files']['missing']
    assert exit_code == 1


def test_verify_thumbnail_size_mismatch_warns(tmp_path, monkeypatch):
    _populate_full_dir(tmp_path)
    _make_png(tmp_path / 'thumbnail_remotion_16x9.png', 1280, 720)  # wrong size
    monkeypatch.setattr(verify_output, 'ffprobe_video', _stub_ffprobe())
    monkeypatch.setattr(verify_output, 'ffprobe_audio', _stub_ffprobe_audio())
    exit_code, result = verify(tmp_path, strict=False, do_auto_fix=True)
    thumb = result['thumbnails']['thumbnail_remotion_16x9.png']
    assert thumb['ok'] is False
    assert thumb['size'] == [1280, 720]
    assert exit_code == 2  # warnings only


# --- AI thumbnail acceptance & platform-aware publish_info ----------------

def test_verify_accepts_ai_thumbnail_in_place_of_remotion(tmp_path, monkeypatch):
    _populate_full_dir(tmp_path)
    # Replace Remotion thumbnails with AI-generated ones at the same dims.
    (tmp_path / 'thumbnail_remotion_16x9.png').unlink()
    (tmp_path / 'thumbnail_remotion_4x3.png').unlink()
    _make_png(tmp_path / 'thumbnail_ai_16x9.png', 1920, 1080)
    _make_png(tmp_path / 'thumbnail_ai_4x3.png', 1200, 900)
    monkeypatch.setattr(verify_output, 'ffprobe_video', _stub_ffprobe())
    monkeypatch.setattr(verify_output, 'ffprobe_audio', _stub_ffprobe_audio())
    exit_code, result = verify(tmp_path, strict=False, do_auto_fix=True)
    assert exit_code == 0
    assert result['errors'] == []


def test_verify_youtube_platform_uses_english_section_headers(tmp_path, monkeypatch):
    _populate_full_dir(tmp_path)
    # Rewrite publish_info with YouTube-style English headers.
    (tmp_path / 'publish_info.md').write_text(
        'github.com/Agents365-ai/video-podcast-maker\n\n'
        '## Title\nT\n## Tags\nx\n## Description\nd\n## Chapters\n0:00 a\n',
        encoding='utf-8',
    )
    monkeypatch.setattr(verify_output, '_resolve_platform', lambda: 'youtube')
    monkeypatch.setattr(verify_output, 'ffprobe_video', _stub_ffprobe())
    monkeypatch.setattr(verify_output, 'ffprobe_audio', _stub_ffprobe_audio())
    exit_code, result = verify(tmp_path, strict=False, do_auto_fix=True)
    assert exit_code == 0
    assert result['publish_info']['platform'] == 'youtube'
    assert result['publish_info']['sections_missing'] == []


def test_verify_douyin_platform_does_not_require_chapters(tmp_path, monkeypatch):
    _populate_full_dir(tmp_path)
    (tmp_path / 'publish_info.md').write_text(
        'github.com/Agents365-ai/video-podcast-maker\n\n'
        '## 文案\nhi\n## 话题标签\n#x\n',
        encoding='utf-8',
    )
    monkeypatch.setattr(verify_output, '_resolve_platform', lambda: 'douyin')
    monkeypatch.setattr(verify_output, 'ffprobe_video', _stub_ffprobe())
    monkeypatch.setattr(verify_output, 'ffprobe_audio', _stub_ffprobe_audio())
    exit_code, result = verify(tmp_path, strict=False, do_auto_fix=True)
    assert exit_code == 0
    assert result['publish_info']['sections_missing'] == []
