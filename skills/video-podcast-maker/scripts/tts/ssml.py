"""SSML helpers for TTS — voice-aware and backend-aware English term wrapping.

Backend × voice → wrap mode policy:

  azure + standard zh-CN voice (Xiaoxiao Neural)   → 'multi_word_only'
  azure + Multilingual voice                       → 'aggressive'
  edge / cosyvoice / doubao / elevenlabs / openai / google → 'off'
                       (these backends do not consume SSML; any <lang>
                       tags would be escaped or spoken aloud)

The 'multi_word_only' default mirrors how Chinese listeners actually parse
mixed-language tech speech: bare abbreviations (AI, ML, GPT, CLI, API) are
naturally read as Chinese letter pronunciations ("ei-ai", "em-el"), and
forcing an English language switch on them produces vocoder artifacts on
Multilingual voices and unnecessary engine effort on standard voices.
Brand and proper-noun phrases (Visual Studio Code, Andrew Ng, Apple
Intelligence) still get wrapped because letter-by-letter Chinese reading
of them sounds wrong.
"""
import re
from xml.sax.saxutils import escape

from .voice_advisor import COMMON_ABBREVS


# Brand and proper-noun multi-word phrases that benefit from English
# pronunciation regardless of voice. Wrapped in both 'multi_word_only'
# and 'aggressive' modes. Order matters: longer phrases first so
# "Visual Studio Code" doesn't get partially eaten by "VS Code".
BRAND_PHRASES = [
    "Visual Studio Code",
    "Apple Intelligence",
    "Microsoft Edge",
    "Final Cut Pro",
    "Google Chrome",
    "Claude Code",
    "Andrew Ng",
    "VS Code",
    "Open AI",
    "OpenAI",
    "GPT-4",
    "GPT 4",
]

_LONG_WORD_MIN_LEN = 5


def mark_english_terms(text, mode='multi_word_only'):
    """Wrap English terms in SSML ``<lang xml:lang="en-US">`` tags by mode.

    Modes:
      ``'off'``
        Return text unchanged. Use for backends that do not consume SSML
        (edge, cosyvoice, doubao, elevenlabs, openai, google). Wrapping
        for these backends would either escape the tags or speak them
        aloud, so the safe action is to do nothing.

      ``'multi_word_only'`` (default)
        Wrap brand / proper-noun phrases in ``BRAND_PHRASES`` only.
        Recommended for standard zh-CN voices (Xiaoxiao Neural).

      ``'aggressive'``
        Wrap ``BRAND_PHRASES`` plus single English words that pass
        :func:`_should_wrap_single_token`. Recommended for Multilingual
        voice. Bare abbreviations still pass through unwrapped.

    Existing tags in the input (e.g. ``<phoneme>`` from phonemes.py) are
    preserved across all modes via NUL-byte placeholders so XML escape
    won't mangle them and ``\\b`` can fire at their edges.
    """
    if mode == 'off':
        return text
    if mode not in ('multi_word_only', 'aggressive'):
        raise ValueError(f"Unknown mark_english_terms mode: {mode!r}")

    # Preserve existing tags so escape() won't double-escape them.
    # NUL is non-word in regex so \b correctly fires at the placeholder edge,
    # letting English terms immediately after a tag (e.g. "</phoneme>API")
    # match. Digit-only inner content avoids the [A-Za-z]-anchored pattern.
    tags = []

    def save_tag(m):
        tags.append(m.group(0))
        return f'\x00{len(tags) - 1}\x00'

    text_with_placeholders = re.sub(r'<[^>]+>', save_tag, text)
    result = escape(text_with_placeholders)

    # Pass 1 — brand / proper-noun phrases (both wrap modes)
    for phrase in BRAND_PHRASES:
        escaped = escape(phrase)
        if escaped in result:
            result = result.replace(
                escaped, f'<lang xml:lang="en-US">{escaped}</lang>'
            )

    # Pass 2 — single tokens (aggressive mode only)
    if mode == 'aggressive':
        # re.ASCII so \b triggers between Chinese (Unicode \w) and Latin chars.
        # Without it, "调用API" leaves API unmatched because \b doesn't fire.
        pattern = r'\b[A-Za-z][A-Za-z0-9\-\.]*[A-Za-z0-9]\b|\b[A-Za-z]{2,}\b'
        for match in reversed(list(re.finditer(pattern, result, re.ASCII))):
            word = match.group(0)
            start, end = match.start(), match.end()
            before = result[:start]
            # Skip if inside an existing tag opening
            if before.rfind('<') > before.rfind('>'):
                continue
            # Skip if inside an already-wrapped <lang>
            if before.count('<lang xml:lang="en-US">') > before.count('</lang>'):
                continue
            if not _should_wrap_single_token(word):
                continue
            result = result[:start] + f'<lang xml:lang="en-US">{word}</lang>' + result[end:]

    # Restore original tags
    for i, tag in enumerate(tags):
        result = result.replace(f'\x00{i}\x00', tag)

    return result


def _should_wrap_single_token(word):
    """Heuristic for the 'aggressive' single-token pass.

    Wrap when the word is long enough and looks like a real English word
    rather than an abbreviation:
      - length >= ``_LONG_WORD_MIN_LEN`` (5)
      - contains at least one lowercase letter (acronyms like JSON, HTML,
        YAML, HTTPS are all-uppercase and skipped — Chinese voice reads
        them naturally letter-by-letter)
      - not in :data:`voice_advisor.COMMON_ABBREVS`

    Skip digits-only and short tokens. Skip all-uppercase tokens regardless
    of length (treated as acronyms, mirrors the abbreviation policy).
    """
    if word.isdigit() or len(word) < _LONG_WORD_MIN_LEN:
        return False
    if word.upper() in COMMON_ABBREVS:
        return False
    if word.isupper():
        return False
    return any(c.islower() for c in word)


def wrap_mode_for(backend, voice):
    """Return the recommended :func:`mark_english_terms` mode for a backend × voice.

    Reads ``BACKENDS[backend]['supports_ssml']`` so the backend matrix
    stays the single source of truth. Multilingual detection is by
    substring match on the voice name.
    """
    # Local import to avoid circular import at module load: backends/__init__
    # may import per-backend modules that import this module's helpers.
    from .backends import BACKENDS

    info = BACKENDS.get(backend)
    if not info or not info.get('supports_ssml'):
        return 'off'
    if voice and 'Multilingual' in voice:
        return 'aggressive'
    return 'multi_word_only'
