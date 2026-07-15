"""Backend-neutral expressiveness markers for narration scripts.

Scripts may contain:
  [PAUSE:0.8]     — a pause in seconds (0.01-99.99)
  (chuckle) etc.  — MiniMax sound tags: laughs, chuckle, sighs, breath,
                    inhale, exhale, coughs (speech-2.8 models only)

Markers ride RAW through the ttsCN bridge — ttsCN renders or strips them
per platform. vpm only needs strip_markers here, for subtitle/boundary
estimation, section matching, and chunk-length accounting.

[PAUSE:x] contains a '.' which the sentence chunker treats as a boundary —
protect_pauses()/restore_pauses() swap the dot out around chunk_text().
"""
import re

PAUSE_RE = re.compile(r"\[PAUSE:(\d{1,2}(?:\.\d{1,2})?)\]")
# Dot swapped for 'p' so the chunker never splits inside a marker
_PROTECTED_PAUSE_RE = re.compile(r"\[PAUSE:(\d{1,2}(?:p\d{1,2})?)\]")

SOUND_TAGS = ("laughs", "chuckle", "sighs", "breath", "inhale", "exhale", "coughs")
SOUND_TAG_RE = re.compile(r"\((?:%s)\)" % "|".join(SOUND_TAGS))


def protect_pauses(text):
    """Make [PAUSE:x] chunker-safe ('.' -> 'p'). Inverse: restore_pauses."""
    return PAUSE_RE.sub(lambda m: "[PAUSE:%s]" % m.group(1).replace(".", "p"), text)


def restore_pauses(text):
    return _PROTECTED_PAUSE_RE.sub(
        lambda m: "[PAUSE:%s]" % m.group(1).replace("p", "."), text)


def strip_markers(text):
    """Remove all markers — for subtitles, boundary estimation, section matching."""
    text = PAUSE_RE.sub("", text)
    return SOUND_TAG_RE.sub("", text)
