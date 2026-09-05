"""Local TTS backends (azure SDK + edge-tts) — no external component skill.

vpm ships exactly two self-contained TTS backends. Both report native
word boundaries; the native-boundary platforms are: edge, azure.

  * edge   — edge-tts (free, no key) via the Azure edge endpoint (default)
  * azure  — Microsoft Speech SDK (needs AZURE_SPEECH_KEY / AZURE_SPEECH_REGION)

The former ttscn component skill dependency is removed: everything a video
needs to reach Step 9 is in-house now. (The multi-platform matrix that ttscn
provided — cosyvoice, doubao, tencent, baidu, minimax, xunfei, elevenlabs,
openai, google — is intentionally out of scope; the repo's public README
points users at ttsCN if they want those.)

The `synthesize()` contract matches the historical bridge:
    synthesize(chunks, config, output_dir, resume) -> (part_files, word_boundaries, total_duration)

`word_boundaries` is a flat list of {text, offset, duration} where text is the
DISPLAY text (Arabic digits, punctuation reinserted) — the same contract the
section matcher and write_srt consume, so subtitles and section timings stay
exact. The pronunciation layer (display -> spoken for the voice, then mapped
back to display for subtitles) is ported verbatim from the lite skill's tts.py.
"""

import asyncio
import json
import os
import re
import subprocess

from ..markers import strip_markers
from .base import check_resume

# ---------------------------------------------------------------------------
# Number conversion: Arabic digits -> Chinese reading for the spoken layer
# ---------------------------------------------------------------------------

_CN_DIGITS = "零一二三四五六七八九"
_CN_UNITS = ["", "十", "百", "千"]


def _four_to_cn(s):
    """1-4 digit string -> Chinese, e.g. '1200' -> 一千二百."""
    res = ""
    zero = False
    for i, ch in enumerate(s):
        d = int(ch)
        unit = _CN_UNITS[len(s) - 1 - i]
        if d == 0:
            if res:
                zero = True
            continue
        if zero:
            res += "零"
            zero = False
        res += _CN_DIGITS[d] + unit
    return res


def int_to_cn(n):
    """Integer -> Chinese reading, e.g. 5600 -> 五千六百, 19 -> 十九."""
    n = int(n)
    if n == 0:
        return "零"
    big = ["", "万", "亿", "万亿"]
    s = str(n)
    groups = []
    while s:
        groups.insert(0, s[-4:])
        s = s[:-4]
    parts = []
    for idx, g in enumerate(groups):
        val = int(g)
        if val == 0:
            continue
        if parts and val < 1000:
            parts.append("零")
        parts.append(_four_to_cn(g) + big[len(groups) - 1 - idx])
    res = "".join(parts)
    if res.startswith("一十"):
        res = res[1:]
    return res


def num_to_cn(s):
    """'86.1' -> 八十六点一, '5600' -> 五千六百."""
    if "." in s:
        ip, dp = s.split(".", 1)
        return int_to_cn(ip) + "点" + "".join(_CN_DIGITS[int(c)] for c in dp)
    return int_to_cn(s)


# ---------------------------------------------------------------------------
# Pronunciation layer: display -> spoken for the voice, remapped for subtitles
# ---------------------------------------------------------------------------

PRONUNCIATION_ALIASES = {
    "MoE": "M O E",
    "FP8": "F P 八",
    "Qwen": "千问",
    "Ornith-1.5": "Ornith 一点五",
    "1M": "一兆",
}

LETTER_WORD_ALIASES = {
    "qwen": "千问",
}

# Quantifier words glued to a spoken number ("10 倍" -> 十倍) so Azure keeps the
# number and its quantifier in one unit instead of pausing. Longest first.
_CN_QWORDS = (
    "美元",
    "小时",
    "分钟",
    "公斤",
    "公里",
    "万人",
    "亿人",
    "百万",
    "千万",
    "倍",
    "个",
    "层",
    "名",
    "分",
    "秒",
    "天",
    "月",
    "年",
    "岁",
    "元",
    "万",
    "亿",
    "点",
    "份",
    "位",
    "次",
    "条",
    "张",
    "件",
    "台",
    "只",
    "本",
    "套",
    "架",
    "批",
    "轮",
    "项",
    "组",
    "段",
    "页",
    "版",
    "款",
)

_CN_NUM_CHARS = "点十百千万亿零一二三四五六七八九"


def _mixed_token_to_spoken(token):
    """'9B' -> 九B, '35B' -> 三十五B, 'Qwen3.5' -> 千问三点五."""

    def repl(m: re.Match[str]) -> str:
        letters, digits = m.group(1), m.group(2)
        if letters:
            return LETTER_WORD_ALIASES.get(letters.lower(), letters)
        return num_to_cn(digits or "")

    return re.sub(r"([A-Za-z]+)|([0-9]+(?:\.[0-9]+)?)", repl, token)


_MIXED_TOKEN_RE = re.compile(r"[A-Za-z]*[0-9]+(?:\.[0-9]+)?[A-Za-z]*")


def pronounce(text, alias_dict=None):
    """Convert display text to the SPOKEN layer.

    Returns (spoken_text, pairs) where pairs is an ordered list of
    (spoken, display) for map_boundaries_to_display().
    """
    alias_dict = alias_dict if alias_dict is not None else PRONUNCIATION_ALIASES
    aliases = sorted(alias_dict, key=len, reverse=True)
    pairs = []
    out = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch.isascii() and ch.isalnum():
            hit = False
            for d in aliases:
                if text.startswith(d, i):
                    spoken = alias_dict[d]
                    out.append(spoken)
                    pairs.append((spoken, d))
                    i += len(d)
                    hit = True
                    break
            if hit:
                continue
            m = _MIXED_TOKEN_RE.match(text, i)
            if m:
                token = m.group(0)
                spoken = _mixed_token_to_spoken(token)
                end = m.end()
                if end < len(text) and spoken and spoken[-1] in _CN_NUM_CHARS:
                    j = end
                    while j < len(text) and text[j].isspace():
                        j += 1
                    matched = False
                    for w in _CN_QWORDS:
                        if text[j : j + len(w)] == w:
                            spoken = spoken + w
                            pairs.append((spoken, text[i : j + len(w)]))
                            out.append(spoken)
                            i = j + len(w)
                            matched = True
                            break
                    if matched:
                        continue
                if spoken != token:
                    pairs.append((spoken, token))
                out.append(spoken)
                i = m.end()
                continue
        out.append(ch)
        i += 1
    return "".join(out), pairs


def map_boundaries_to_display(word_boundaries, pairs):
    """Rewrite spoken-text word boundaries so subtitles show the display text.

    `pairs` is the ordered (spoken, display) list from pronounce(). The spoken
    forms are located sequentially in a space-stripped view of the boundary
    stream (Azure drops the spaces of letter aliases); each match becomes one
    display-text boundary spanning the matched run. Unmatched pairs stay spoken.
    """
    if not pairs or not word_boundaries:
        return word_boundaries
    concat = "".join(wb["text"] for wb in word_boundaries)
    spans = []
    pos = 0
    for wb in word_boundaries:
        spans.append((pos, pos + len(wb["text"])))
        pos += len(wb["text"])

    flat_chars = []
    fmap = []
    for ci, ch in enumerate(concat):
        if ch != " ":
            fmap.append(ci)
            flat_chars.append(ch)
    flat = "".join(flat_chars)

    reps = []
    cur = 0
    for spoken, display in pairs:
        sf = spoken.replace(" ", "")
        j = flat.find(sf, cur)
        if j == -1:
            print(f"  ⚠ 边界映射未命中: {spoken} → {display} (字幕保留读音文本)")
            continue
        reps.append((fmap[j], fmap[j + len(sf) - 1] + 1, display))
        cur = j + len(sf)
    if not reps:
        return word_boundaries

    def time_at(p):
        for (s, e), wb in zip(spans, word_boundaries):
            if s <= p <= e:
                ratio = (p - s) / max(1, e - s)
                return wb["offset"] + wb["duration"] * ratio
        return word_boundaries[-1]["offset"] + word_boundaries[-1]["duration"]

    out = []
    pos = 0
    ri = 0
    while pos < len(concat):
        if ri < len(reps) and reps[ri][0] == pos:
            s, e, disp = reps[ri]
            out.append(
                {
                    "text": disp,
                    "offset": time_at(s),
                    "duration": time_at(e) - time_at(s),
                }
            )
            pos = e
            ri += 1
            continue
        nxt = reps[ri][0] if ri < len(reps) else len(concat)
        e = min(nxt, len(concat))
        for s, be in spans:
            if s <= pos < be:
                e = min(e, be)
                break
        piece = concat[pos:e]
        out.append(
            {
                "text": piece,
                "offset": time_at(pos),
                "duration": time_at(e) - time_at(pos),
            }
        )
        pos = e
    return out


# ---------------------------------------------------------------------------
# SSML (azure) + phoneme application
# ---------------------------------------------------------------------------

_TONE_MAP = {
    "ā": ("a", 1),
    "á": ("a", 2),
    "ǎ": ("a", 3),
    "à": ("a", 4),
    "ē": ("e", 1),
    "é": ("e", 2),
    "ě": ("e", 3),
    "è": ("e", 4),
    "ī": ("i", 1),
    "í": ("i", 2),
    "ǐ": ("i", 3),
    "ì": ("i", 4),
    "ō": ("o", 1),
    "ó": ("o", 2),
    "ǒ": ("o", 3),
    "ò": ("o", 4),
    "ū": ("u", 1),
    "ú": ("u", 2),
    "ǔ": ("u", 3),
    "ù": ("u", 4),
    "ǖ": ("v", 1),
    "ǘ": ("v", 2),
    "ǚ": ("v", 3),
    "ǜ": ("v", 4),
}


def pinyin_to_sapi(pinyin):
    """Tone-marked pinyin -> SAPI alphabet, e.g. 'tóng háng' -> 'tong 2 hang 2'."""
    out = []
    for syl in pinyin.split():
        plain = []
        tone = 5
        for ch in syl:
            if ch in _TONE_MAP:
                base, t = _TONE_MAP[ch]
                plain.append(base)
                tone = t
            else:
                plain.append(ch)
        out.append("".join(plain) + " " + str(tone))
    return " ".join(out)


def apply_phonemes(text, phoneme_dict):
    """Wrap multi-character dict words in <phoneme alphabet='sapi'> tags."""
    if not phoneme_dict:
        return text
    sorted_words = sorted(phoneme_dict, key=len, reverse=True)
    placeholders = {}
    result = text
    for i, word in enumerate(sorted_words):
        if word not in result:
            continue
        val = phoneme_dict[word]
        if not val or str(val).strip().lower() == "off":
            continue
        placeholder = f"__PH_{i}__"
        placeholders[placeholder] = (word, val)
        result = result.replace(word, placeholder)
    for placeholder, (word, pinyin) in placeholders.items():
        ph = pinyin_to_sapi(pinyin)
        tag = f'<phoneme alphabet="sapi" ph="{ph}">{word}</phoneme>'
        result = result.replace(placeholder, tag)
    return result


def build_ssml(text, voice, style=None, rate=None, phonemes=None):
    """Wrap text in SSML for Azure. Escapes first, then inserts phoneme tags."""
    escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    body = apply_phonemes(escaped, phonemes or {})
    if style and rate:
        wrapped = (
            f'<mstts:express-as style="{style}"><prosody rate="{rate}">'
            f"{body}</prosody></mstts:express-as>"
        )
    elif style:
        wrapped = f'<mstts:express-as style="{style}">{body}</mstts:express-as>'
    elif rate:
        wrapped = f'<prosody rate="{rate}">{body}</prosody>'
    else:
        wrapped = body
    return (
        '<speak version="1.0" xml:lang="zh-CN" '
        'xmlns="http://www.w3.org/2001/10/synthesis" '
        'xmlns:mstts="https://www.w3.org/2001/mstts">'
        f'<voice name="{voice}">{wrapped}</voice>'
        "</speak>"
    )


# ---------------------------------------------------------------------------
# Word boundaries: punctuation re-insertion (azure/edge ticks -> seconds)
# ---------------------------------------------------------------------------

_PUNCT_RE = re.compile(r"[，。！？、：；" "''…—，！?]$")
_PUNCTS = tuple("，。！？、：；‘’“”…—")


def merge_boundaries(text, raw, base_offset=0.0):
    """Reinsert punctuation between spoken-text word-boundary tokens.

    `raw` is the backend's token list in 100ns ticks ({offset, duration,
    text}); tokens already carrying punctuation pass through as-is. Missing
    punctuation chars sit at the previous token's end with a tiny duration.
    Returns a new list in seconds with base_offset applied.
    """
    result = []
    cursor = 0
    prev_end = 0.0
    for token in raw:
        off = base_offset + token["offset"] / 10000000.0
        dur = token["duration"] / 10000000.0
        word = token.get("text", "")
        if word:
            while cursor < len(text) and text[cursor] != word[0]:
                result.append(
                    {"text": text[cursor], "offset": prev_end, "duration": 0.01}
                )
                cursor += 1
        result.append({"text": word, "offset": off, "duration": dur})
        cursor += len(word)
        prev_end = off + dur
    while cursor < len(text):
        result.append({"text": text[cursor], "offset": prev_end, "duration": 0.01})
        cursor += 1
    return result


# ---------------------------------------------------------------------------
# Synthesis
# ---------------------------------------------------------------------------

_DEFAULT_VOICES = {
    "azure": "zh-CN-XiaoxiaoNeural",
    "edge": "zh-CN-XiaoxiaoNeural",
}


def _resample_to_wav(src, dst):
    """Resample any audio to the suite standard 48 kHz mono 16-bit WAV."""
    proc = subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            src,
            "-ar",
            "48000",
            "-ac",
            "1",
            "-sample_fmt",
            "s16",
            dst,
        ],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg resample failed: {proc.stderr.strip()[-200:]}")


def _synth_azure_once(spoken, voice, style, rate, phonemes, part_file):
    """Synthesize one chunk via the Azure Speech SDK.

    Returns (wav_duration, raw_100ns_boundaries). The raw part is written next
    to part_file and resampled in place by the caller.
    """
    import azure.cognitiveservices.speech as speechsdk

    key = os.environ.get("AZURE_SPEECH_KEY")
    region = os.environ.get("AZURE_SPEECH_REGION")
    if not key or not region:
        raise RuntimeError("Set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION first")
    ssml = build_ssml(spoken, voice, style=style, rate=rate, phonemes=phonemes)
    raw_file = part_file + ".raw.wav"
    config = speechsdk.SpeechConfig(subscription=key, region=region)
    config.SpeechSynthesisVoiceName = voice
    audio = speechsdk.audio.AudioOutputConfig(filename=raw_file)
    synth = speechsdk.SpeechSynthesizer(speech_config=config, audio_config=audio)
    boundaries = []

    def cb(evt):
        boundaries.append(
            {
                "offset": evt.audio_offset,
                "duration": evt.duration.total_seconds() * 10000000.0,
                "text": evt.text,
            }
        )

    synth.synthesis_word_boundary.connect(cb)
    result = synth.speak_ssml_async(ssml).get()
    if (
        result is None
        or result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted
    ):
        detail = result.cancellation_details if result is not None else None
        err = detail.error_details if detail else ""
        raise RuntimeError(f"Azure synthesis failed: {result} {err}")
    _resample_to_wav(raw_file, part_file)
    os.remove(raw_file)
    dur = check_resume(part_file)
    if dur is None:
        raise RuntimeError("Azure output could not be probed — no duration")
    return dur, boundaries


def _synth_edge_once(spoken, voice, rate, part_file):
    """Synthesize one chunk via edge-tts (free, no key).

    Returns (wav_duration, raw_100ns_boundaries). edge-tts streams an MP3 and
    WordBoundary metadata; the MP3 is resampled to the standard WAV.
    """
    import edge_tts

    raw_file = part_file + ".raw.mp3"
    boundaries = []

    async def _run():
        tts = edge_tts.Communicate(spoken, voice, rate=rate, boundary="WordBoundary")
        async for chunk in tts.stream():
            ctype = chunk.get("type")
            if ctype == "audio":
                data = chunk.get("data")
                if data:
                    with open(raw_file, "ab") as f:
                        f.write(data)
            elif ctype == "WordBoundary":
                offsets = chunk.get("offset")
                dur_ticks = chunk.get("duration")
                text = chunk.get("text")
                if offsets is not None and dur_ticks is not None and text:
                    boundaries.append(
                        {
                            "offset": offsets,
                            "duration": dur_ticks,
                            "text": text,
                        }
                    )

    asyncio.run(_run())
    if not os.path.exists(raw_file) or os.path.getsize(raw_file) == 0:
        raise RuntimeError("edge-tts returned no audio")
    _resample_to_wav(raw_file, part_file)
    os.remove(raw_file)
    dur = check_resume(part_file)
    if dur is None:
        raise RuntimeError("edge-tts output could not be probed — no duration")
    return dur, boundaries


def _load_phonemes(path):
    """Load the resolved phoneme dict JSON written by generate_tts.py."""
    if not path or not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def synthesize(chunks, config, output_dir, resume=False):
    """Synthesize all chunks through the local azure/edge backend.

    Mirrors the ttscn bridge contract: returns (part_files, word_boundaries,
    total_duration) where each boundary carries DISPLAY text.
    """
    platform = config.get("platform") or "edge"
    voice = config.get("voice") or _DEFAULT_VOICES.get(platform, "zh-CN-XiaoxiaoNeural")
    rate = config.get("speech_rate") or "+5%"
    style = config.get("style")
    phonemes = _load_phonemes(config.get("phonemes_path"))

    part_files = []
    word_boundaries = []
    accumulated = 0.0
    os.makedirs(output_dir, exist_ok=True)

    for i, chunk in enumerate(chunks):
        part_file = os.path.join(output_dir, f"part_{i}.wav")
        part_files.append(part_file)

        if resume:
            dur = check_resume(part_file)
            if dur is not None:
                print(f"  ⏭ Part {i + 1}/{len(chunks)} skipped (resume, {dur:.1f}s)")
                # No boundary data on resume — caller falls back to proportional.
                accumulated += dur
                continue

        display = strip_markers(chunk)
        spoken, pairs = pronounce(display)

        if platform == "azure":
            dur, raw = _synth_azure_once(
                spoken, voice, style, rate, phonemes, part_file
            )
        else:
            dur, raw = _synth_edge_once(spoken, voice, rate, part_file)

        # merge_boundaries aligns the SPOKEN token stream (what the engine
        # reports for numbers/aliases) against the spoken text, then
        # map_boundaries_to_display rewrites each spoken run back to its
        # display form so SRT/section-matching see the script verbatim.
        merged = map_boundaries_to_display(
            merge_boundaries(spoken, raw, base_offset=accumulated), pairs
        )
        word_boundaries.extend(merged)
        accumulated += dur
        print(
            f"  ✓ Part {i + 1}/{len(chunks)} done via local/{platform} "
            f"({len(display)} chars, {dur:.1f}s)"
        )

    return part_files, word_boundaries, accumulated
