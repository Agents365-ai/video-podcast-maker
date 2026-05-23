"""Voice advisor — recommend the best Azure voice for given content.

Multilingual voices (e.g. zh-CN-XiaoxiaoMultilingualNeural) switch the synthesis
engine to English mode whenever the SSML wraps a token in <lang xml:lang="en-US">.
This switch produces vocoder artifacts at certain Chinese-prosody → English-vowel
→ Chinese-consonant transitions (a known deterministic glitch). It also has
weaker SAPI phoneme support for zh-CN.

The standard zh-CN-XiaoxiaoNeural voice handles bare English abbreviations
(AI, ML, GPT, CLI) by reading them as Chinese-letter pronunciations (ei-ai,
em-el, gee-pee-tee), which is exactly how Chinese speakers naturally pronounce
them in conversation. No language switch, no artifacts, full phoneme support.

Use Multilingual ONLY when the script contains substantial English passages or
proper nouns that genuinely need English pronunciation (e.g. heavy SDK/code
content where pronouncing "Visual Studio Code" as Chinese letters would sound
wrong).
"""
import re


# Bare English abbreviations that Chinese speakers typically read as letters
# (no language switch needed — Xiaoxiao reads them naturally in zh-CN context)
COMMON_ABBREVS = {
    'AI', 'ML', 'LLM', 'GPT', 'CLI', 'API', 'SDK', 'IDE', 'OS', 'PC',
    'IOS', 'URL', 'HTML', 'CSS', 'JS', 'TS', 'SQL', 'DB', 'CDN', 'DNS',
    'HTTP', 'HTTPS', 'TCP', 'IP', 'CPU', 'GPU', 'RAM', 'SSD', 'HDD',
    'JSON', 'XML', 'CSV', 'YAML', 'PR', 'CI', 'CD', 'UI', 'UX', 'QA',
    'KPI', 'ROI', 'B2B', 'B2C', 'CEO', 'CTO', 'CFO', 'HR',
}


def analyse_content(text):
    """Scan text and return a dict of metrics + voice recommendation."""
    cn_chars = len(re.findall(r'[一-鿿]', text))

    # Find all English tokens (≥2 letters)
    en_tokens = re.findall(r'\b[A-Za-z][A-Za-z0-9\-]*[A-Za-z0-9]\b', text)

    bare_abbrev_count = 0
    multi_word_phrases = 0
    long_english_words = 0  # ≥5 letters (likely needs real English pronunciation)
    code_like = 0  # contains digits or hyphens

    for tok in en_tokens:
        if tok.upper() in COMMON_ABBREVS:
            bare_abbrev_count += 1
        elif re.search(r'[0-9\-]', tok):
            code_like += 1
        elif len(tok) >= 5:
            long_english_words += 1
        # else: short English word (treated as borderline)

    # Multi-word phrases: count groups of consecutive english tokens separated by space
    multi_word_matches = re.findall(r'\b[A-Za-z]+(?:\s+[A-Za-z]+)+\b', text)
    multi_word_phrases = len(multi_word_matches)

    total_en_complexity = long_english_words + code_like + multi_word_phrases * 2

    # Recommendation logic:
    # - English-heavy or technical → Multilingual
    # - Mostly Chinese with abbreviations → Standard
    if cn_chars == 0:
        recommendation = 'multilingual'
        reason = 'No Chinese content detected — use Multilingual or English voice'
    elif total_en_complexity >= 8 or total_en_complexity / max(cn_chars, 1) > 0.02:
        recommendation = 'multilingual'
        reason = f'{total_en_complexity} complex English tokens (long words / multi-word phrases / code) — Multilingual handles them better'
    else:
        recommendation = 'standard'
        reason = (f'Mostly Chinese ({cn_chars} chars) with {bare_abbrev_count} bare abbreviations — '
                  'standard zh-CN voice avoids language-switch artifacts')

    return {
        'cn_chars': cn_chars,
        'en_tokens': len(en_tokens),
        'bare_abbreviations': bare_abbrev_count,
        'long_english_words': long_english_words,
        'multi_word_phrases': multi_word_phrases,
        'code_like': code_like,
        'recommendation': recommendation,
        'reason': reason,
    }


VOICE_MAP = {
    'standard': 'zh-CN-XiaoxiaoNeural',
    'multilingual': 'zh-CN-XiaoxiaoMultilingualNeural',
}


def print_advisory(text, current_voice):
    """Print a one-screen advisory based on content vs current voice choice."""
    metrics = analyse_content(text)
    suggested = VOICE_MAP[metrics['recommendation']]

    print("\n--- Voice Advisor ---")
    print(f"  Chinese chars: {metrics['cn_chars']}")
    print(f"  English tokens: {metrics['en_tokens']} "
          f"(abbrev: {metrics['bare_abbreviations']}, "
          f"long words: {metrics['long_english_words']}, "
          f"multi-word: {metrics['multi_word_phrases']}, "
          f"code-like: {metrics['code_like']})")
    print(f"  Recommended: {suggested}")
    print(f"  Reason: {metrics['reason']}")

    if current_voice and 'Multilingual' in current_voice and metrics['recommendation'] == 'standard':
        print(f"  ⚠️  Current voice is Multilingual but content does not require it.")
        print(f"      Consider switching to {suggested} via AZURE_TTS_VOICE env var.")
        print(f"      Multilingual is known to produce vocoder artifacts at certain")
        print(f"      Chinese-tone → English-letter transitions (e.g. '是，AI让...').")
    elif current_voice and 'Multilingual' not in current_voice and metrics['recommendation'] == 'multilingual':
        print(f"  ⚠️  Current voice is standard but content has substantial English.")
        print(f"      Consider switching to {suggested} for better English pronunciation.")
    return metrics
