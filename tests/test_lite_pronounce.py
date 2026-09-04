"""Tests for the lite tts.py pronunciation layer (pronounce / number
conversion / boundary remapping) — pure functions, no network."""
import importlib.util
import os

LITE_TTS = os.path.join(
    os.path.dirname(__file__), os.pardir,
    "skills", "video-podcast-maker-lite", "scripts", "tts.py",
)

spec = importlib.util.spec_from_file_location("lite_tts", LITE_TTS)
lite_tts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lite_tts)


# ---------------------------------------------------------------------------
# int_to_cn / num_to_cn
# ---------------------------------------------------------------------------

def test_int_to_cn_common():
    cases = {
        0: "零", 2: "二", 8: "八", 19: "十九", 24: "二十四", 30: "三十",
        101: "一百零一", 300: "三百", 350: "三百五十", 397: "三百九十七",
        1001: "一千零一", 1200: "一千二百", 5600: "五千六百",
        10005: "一万零五", 12000: "一万二千", 12000000: "一千二百万",
    }
    for n, want in cases.items():
        assert lite_tts.int_to_cn(n) == want, f"{n}: got {lite_tts.int_to_cn(n)}"


def test_num_to_cn_decimals():
    assert lite_tts.num_to_cn("86.1") == "八十六点一"
    assert lite_tts.num_to_cn("1.0") == "一点零"
    assert lite_tts.num_to_cn("2.8") == "二点八"


# ---------------------------------------------------------------------------
# pronounce
# ---------------------------------------------------------------------------

def test_pronounce_numbers_and_mixed_tokens():
    spoken, pairs = lite_tts.pronounce("跑分 86.1 分，9B 和 35B-A3B，破了 1200 万。")
    assert "八十六点一" in spoken
    assert "九B" in spoken
    assert "三十五B" in spoken
    assert "A三B" in spoken
    assert "一千二百" in spoken
    # pairs are ordered by appearance and carry the display text;
    # a trailing quantifier is glued into the pair (spoken layer inserts no pause)
    assert [d for _s, d in pairs] == ["86.1 分", "9B", "35B", "A3B", "1200 万"]


def test_pronounce_explicit_aliases_win_over_generic():
    spoken, pairs = lite_tts.pronounce("35B MoE 和 FP8，基于 Qwen3.5。")
    assert "M O E" in spoken        # MoE read as letters, not "莫"
    assert "F P 八" in spoken
    assert "千问三点五" in spoken     # Qwen -> 千问 also inside mixed tokens
    displays = [d for _s, d in pairs]
    assert displays == ["35B", "MoE", "FP8", "Qwen", "3.5"]


def test_pronounce_plain_text_untouched():
    text = "大家好，欢迎来到我的频道。"
    spoken, pairs = lite_tts.pronounce(text)
    assert spoken == text
    assert pairs == []


# ---------------------------------------------------------------------------
# map_boundaries_to_display
# ---------------------------------------------------------------------------

def _wb(text, offset, duration):
    return {"text": text, "offset": offset, "duration": duration}


def test_map_boundaries_merges_spoken_run_into_display():
    # Azure splits "八十六点一" into word chunks; they must become one "86.1".
    wbs = [
        _wb("跑分", 0.0, 0.5), _wb(" ", 0.5, 0.05),
        _wb("八十", 0.55, 0.4), _wb("六点", 0.95, 0.4), _wb("一", 1.35, 0.2),
        _wb(" ", 1.55, 0.05), _wb("分", 1.6, 0.3),
    ]
    out = lite_tts.map_boundaries_to_display(wbs, [("八十六点一", "86.1")])
    texts = [w["text"] for w in out]
    assert "86.1" in texts
    assert "".join(texts) == "跑分 八十六点一 分".replace("八十六点一", "86.1")
    entry = next(w for w in out if w["text"] == "86.1")
    assert abs(entry["offset"] - 0.55) < 1e-6
    assert abs(entry["duration"] - 1.0) < 1e-6


def test_map_boundaries_letter_alias_spaces_stripped():
    # Azure drops the spaces in "M O E" and emits 'M','O','E'.
    wbs = [
        _wb("三十五", 0.0, 0.5), _wb("B", 0.5, 0.3),
        _wb(" ", 0.8, 0.05),
        _wb("M", 0.85, 0.3), _wb("O", 1.15, 0.3), _wb("E", 1.45, 0.3),
        _wb("，", 1.75, 0.1),
    ]
    pairs = [("三十五B", "35B"), ("M O E", "MoE")]
    out = lite_tts.map_boundaries_to_display(wbs, pairs)
    texts = [w["text"] for w in out]
    assert texts == ["35B", " ", "MoE", "，"]


def test_map_boundaries_unmatched_pair_keeps_spoken(capsys):
    wbs = [_wb("你好", 0.0, 0.5)]
    out = lite_tts.map_boundaries_to_display(wbs, [("不存在", "X")])
    assert [w["text"] for w in out] == ["你好"]
    assert "未命中" in capsys.readouterr().out
