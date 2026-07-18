"""Tests for ttsCN word-boundary merge logic.

Run from repo root: PYTHONPATH=skills/video-podcast-maker/scripts python3 -m pytest tests/test_ttscn_boundaries.py -v
"""
import pytest

# Import requires being in the scripts/ directory (package-relative imports)
from tts.backends.ttscn import _merge_native_boundaries


def test_basic_merge():
    chunk = "Hello, world."
    native = [
        {"text": "Hello", "offset_sec": 0.0, "duration_sec": 0.5},
        {"text": "world", "offset_sec": 0.6, "duration_sec": 0.4},
    ]
    result = _merge_native_boundaries(chunk, native, base_offset=10.0)
    texts = [w["text"] for w in result]
    assert "Hello" in texts
    assert "world" in texts
    assert "," in texts
    assert "." in texts
    hello = next(w for w in result if w["text"] == "Hello")
    assert hello["offset"] == 10.0


def test_syllable_dedup():
    """MiniMax: 3 entries for '37' → merge into 1; 5 entries for '128' → merge into 1."""
    chunk = "价格从37元涨到128元。"
    native = [
        {"text": "价格", "offset_sec": 0.0, "duration_sec": 0.4},
        {"text": "从", "offset_sec": 0.4, "duration_sec": 0.2},
        {"text": "37", "offset_sec": 0.6, "duration_sec": 0.15},
        {"text": "37", "offset_sec": 0.75, "duration_sec": 0.15},
        {"text": "37", "offset_sec": 0.90, "duration_sec": 0.10},
        {"text": "元", "offset_sec": 1.0, "duration_sec": 0.15},
        {"text": "涨", "offset_sec": 1.15, "duration_sec": 0.15},
        {"text": "到", "offset_sec": 1.3, "duration_sec": 0.1},
        {"text": "128", "offset_sec": 1.4, "duration_sec": 0.1},
        {"text": "128", "offset_sec": 1.5, "duration_sec": 0.1},
        {"text": "128", "offset_sec": 1.6, "duration_sec": 0.1},
        {"text": "128", "offset_sec": 1.7, "duration_sec": 0.1},
        {"text": "128", "offset_sec": 1.8, "duration_sec": 0.1},
        {"text": "元", "offset_sec": 1.9, "duration_sec": 0.15},
    ]
    result = _merge_native_boundaries(chunk, native, 0.0)
    texts = [w["text"] for w in result]
    assert texts.count("37") == 1
    assert texts.count("128") == 1
    # Duration should span all syllables
    merged_37 = next(w for w in result if w["text"] == "37")
    assert merged_37["duration"] == pytest.approx(0.40, abs=0.02)
    merged_128 = next(w for w in result if w["text"] == "128")
    assert merged_128["duration"] == pytest.approx(0.50, abs=0.02)


def test_non_consecutive_same_tokens_not_merged():
    chunk = "37 is greater than 37."
    native = [
        {"text": "37", "offset_sec": 0.0, "duration_sec": 0.3},
        {"text": "is", "offset_sec": 0.3, "duration_sec": 0.2},
        {"text": "greater", "offset_sec": 0.5, "duration_sec": 0.4},
        {"text": "than", "offset_sec": 0.9, "duration_sec": 0.2},
        {"text": "37", "offset_sec": 1.1, "duration_sec": 0.3},
    ]
    result = _merge_native_boundaries(chunk, native, 0.0)
    texts = [w["text"] for w in result]
    assert texts.count("37") == 2
