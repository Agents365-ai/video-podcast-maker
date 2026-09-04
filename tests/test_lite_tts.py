"""Tests for the lite skill's tts.py — pure functions only, no network.

The lite script is loaded by file path (its module name `tts` would clash
with the full skill's scripts/tts package on sys.path).
"""
import importlib.util
import os

import pytest

LITE_TTS = os.path.join(
    os.path.dirname(__file__), os.pardir,
    "skills", "video-podcast-maker-lite", "scripts", "tts.py",
)

spec = importlib.util.spec_from_file_location("lite_tts", LITE_TTS)
lite_tts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lite_tts)


# ---------------------------------------------------------------------------
# parse_sections
# ---------------------------------------------------------------------------

def test_parse_sections_basic():
    text = (
        "# comment line\n"
        "[SECTION:hero]\n# a hint, not narration\n你好世界。\n\n"
        "[SECTION:content-1]\n第一点。\n"
        "[SECTION:outro]\n谢谢观看。\n"
    )
    sections = lite_tts.parse_sections(text)
    assert [s["name"] for s in sections] == ["hero", "content-1", "outro"]
    # Comment lines are stripped from narration text
    assert sections[0]["text"] == "你好世界。"
    assert sections[1]["text"] == "第一点。"
    # Label derives from the first sentence of the section
    assert sections[0]["label"] == "你好世界"


def test_parse_sections_ignores_markers_in_comments():
    # A comment line mentioning a literal marker must not create a section.
    text = "# 每个 [SECTION:xxx] 是一个片段\n[SECTION:hero]\n你好。\n"
    sections = lite_tts.parse_sections(text)
    assert [s["name"] for s in sections] == ["hero"]


def test_parse_sections_explicit_label():
    text = "[SECTION:outro|感谢观看]\n好了，今天的内容就到这里。\n"
    sections = lite_tts.parse_sections(text)
    assert sections[0]["label"] == "感谢观看"
    # Explicit label must not leak into narration text
    assert sections[0]["text"] == "好了，今天的内容就到这里。"


def test_parse_sections_no_markers():
    with pytest.raises(ValueError, match=r"No \[SECTION"):
        lite_tts.parse_sections("没有任何标记的稿子。")


def test_parse_sections_duplicate_names():
    text = "[SECTION:a]\n第一节。\n[SECTION:a]\n重复了。\n"
    with pytest.raises(ValueError, match="Duplicate"):
        lite_tts.parse_sections(text)


def test_parse_sections_empty_section():
    text = "[SECTION:a]\n第一节。\n[SECTION:b]\n# only a comment\n"
    with pytest.raises(ValueError, match="no narration"):
        lite_tts.parse_sections(text)


# ---------------------------------------------------------------------------
# build_ssml
# ---------------------------------------------------------------------------

def test_build_ssml_minimal_no_wrappers():
    ssml = lite_tts.build_ssml("你好。", "zh-CN-XiaoxiaoNeural")
    assert ssml.startswith('<speak version="1.0"')
    assert 'xmlns:mstts="https://www.w3.org/2001/mstts"' in ssml
    assert '<voice name="zh-CN-XiaoxiaoNeural">你好。</voice>' in ssml
    assert "express-as" not in ssml
    assert "prosody" not in ssml


def test_build_ssml_escapes_special_chars():
    ssml = lite_tts.build_ssml("A & B <tag>", "v")
    assert "A &amp; B &lt;tag&gt;" in ssml
    assert "<tag>" not in ssml


def test_build_ssml_style_and_rate_wrappers():
    ssml = lite_tts.build_ssml("你好", "v", style="gentle", rate="-4%")
    assert '<mstts:express-as style="gentle">' in ssml
    assert '<prosody rate="-4%">' in ssml
    # prosody sits inside express-as
    assert ssml.index("express-as") < ssml.index("prosody")


# ---------------------------------------------------------------------------
# merge_boundaries (punctuation re-insertion, azure ticks -> seconds)
# ---------------------------------------------------------------------------

def test_merge_boundaries_reinserts_punctuation():
    text = "你好，世界。"
    # edge-tts reports only spoken tokens, in 100ns ticks.
    raw = [
        {"offset": 0, "duration": 5_000_000, "text": "你好"},      # 0.0-0.5s
        {"offset": 6_000_000, "duration": 5_000_000, "text": "世界"},  # 0.6-1.1s
    ]
    merged = lite_tts.merge_boundaries(text, raw, base_offset=0.0)
    texts = [b["text"] for b in merged]
    assert texts == ["你好", "，", "世界", "。"]
    # Spoken tokens keep their real timings (converted to seconds)
    assert merged[0]["offset"] == 0.0
    assert merged[0]["duration"] == 0.5
    assert merged[2]["offset"] == 0.6
    # Punctuation anchors to the previous token's end with a tiny duration
    assert merged[1]["offset"] == 0.5
    assert merged[1]["duration"] == 0.01


def test_merge_boundaries_applies_base_offset():
    raw = [{"offset": 1_000_000, "duration": 2_000_000, "text": "你好"}]
    merged = lite_tts.merge_boundaries("你好", raw, base_offset=10.0)
    assert merged[0]["offset"] == pytest.approx(10.1)
    assert merged[0]["duration"] == pytest.approx(0.2)


def test_merge_boundaries_accepts_punctuation_tokens():
    # Azure reports punctuation as its own boundary tokens — the walk must
    # pass them through at their real offsets, not duplicate them.
    text = "你好，世界。"
    raw = [
        {"offset": 0, "duration": 5_000_000, "text": "你好"},
        {"offset": 5_000_000, "duration": 1_000_000, "text": "，"},
        {"offset": 6_000_000, "duration": 5_000_000, "text": "世界"},
        {"offset": 11_000_000, "duration": 1_000_000, "text": "。"},
    ]
    merged = lite_tts.merge_boundaries(text, raw, base_offset=0.0)
    assert [b["text"] for b in merged] == ["你好", "，", "世界", "。"]
    assert merged[1]["offset"] == 0.5
    assert merged[1]["duration"] == 0.1


# ---------------------------------------------------------------------------
# build_cues (word boundaries -> subtitle cues)
# ---------------------------------------------------------------------------

def _char_boundaries(text, start=0.0, per_char=0.2):
    """Fake word boundaries: one entry per character."""
    return [
        {"text": ch, "offset": start + i * per_char, "duration": per_char}
        for i, ch in enumerate(text)
    ]


def test_build_cues_breaks_at_strong_punctuation():
    # First sentence reaches >= 10 chars at 。 → break right after it.
    boundaries = _char_boundaries("这是第一句话已经够长了。然后第二句。")
    cues = lite_tts.build_cues(boundaries)
    assert len(cues) == 2
    assert cues[0][2] == "这是第一句话已经够长了"
    assert cues[1][2] == "然后第二句"


def test_build_cues_strips_edge_punctuation():
    boundaries = _char_boundaries("你好世界。")
    cues = lite_tts.build_cues(boundaries)
    assert cues[0][2] == "你好世界"


def test_build_cues_force_break_backtracks_to_punctuation():
    # > 40 chars, a comma mid-way, no strong punctuation until the end.
    text = "这是一个非常非常长的分句用来撑长度，接着继续写更多的内容直到超过四十个字符才会断。"
    assert len(text) > 40
    cues = lite_tts.build_cues(_char_boundaries(text))
    assert len(cues) == 2
    # Forced break backtracks to the comma rather than cutting mid-phrase
    assert cues[0][2].endswith("撑长度")
    assert all(len(c[2]) <= 40 for c in cues)


def test_build_cues_timings_span_whole_cue():
    boundaries = _char_boundaries("你好世界。", start=1.0, per_char=0.5)
    cues = lite_tts.build_cues(boundaries)
    start, end, _ = cues[0]
    assert start == 1.0
    # 5 chars x 0.5s; the trailing 。 entry is 0.5s long as well here
    assert end == pytest.approx(1.0 + 5 * 0.5)


def test_build_cues_empty():
    assert lite_tts.build_cues([]) == []


# ---------------------------------------------------------------------------
# render_srt / format_srt_time
# ---------------------------------------------------------------------------

def test_render_srt_format():
    srt = lite_tts.render_srt([(0.0, 1.5, "你好"), (61.25, 62.0, "世界")])
    assert srt == (
        "1\n00:00:00,000 --> 00:00:01,500\n你好\n\n"
        "2\n00:01:01,250 --> 00:01:02,000\n世界\n\n"
    )


def test_format_srt_time_rounding_carry():
    # 1.9999s must not produce "00:00:01,1000"
    assert lite_tts.format_srt_time(1.9999) == "00:00:02,000"


# ---------------------------------------------------------------------------
# build_timing
# ---------------------------------------------------------------------------

def test_build_timing_frames_and_offsets():
    sections = [
        {"name": "hero", "label": "开场", "text": "…"},
        {"name": "outro", "label": "结尾", "text": "…"},
    ]
    timing = lite_tts.build_timing(sections, [2.0, 3.0], total_duration=5.0)
    assert timing["fps"] == 30
    assert timing["total_frames"] == 150
    hero, outro = timing["sections"]
    assert hero["start_time"] == 0.0
    assert hero["duration_frames"] == 60
    assert outro["start_time"] == 2.0
    assert outro["start_frame"] == 60
    assert outro["end_time"] == 5.0


# ---------------------------------------------------------------------------
# pinyin_to_sapi / apply_phonemes / load_phoneme_dict (pronunciation fixes)
# ---------------------------------------------------------------------------

def test_pinyin_to_sapi_tone_marks():
    assert lite_tts.pinyin_to_sapi("tóng háng") == "tong 2 hang 2"
    assert lite_tts.pinyin_to_sapi("mìng lìng háng") == "ming 4 ling 4 hang 2"


def test_pinyin_to_sapi_neutral_tone_and_u_umlaut():
    assert lite_tts.pinyin_to_sapi("le") == "le 5"
    assert lite_tts.pinyin_to_sapi("lǚ xíng") == "lv 3 xing 2"


def test_apply_phonemes_wraps_word():
    out = lite_tts.apply_phonemes("在命令行里干活", {"命令行": "mìng lìng háng"})
    assert out == '在<phoneme alphabet="sapi" ph="ming 4 ling 4 hang 2">命令行</phoneme>里干活'


def test_apply_phonemes_longest_first_no_nesting():
    # "一行命令" must win over "一行"; the longer tag must not be re-matched.
    out = lite_tts.apply_phonemes(
        "跑一行命令", {"一行": "yì háng", "一行命令": "yì háng mìng lìng"}
    )
    assert out.count("<phoneme") == 1
    assert 'ph="yi 4 hang 2 ming 4 ling 4"' in out


def test_apply_phonemes_empty_dict_passthrough():
    assert lite_tts.apply_phonemes("你好", {}) == "你好"


def test_build_ssml_phoneme_tag_survives_escaping():
    ssml = lite_tts.build_ssml("A & B 命令行", "v", phonemes={"命令行": "mìng lìng háng"})
    assert '<phoneme alphabet="sapi" ph="ming 4 ling 4 hang 2">命令行</phoneme>' in ssml
    assert "A &amp; B" in ssml
    assert "&lt;phoneme" not in ssml


def test_load_phoneme_dict_skips_underscore_keys(tmp_path):
    p = tmp_path / "phonemes.json"
    p.write_text('{"_comment": "x", "同行": "tóng háng"}', encoding="utf-8")
    assert lite_tts.load_phoneme_dict("input.txt", str(p)) == {"同行": "tóng háng"}


def test_load_phoneme_dict_missing_returns_empty(tmp_path, monkeypatch):
    # No explicit file, none next to the input, and no global dict either.
    monkeypatch.setenv("HOME", str(tmp_path))
    assert lite_tts.load_phoneme_dict(str(tmp_path / "nope.txt")) == {}


def test_load_phoneme_dict_merges_global_and_per_video(tmp_path, monkeypatch):
    # Global dict in a fake HOME, per-video dict next to the input file.
    global_dir = tmp_path / "home" / ".video-podcast-maker"
    global_dir.mkdir(parents=True)
    (global_dir / "phonemes.json").write_text(
        '{"命令行": "mìng lìng háng", "同行": "tóng háng"}', encoding="utf-8"
    )
    video_dir = tmp_path / "videos" / "demo"
    video_dir.mkdir(parents=True)
    (video_dir / "phonemes.json").write_text(
        '{"整行": "zhěng háng", "同行": "tóng xíng override"}', encoding="utf-8"
    )
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    d = lite_tts.load_phoneme_dict(str(video_dir / "podcast.txt"))
    # Both sources present; per-video entry wins on conflict
    assert d["命令行"] == "mìng lìng háng"
    assert d["整行"] == "zhěng háng"
    assert d["同行"] == "tóng xíng override"
