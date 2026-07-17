"""Tests for tts.phonemes — inline phoneme extraction."""
from tts.phonemes import extract_inline_phonemes


# ---------- extract_inline_phonemes ----------


def test_extract_single_marker():
    """Syllable count in pinyin decides how many preceding chars form the word.

    "每个执行器[zhí xíng qì]" has 3 syllables → key is the last 3 chars
    ("执行器"), not the full greedy Chinese run "每个执行器". Clean text still
    preserves the prefix "每个".
    """
    text = "每个执行器[zhí xíng qì]都有自己的窗口"
    clean, phonemes = extract_inline_phonemes(text)
    assert clean == "每个执行器都有自己的窗口"
    assert phonemes == {"执行器": "zhí xíng qì"}


def test_extract_single_marker_tight():
    """When the annotated word is preceded by punctuation, key is unambiguous."""
    text = "上下文，执行器[zhí xíng qì]处理请求"
    clean, phonemes = extract_inline_phonemes(text)
    assert phonemes == {"执行器": "zhí xíng qì"}


def test_extract_multiple_markers():
    """Each marker independently picks the last-N chars matching its syllables."""
    text = "执行器[zhí xíng qì]和重做[chóng zuò]都很常用"
    clean, phonemes = extract_inline_phonemes(text)
    assert "[" not in clean
    assert phonemes == {"执行器": "zhí xíng qì", "重做": "chóng zuò"}


def test_extract_preserves_prefix_in_clean_text():
    """Greedy Chinese run is split, but the prefix is not dropped — it stays in text."""
    text = "每个执行器[zhí xíng qì]"
    clean, _ = extract_inline_phonemes(text)
    assert clean == "每个执行器"


def test_extract_syllables_exceed_preceding_chars():
    """If pinyin has more syllables than available Chinese chars, take all chars."""
    text = "器[zhí xíng qì]"  # 1 char, 3 syllables
    _, phonemes = extract_inline_phonemes(text)
    assert phonemes == {"器": "zhí xíng qì"}


def test_extract_no_markers():
    text = "纯中文文本没有注音"
    clean, phonemes = extract_inline_phonemes(text)
    assert clean == text
    assert phonemes == {}


def test_extract_ignores_non_chinese_brackets():
    """[something] after ASCII should NOT be extracted as a phoneme."""
    text = "see file [abc] for details"
    clean, phonemes = extract_inline_phonemes(text)
    assert phonemes == {}
    assert clean == text
