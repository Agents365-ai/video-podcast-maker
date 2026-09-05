"""Tests for the native TTS backend (tts/backends/native.py) — pure functions.

The synthesis functions call network/SDK, so this covers only the routing table
and the pronunciation / boundary-mapping layer (ported from the lite skill). The
same expectations mirror tests/test_lite_pronounce.py and tests/test_lite_tts.py.
"""
import pytest

from tts.backends import (
    BACKENDS, get_synthesize_func, get_max_chars, init_backend,
    MissingEnvVarError, UnknownBackendError,
)
import tts.backends as backends
from tts.backends.native import (
    apply_phonemes, build_ssml, int_to_cn, map_boundaries_to_display,
    merge_boundaries, num_to_cn, pinyin_to_sapi, pronounce,
)


@pytest.fixture(autouse=True)
def no_user_prefs(monkeypatch):
    """Isolate voice resolution from any real user_prefs.json on this machine."""
    monkeypatch.setattr(backends, "user_prefs_get", lambda *k: None)
    monkeypatch.delenv("TTS_VOICE", raising=False)


# --- routing table --------------------------------------------------------

def test_registry_has_only_local_backends():
    assert set(BACKENDS) == {"edge", "azure"}
    assert BACKENDS["azure"]["env"] == ["AZURE_SPEECH_KEY"]
    assert BACKENDS["edge"]["env"] == []


def test_get_synthesize_func_returns_native():
    assert get_synthesize_func("edge").__module__ == "tts.backends.native"
    assert get_synthesize_func("azure").__module__ == "tts.backends.native"


def test_get_max_chars_flat_400():
    assert get_max_chars("edge") == 400
    assert get_max_chars("azure") == 400


def test_unknown_backend_raises():
    with pytest.raises(UnknownBackendError, match="Unknown backend"):
        init_backend("tencent")


def test_azure_requires_key(monkeypatch):
    monkeypatch.delenv("AZURE_SPEECH_KEY", raising=False)
    monkeypatch.delenv("TTS_VOICE", raising=False)
    with pytest.raises(MissingEnvVarError):
        init_backend("azure")


def test_edge_requires_no_key(monkeypatch):
    monkeypatch.delenv("TTS_VOICE", raising=False)
    config = init_backend("edge")
    assert config["platform"] == "edge"
    assert config["voice"] is None


# --- number conversion ----------------------------------------------------

def test_int_to_cn_common():
    cases = {
        0: "零", 19: "十九", 24: "二十四", 300: "三百", 350: "三百五十",
        397: "三百九十七", 1001: "一千零一", 1200: "一千二百",
        5600: "五千六百", 10005: "一万零五",
    }
    for n, want in cases.items():
        assert int_to_cn(n) == want, f"{n}: got {int_to_cn(n)}"


def test_num_to_cn_decimals():
    assert num_to_cn("86.1") == "八十六点一"
    assert num_to_cn("2.8") == "二点八"


# --- pronounce ------------------------------------------------------------

def test_pronounce_numbers_and_mixed_tokens():
    spoken, pairs = pronounce("跑分 86.1 分，9B 和 35B-A3B，破了 1200 万。")
    assert "八十六点一" in spoken
    assert "九B" in spoken
    assert "三十五B" in spoken
    assert "A三B" in spoken
    assert "一千二百" in spoken
    assert [d for _s, d in pairs] == ["86.1 分", "9B", "35B", "A3B", "1200 万"]


def test_pronounce_explicit_aliases_win():
    spoken, pairs = pronounce("35B MoE 和 FP8，基于 Qwen3.5。")
    assert "M O E" in spoken
    assert "F P 八" in spoken
    assert "千问三点五" in spoken


def test_pronounce_plain_text_untouched():
    spoken, pairs = pronounce("大家好，欢迎来到我的频道。")
    assert spoken == "大家好，欢迎来到我的频道。"
    assert pairs == []


# --- map_boundaries_to_display -------------------------------------------

def _wb(text, offset, duration):
    return {"text": text, "offset": offset, "duration": duration}


def test_map_boundaries_merges_spoken_run_into_display():
    wbs = [
        _wb("跑分", 0.0, 0.5), _wb(" ", 0.5, 0.05),
        _wb("八十", 0.55, 0.4), _wb("六点", 0.95, 0.4), _wb("一", 1.35, 0.2),
        _wb(" ", 1.55, 0.05), _wb("分", 1.6, 0.3),
    ]
    out = map_boundaries_to_display(wbs, [("八十六点一", "86.1")])
    texts = [w["text"] for w in out]
    assert "86.1" in texts
    assert "".join(texts) == "跑分 86.1 分"
    entry = next(w for w in out if w["text"] == "86.1")
    assert abs(entry["offset"] - 0.55) < 1e-6
    assert abs(entry["duration"] - 1.0) < 1e-6


def test_map_boundaries_unmatched_pair_keeps_spoken():
    out = map_boundaries_to_display([_wb("你好", 0.0, 0.5)], [("不存在", "X")])
    assert [w["text"] for w in out] == ["你好"]


# --- merge_boundaries (punctuation re-insertion, 100ns ticks -> seconds) ---

def test_merge_boundaries_reinserts_punctuation():
    text = "你好，世界。"
    raw = [
        {"offset": 0, "duration": 5_000_000, "text": "你好"},
        {"offset": 6_000_000, "duration": 5_000_000, "text": "世界"},
    ]
    merged = merge_boundaries(text, raw, base_offset=0.0)
    assert [b["text"] for b in merged] == ["你好", "，", "世界", "。"]
    assert merged[0]["offset"] == 0.0
    assert merged[0]["duration"] == 0.5
    assert merged[2]["offset"] == 0.6
    assert merged[1]["offset"] == 0.5
    assert merged[1]["duration"] == 0.01


def test_merge_boundaries_applies_base_offset():
    raw = [{"offset": 1_000_000, "duration": 2_000_000, "text": "你好"}]
    merged = merge_boundaries("你好", raw, base_offset=10.0)
    assert merged[0]["offset"] == pytest.approx(10.1)
    assert merged[0]["duration"] == pytest.approx(0.2)


# --- pinyin / SSML --------------------------------------------------------

def test_pinyin_to_sapi_tone_marks():
    assert pinyin_to_sapi("tóng háng") == "tong 2 hang 2"
    assert pinyin_to_sapi("lǚ xíng") == "lv 3 xing 2"


def test_apply_phonemes_wraps_word():
    out = apply_phonemes("在命令行里干活", {"命令行": "mìng lìng háng"})
    assert out == '在<phoneme alphabet="sapi" ph="ming 4 ling 4 hang 2">命令行</phoneme>里干活'


def test_build_ssml_minimal():
    ssml = build_ssml("你好。", "zh-CN-XiaoxiaoNeural")
    assert ssml.startswith('<speak version="1.0"')
    assert '<voice name="zh-CN-XiaoxiaoNeural">你好。</voice>' in ssml


def test_build_ssml_escapes_special_chars():
    ssml = build_ssml("A & B <tag>", "v")
    assert "A &amp; B &lt;tag&gt;" in ssml
    assert "<tag>" not in ssml
