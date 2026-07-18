"""Chinese phoneme (多音字) dictionary loading for TTS.

vpm only loads/merges phoneme dictionaries and extracts inline annotations;
the merged dict is written to a file and passed to ttsCN via --phonemes,
which applies it per platform (azure SSML <phoneme>, minimax pinyin).
"""
import os
import re
import json
import tempfile


def _atomic_write_json(data, path):
    """Write JSON via a unique temp file + os.replace so concurrent
    sessions never read a truncated/interleaved file."""
    fd, tmp_path = tempfile.mkstemp(
        dir=os.path.dirname(os.path.abspath(path)), suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        os.replace(tmp_path, path)
    except BaseException:
        os.unlink(tmp_path)
        raise


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

    # Auto-create or merge phonemes.json from template (atomic writes so a
    # concurrent session in another project never reads a partial file)
    if os.path.exists(template_path):
        if not os.path.exists(global_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                _atomic_write_json(json.load(f), global_path)
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
                _atomic_write_json(user_data, global_path)
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
