"""Chinese phoneme (多音字) processing for TTS."""
import os
import re
import json


def load_phoneme_dicts(input_file, phoneme_file=None):
    """Load and merge phoneme dictionaries (global + project-level)

    Priority (highest to lowest):
    1. Explicit --phonemes argument (replaces project-level)
    2. Project-level: videos/{name}/phonemes.json (same dir as input)
    3. Global: phonemes.json in skill root directory

    Global and project-level are merged; project entries override global.
    """
    # scripts/tts/phonemes.py → skill root is three levels up
    SKILL_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    global_path = os.path.join(SKILL_DIR, 'phonemes.json')
    template_path = os.path.join(SKILL_DIR, 'phonemes.template.json')
    project_path = os.path.join(os.path.dirname(os.path.abspath(input_file)), 'phonemes.json')

    # Auto-create or merge phonemes.json from template
    if os.path.exists(template_path):
        if not os.path.exists(global_path):
            import shutil
            shutil.copy2(template_path, global_path)
            print(f"✓ Created phonemes.json from template")
        else:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_data = {k: v for k, v in json.load(f).items() if not k.startswith('_')}
            with open(global_path, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
            user_entries = {k: v for k, v in user_data.items() if not k.startswith('_')}
            new_entries = {k: v for k, v in template_data.items() if k not in user_entries}
            if new_entries:
                user_data.update(new_entries)
                with open(global_path, 'w', encoding='utf-8') as f:
                    json.dump(user_data, f, ensure_ascii=False, indent=4)
                print(f"✓ Merged {len(new_entries)} new entries from template into phonemes.json")

    merged = {}

    if os.path.exists(global_path):
        with open(global_path, 'r', encoding='utf-8') as f:
            data = {k: v for k, v in json.load(f).items() if not k.startswith('_')}
            merged.update(data)
            print(f"Global phoneme dictionary: {global_path} ({len(data)} entries)")

    override_path = phoneme_file if phoneme_file else project_path
    if override_path and os.path.exists(override_path):
        with open(override_path, 'r', encoding='utf-8') as f:
            data = {k: v for k, v in json.load(f).items() if not k.startswith('_')}
            merged.update(data)
            print(f"Project phoneme dictionary: {override_path} ({len(data)} entries)")

    return merged


def extract_inline_phonemes(text):
    """Extract inline phoneme markers from text: 执行器[zhí xíng qì]

    The regex greedily captures every Chinese character before '[', but only
    the last N chars (where N = pinyin syllable count, since Chinese is one
    char per syllable) are treated as the annotated word. Any extra Chinese
    prefix is left intact in the clean text.

    Example: "每个执行器[zhí xíng qì]" → key "执行器" (3 syllables → last 3 chars),
    clean text "每个执行器". Without this rule the greedy run would wrongly
    attach "每个" to the phoneme tag and produce 5-char text under a 3-syllable
    SSML wrapper, which TTS engines mispronounce.

    Returns: (clean_text, phoneme_dict)
    """
    pattern = r'([\u4e00-\u9fff]+)\[([a-zA-Zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜü\s]+)\]'
    phonemes = {}

    def extract(m):
        preceding = m.group(1)
        pinyin = m.group(2).strip()
        syllables = len(pinyin.split())
        if syllables == 0:
            return m.group(0)  # degenerate — leave untouched
        if syllables >= len(preceding):
            word = preceding
            prefix = ""
        else:
            word = preceding[-syllables:]
            prefix = preceding[:-syllables]
        phonemes[word] = pinyin
        return prefix + word

    clean = re.sub(pattern, extract, text)
    return clean, phonemes


def pinyin_to_sapi(pinyin):
    """Convert pinyin with tone marks to SAPI format with numeric tones.

    Example: "zhí xíng qì" -> "zhi 2 xing 2 qi 4"
    """
    tone_map = {
        'ā': ('a', '1'), 'á': ('a', '2'), 'ǎ': ('a', '3'), 'à': ('a', '4'),
        'ē': ('e', '1'), 'é': ('e', '2'), 'ě': ('e', '3'), 'è': ('e', '4'),
        'ī': ('i', '1'), 'í': ('i', '2'), 'ǐ': ('i', '3'), 'ì': ('i', '4'),
        'ō': ('o', '1'), 'ó': ('o', '2'), 'ǒ': ('o', '3'), 'ò': ('o', '4'),
        'ū': ('u', '1'), 'ú': ('u', '2'), 'ǔ': ('u', '3'), 'ù': ('u', '4'),
        'ǖ': ('v', '1'), 'ǘ': ('v', '2'), 'ǚ': ('v', '3'), 'ǜ': ('v', '4'), 'ü': ('v', '5'),
    }

    syllables = pinyin.split()
    result = []

    for syllable in syllables:
        tone = '5'
        converted = ''
        for char in syllable:
            if char in tone_map:
                base, t = tone_map[char]
                converted += base
                tone = t
            else:
                converted += char
        result.append(f"{converted} {tone}")

    return ' '.join(result)


def apply_phonemes(text, phoneme_dict):
    """Apply SSML phoneme tags for multi-character words.

    Uses SAPI alphabet with numeric tones for Azure TTS compatibility.
    """
    if not phoneme_dict:
        return text

    sorted_words = sorted(phoneme_dict.keys(), key=len, reverse=True)
    placeholders = {}
    result = text

    for i, word in enumerate(sorted_words):
        if word not in result:
            continue
        placeholder = f"__PH_{i}__"
        placeholders[placeholder] = (word, phoneme_dict[word])
        result = result.replace(word, placeholder)

    for placeholder, (word, pinyin) in placeholders.items():
        sapi_pinyin = pinyin_to_sapi(pinyin)
        phoneme_tag = f'<phoneme alphabet="sapi" ph="{sapi_pinyin}">{word}</phoneme>'
        result = result.replace(placeholder, phoneme_tag)

    return result


def apply_phonemes_minimax(text, phoneme_dict):
    """Annotate polyphonic words with MiniMax pinyin syntax: 重(chong2)庆(qing4).

    MiniMax (speech-2.x) reads a parenthesized numbered-pinyin annotation
    placed directly after a character. Each dict word is expanded to per-char
    annotations; entries whose syllable count doesn't match the character
    count are skipped (fail-safe: default pronunciation). Longest-first with
    placeholders, mirroring apply_phonemes().
    """
    if not phoneme_dict:
        return text

    sorted_words = sorted(phoneme_dict.keys(), key=len, reverse=True)
    placeholders = {}
    result = text

    for i, word in enumerate(sorted_words):
        syllables = phoneme_dict[word].split()
        if len(syllables) != len(word) or word not in result:
            continue
        placeholder = f"__PHM_{i}__"
        annotated = "".join(
            f"{char}({pinyin_to_sapi(syl).replace(' ', '')})"
            for char, syl in zip(word, syllables))
        placeholders[placeholder] = annotated
        result = result.replace(word, placeholder)

    for placeholder, annotated in placeholders.items():
        result = result.replace(placeholder, annotated)

    return result
