"""Tests for tts.sections — section parsing, validation, time matching."""
from tts.sections import parse_sections, validate_sections, match_section_times


# ---------- parse_sections ----------


def test_parse_sections_basic():
    text = """[SECTION:hero]
你好，欢迎收听本期播客。

[SECTION:content]
今天聊聊人工智能。

[SECTION:outro]
"""
    sections, matches, clean = parse_sections(text)
    assert [s["name"] for s in sections] == ["hero", "content", "outro"]
    assert sections[0]["label"] == "你好"
    assert sections[1]["label"] == "今天聊聊人工智能"
    assert sections[0]["is_silent"] is False
    assert sections[2]["is_silent"] is True
    assert "[SECTION:" not in clean


def test_parse_sections_no_markers():
    sections, matches, clean = parse_sections("just some text with no markers")
    assert sections == []
    assert matches == []
    assert clean == "just some text with no markers"


def test_parse_sections_silent_section():
    """A section with only whitespace content must be marked silent."""
    text = "[SECTION:outro]\n\n   \n"
    sections, _, _ = parse_sections(text)
    assert len(sections) == 1
    assert sections[0]["is_silent"] is True
    assert sections[0]["label"] == "outro"  # falls back to section name


def test_parse_sections_label_truncation():
    """Label is truncated at first punctuation, max 10 chars."""
    text = "[SECTION:hero]\n这是一段很长的开场白没有标点的话会被截断到十个字符为止是不是\n"
    sections, _, _ = parse_sections(text)
    assert len(sections[0]["label"]) <= 10


def test_parse_sections_first_text_stripped():
    """first_text collapses whitespace across multiple lines."""
    text = "[SECTION:hero]\nline one\n  line two  \n"
    sections, _, _ = parse_sections(text)
    assert " " not in sections[0]["first_text"]


# ---------- validate_sections ----------


def test_validate_clean_input():
    text = "[SECTION:hero]\nhello\n[SECTION:outro]\n"
    sections, matches, _ = parse_sections(text)
    errors, warnings = validate_sections(text, sections, matches)
    assert errors == []
    # Silent outro section should NOT warn (it's in the whitelist)
    assert warnings == []


def test_validate_no_sections_errors():
    text = "just plain text"
    sections, matches, _ = parse_sections(text)
    errors, warnings = validate_sections(text, sections, matches)
    assert any("No [SECTION:xxx]" in e for e in errors)


def test_validate_malformed_marker_detected():
    text = "[SECTION :hero]\ncontent\n"  # space after SECTION
    sections, matches, _ = parse_sections(text)
    errors, _ = validate_sections(text, sections, matches)
    assert any("Malformed" in e for e in errors)


def test_validate_duplicate_section_names():
    text = "[SECTION:hero]\na\n[SECTION:hero]\nb\n"
    sections, matches, _ = parse_sections(text)
    errors, _ = validate_sections(text, sections, matches)
    assert any("Duplicate" in e for e in errors)


def test_validate_silent_non_outro_warns():
    """A silent middle section should produce a warning (not an error)."""
    text = "[SECTION:hero]\nhello\n[SECTION:middle]\n\n[SECTION:outro]\n"
    sections, matches, _ = parse_sections(text)
    _, warnings = validate_sections(text, sections, matches)
    assert any("middle" in w and "silent" in w for w in warnings)


def test_validate_preface_content_warns():
    text = "stuff before\n[SECTION:hero]\nhello\n"
    sections, matches, _ = parse_sections(text)
    _, warnings = validate_sections(text, sections, matches)
    assert any("before first section" in w for w in warnings)


# ---------- match_section_times ----------


def _wb(text, offset):
    return {"text": text, "offset": offset}


def test_match_single_section():
    sections = [{"name": "main", "first_text": "", "start_time": 0, "end_time": None, "is_silent": False}]
    out = match_section_times(sections, [], 10.0)
    assert out[0]["start_time"] == 0
    assert out[0]["end_time"] == 10.0
    assert out[0]["duration"] == 10.0


def test_match_with_word_boundaries_exact_hit():
    sections = [
        {"name": "hero", "first_text": "欢迎收听本期播客今天聊聊", "start_time": None, "end_time": None, "is_silent": False},
        {"name": "content", "first_text": "Claude是一个强大的AI助手", "start_time": None, "end_time": None, "is_silent": False},
    ]
    # word boundaries simulate TTS output chronologically
    wbs = [
        _wb("欢迎", 0.0), _wb("收听", 0.5), _wb("本期", 1.0), _wb("播客", 1.5),
        _wb("今天", 2.0), _wb("聊聊", 2.5),
        _wb("Claude", 3.0), _wb("是", 3.3), _wb("一个", 3.6),
        _wb("强大", 4.0), _wb("的", 4.2), _wb("AI", 4.4), _wb("助手", 4.6),
    ]
    out = match_section_times(sections, wbs, 5.0)
    assert out[0]["start_time"] == 0
    # content section should be detected around offset 3.0s (where "Claude" appears)
    assert out[1]["start_time"] == 3.0
    assert out[0]["end_time"] == 3.0
    assert out[1]["end_time"] == 5.0


def test_match_fallback_when_not_found():
    """When first_text can't be located, fall back to proportional estimation."""
    sections = [
        {"name": "hero", "first_text": "aaa", "start_time": None, "end_time": None, "is_silent": False},
        {"name": "content", "first_text": "totally_different_text_nowhere_in_wb", "start_time": None, "end_time": None, "is_silent": False},
    ]
    wbs = [_wb("aaa", 0.0), _wb("bbb", 1.0)]
    out = match_section_times(sections, wbs, 10.0)
    # content estimated somewhere in the second half, not None
    assert out[1]["start_time"] is not None
    assert out[1]["start_time"] > 0


def test_match_trailing_silent_section_gets_total_duration():
    sections = [
        {"name": "hero", "first_text": "欢迎", "start_time": None, "end_time": None, "is_silent": False},
        {"name": "outro", "first_text": "", "start_time": None, "end_time": None, "is_silent": True},
    ]
    wbs = [_wb("欢迎", 0.0), _wb("大家", 1.0)]
    out = match_section_times(sections, wbs, 5.0)
    assert out[1]["start_time"] == 5.0
    assert out[1]["end_time"] == 5.0
    assert out[1]["duration"] == 0
    # hero section end_time should extend to total_duration because outro is silent trailing
    assert out[0]["end_time"] == 5.0


def test_match_resume_mode_no_word_boundaries():
    """With no word_boundaries (e.g., resumed session), sections are estimated proportionally."""
    sections = [
        {"name": "a", "first_text": "x", "start_time": None, "end_time": None, "is_silent": False},
        {"name": "b", "first_text": "y", "start_time": None, "end_time": None, "is_silent": False},
        {"name": "c", "first_text": "z", "start_time": None, "end_time": None, "is_silent": False},
    ]
    out = match_section_times(sections, [], 9.0)
    # Three non-silent sections, 9s total → 3s each
    assert out[0]["start_time"] == 0
    assert abs(out[0]["duration"] - 3.0) < 0.01
    assert abs(out[2]["end_time"] - 9.0) < 0.01
