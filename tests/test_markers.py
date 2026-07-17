"""Tests for tts/markers.py — [PAUSE:x] + sound tags (rendering lives in ttsCN)."""
from generate_tts import chunk_text
from tts.markers import protect_pauses, restore_pauses, strip_markers

SAMPLE = "你好。[PAUSE:0.8]欢迎观看。(chuckle)结果很意外。[PAUSE:1]完。"


def test_strip_removes_everything():
    assert strip_markers(SAMPLE) == "你好。欢迎观看。结果很意外。完。"


def test_protect_restore_round_trip():
    assert restore_pauses(protect_pauses(SAMPLE)) == SAMPLE


def test_chunker_never_splits_inside_marker():
    # Force tiny chunks so the '.' inside [PAUSE:0.8] would be a split point
    # without protection.
    text = "第一句话说完了。[PAUSE:0.8]第二句话开始了。第三句话也来了。"
    chunks = [restore_pauses(c) for c in chunk_text(protect_pauses(text), 15)]
    joined = "".join(chunks)
    assert "[PAUSE:0.8]" in joined
    for c in chunks:
        # No chunk may contain a broken half-marker
        assert c.count("[PAUSE") == c.count("]" ) or "[PAUSE:0.8]" in c or "[PAUSE" not in c
    assert not any("[PAUSE:0" in c and "]" not in c.split("[PAUSE:0")[1] for c in chunks)


def test_unknown_parens_untouched():
    text = "这个(备注)不是声音标签。"
    assert strip_markers(text) == text
