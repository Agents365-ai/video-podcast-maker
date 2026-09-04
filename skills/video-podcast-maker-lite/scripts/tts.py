#!/usr/bin/env python3
"""Video Podcast Maker Lite TTS: script -> Azure TTS (SSML) -> audio + SRT + timing.

Single-file sibling of the full skill's modular scripts/tts package: Azure
only, no extra skills. One section per synthesis (SSML), concatenated with
ffmpeg, so section timings are exact by construction.

Usage:
  python3 tts.py <podcast.txt> <output_dir> [--voice V] [--style S] [--rate R]
                 [--phonemes FILE] [--aliases FILE] [--check]

Output: podcast_audio.wav, podcast_audio.srt, timing.json, cues.json.
Env fallbacks: TTS_VOICE / TTS_STYLE / TTS_RATE.
"""
import argparse
import json
import os
import re
import sys
import subprocess

# ---------------------------------------------------------------------------
# Number conversion
# ---------------------------------------------------------------------------

_CN_DIGITS = "零一二三四五六七八九"
_CN_UNITS = ["", "十", "百", "千"]


def _four_to_cn(s):
    """1-4 digit string -> Chinese, e.g. '1200' -> 一千二百, '1005' -> 一千零五."""
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
# Pronunciation layer (display -> spoken, boundaries mapped back for subtitles)
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

# Quantifier words glued to a spoken number ("10 倍" -> 十倍, "57 分" ->
# 五十七分, "0.045 美元" -> 零点零四五美元) so Azure keeps the number and its
# quantifier in one unit instead of pausing. Longest word matches first.
_CN_QWORDS = (
    "美元", "小时", "分钟", "公斤", "公里", "万人", "亿人", "百万", "千万",
    "倍", "个", "层", "名", "分", "秒", "天", "月", "年", "岁", "元", "万",
    "亿", "点", "份", "位", "次", "条", "张", "件", "台", "只", "本", "套",
    "架", "批", "轮", "项", "组", "段", "页", "版", "款",
)
# A spoken token ending in these characters is a full number reading.
_CN_NUM_CHARS = "点十百千万亿零一二三四五六七八九"


def _mixed_token_to_spoken(token):
    """'9B' -> 九B, '35B' -> 三十五B, 'Qwen3.5' -> 千问三点五."""
    def repl(m):
        if m.group(1):
            return LETTER_WORD_ALIASES.get(m.group(1).lower(), m.group(1))
        return num_to_cn(m.group(2))
    return re.sub(r"([A-Za-z]+)|([0-9]+(?:\.[0-9]+)?)", repl, token)


# Number-bearing token: 9B / 35B / 86.1 / 5600 / A3B / Qwen3.5 ...
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
                # Glue a directly-following quantifier word to a spoken number
                # so Azure reads 十倍 as one unit instead of inserting a pause
                # between the number word and its quantifier.
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
    display-text boundary spanning the matched run, timing split
    proportionally. Unmatched pairs are left as spoken.
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
            out.append({"text": disp, "offset": time_at(s), "duration": time_at(e) - time_at(s)})
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
        out.append({
            "text": piece,
            "offset": time_at(pos),
            "duration": time_at(e) - time_at(pos),
        })
        pos = e
    return out


# ---------------------------------------------------------------------------
# Phoneme dictionary (multi-character words -> SSML phoneme tags)
# ---------------------------------------------------------------------------

_TONE_MAP = {
    "ā": ("a", 1), "á": ("a", 2), "ǎ": ("a", 3), "à": ("a", 4),
    "ē": ("e", 1), "é": ("e", 2), "ě": ("e", 3), "è": ("e", 4),
    "ī": ("i", 1), "í": ("i", 2), "ǐ": ("i", 3), "ì": ("i", 4),
    "ō": ("o", 1), "ó": ("o", 2), "ǒ": ("o", 3), "ò": ("o", 4),
    "ū": ("u", 1), "ú": ("u", 2), "ǔ": ("u", 3), "ù": ("u", 4),
    "ǖ": ("v", 1), "ǘ": ("v", 2), "ǚ": ("v", 3), "ǜ": ("v", 4),
}


def pinyin_to_sapi(pinyin):
    """Tone-marked pinyin -> SAPI alphabet, e.g. 'tóng háng' -> 'tong 2 hang 2'.

    Neutral tone = 5; ü -> v (SAPI has no ü).
    """
    syllables = pinyin.split()
    out = []
    for syl in syllables:
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
    """Wrap multi-character dict words in <phoneme alphabet="sapi"> tags.

    Longest words first, placeholders prevent nested re-tags. A dict entry
    whose value is falsy or "off" is skipped (MiniMax neutralizer convention).
    """
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


def load_phoneme_dict(input_path, explicit=None):
    """Load the phoneme dict: an explicit --phonemes file REPLACES the merge
    (global + project); otherwise global ~/.video-podcast-maker/phonemes.json
    and the phonemes.json next to the input are merged, project wins. Keys
    starting with '_' are comments and are skipped.
    """
    if explicit:
        if not os.path.exists(explicit):
            return {}
        with open(explicit, encoding="utf-8") as f:
            data = json.load(f)
        return {k: v for k, v in data.items() if not k.startswith("_")}

    merged = {}
    global_path = os.path.join(
        os.path.expanduser("~/.video-podcast-maker"), "phonemes.json")
    if os.path.exists(global_path):
        with open(global_path, encoding="utf-8") as f:
            data = json.load(f)
        merged.update({k: v for k, v in data.items() if not k.startswith("_")})
    project_path = os.path.join(
        os.path.dirname(os.path.abspath(input_path)), "phonemes.json")
    if os.path.exists(project_path):
        with open(project_path, encoding="utf-8") as f:
            data = json.load(f)
        merged.update({k: v for k, v in data.items() if not k.startswith("_")})
    return merged


def load_aliases(input_path, explicit=None):
    """Load pronunciation aliases, same priority as load_phoneme_dict:
    an explicit --aliases file replaces the merge, otherwise global
    ~/.video-podcast-maker/aliases.json + the aliases.json next to the input
    are merged (project wins)."""
    if explicit:
        if not os.path.exists(explicit):
            return {}
        with open(explicit, encoding="utf-8") as f:
            return json.load(f)

    merged = {}
    global_path = os.path.join(
        os.path.expanduser("~/.video-podcast-maker"), "aliases.json")
    if os.path.exists(global_path):
        with open(global_path, encoding="utf-8") as f:
            merged.update(json.load(f))
    project_path = os.path.join(
        os.path.dirname(os.path.abspath(input_path)), "aliases.json")
    if os.path.exists(project_path):
        with open(project_path, encoding="utf-8") as f:
            merged.update(json.load(f))
    return merged


# ---------------------------------------------------------------------------
# Script parsing
# ---------------------------------------------------------------------------

def parse_sections(text):
    """Parse [SECTION:name|label] markers.

    Comment lines (starting with '#') are removed first, so markers inside
    comments never create sections; an empty section (no narration left) is
    an error. Raises ValueError on no markers / duplicate names / empty
    section. Returns a list of {name, label, text}. `label` is the explicit
    marker suffix or the section's first sentence (first punctuation run).
    """
    lines = [ln for ln in text.splitlines() if not ln.strip().startswith("#")]
    clean = "\n".join(lines)
    pattern = r"\[SECTION:(\w[\w-]*)(?:\|([^\]\n]+))?\]"
    matches = list(re.finditer(pattern, clean))
    if not matches:
        raise ValueError("No [SECTION] markers found in script")
    sections = []
    names = []
    for i, m in enumerate(matches):
        name = m.group(1)
        if name in names:
            raise ValueError(f"Duplicate section name: {name}")
        names.append(name)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(clean)
        section_text = clean[start:end].strip()
        if not section_text:
            raise ValueError(f"Section '{name}' has no narration")
        explicit = (m.group(2) or "").strip()
        if explicit:
            label = explicit
        else:
            first_line = section_text.splitlines()[0]
            label = re.split(r"[，。！？、：；]", first_line)[0][:10] or name
        first_paras = re.sub(r"\s+", "", section_text[:80])
        sections.append({
            "name": name,
            "label": label,
            "text": section_text,
            "first_text": first_paras,
        })
    return sections


# ---------------------------------------------------------------------------
# SSML building
# ---------------------------------------------------------------------------

def build_ssml(text, voice, style=None, rate=None, phonemes=None):
    """Wrap text in SSML for Azure. Text is escaped first, then phoneme tags
    are inserted (so raw tags survive and nothing gets double-escaped).
    """
    escaped = (
        text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )
    body = apply_phonemes(escaped, phonemes or {})
    if style and rate:
        wrapped = f'<mstts:express-as style="{style}"><prosody rate="{rate}">{body}</prosody></mstts:express-as>'
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
# Word boundaries: punctuation re-insertion + subtitle cues + SRT
# ---------------------------------------------------------------------------

_PUNCT_RE = re.compile(r"[，。！？、：；""''…—，！?]$")
_PUNCTS = tuple("，。！？、：；‘’“”…—")


def merge_boundaries(text, raw, base_offset=0.0):
    """Reinsert punctuation between Azure word-boundary tokens.

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
        # Any non-token characters between the previous token and this one
        # are punctuation we synthesized (edge-tts/azure drop them).
        if word:
            while cursor < len(text) and text[cursor] != word[0]:
                result.append({"text": text[cursor], "offset": prev_end, "duration": 0.01})
                cursor += 1
        result.append({"text": word, "offset": off, "duration": dur})
        cursor += len(word)
        prev_end = off + dur
    while cursor < len(text):
        result.append({"text": text[cursor], "offset": prev_end, "duration": 0.01})
        cursor += 1
    return result


STRONG_PUNCTS = set("。！？")
WEAK_PUNCTS = set("，；、：")

# MiniMax sound tags ([PAUSE:x] / (chuckle) etc) ride the full skill's ttscn
# bridge; on the Azure path they are not expressiveness — strip them before
# synthesis so they never reach the SSML text or the subtitles.
_SOUND_TAG_RE = re.compile(r"\((?:laughs|chuckle|sighs|breath|inhale|exhale|coughs)\)")
_PAUSE_RE = re.compile(r"\[PAUSE:[\d.]+\]")


def strip_markers(text):
    """Remove [PAUSE:x] and (sound) markers (Azure has no use for them)."""
    return _SOUND_TAG_RE.sub("", _PAUSE_RE.sub("", text))


def build_cues(boundaries):
    """Pack word boundaries into [(start, end, text)] subtitle cues.

    Break after a strong punctuation once text reaches 10 chars, after a weak
    one at 20, and force a break past 40 chars that backtracks to the last
    punctuation (never cutting mid-phrase). Edge punctuation is stripped.
    """
    cues = []
    buf = []
    buf_text = ""

    def flush(entries):
        if not entries:
            return
        text = "".join(e[0] for e in entries)
        clean = re.sub(r"^[，。！？、：；“”‘’…—\s]+|[，。！？、：；“”‘’…—\s]+$", "", text.strip())
        if not clean:
            return
        start = entries[0][1]
        last = entries[-1]
        cues.append((start, last[1] + last[2], clean))

    def last_punct_idx(entries, punct_set):
        for j in range(len(entries) - 1, -1, -1):
            if entries[j][0] in punct_set:
                return j
        return -1

    for i, wb in enumerate(boundaries):
        buf.append((wb["text"], wb["offset"], wb["duration"]))
        buf_text += wb["text"]
        text_len = len(buf_text)
        is_last = i == len(boundaries) - 1
        is_strong = wb["text"] in STRONG_PUNCTS
        is_weak = wb["text"] in WEAK_PUNCTS

        should_break = False
        if is_last:
            should_break = True
        elif is_strong and text_len >= 10:
            should_break = True
        elif is_weak and text_len >= 20:
            should_break = True
        elif text_len >= 40:
            strong_idx = last_punct_idx(buf, STRONG_PUNCTS)
            weak_idx = last_punct_idx(buf, WEAK_PUNCTS)
            break_idx = strong_idx if strong_idx >= 0 else weak_idx
            if break_idx >= 0 and break_idx > 0:
                flush(buf[: break_idx + 1])
                remaining = buf[break_idx + 1:]
                buf = list(remaining)
                buf_text = "".join(e[0] for e in buf)
                continue
            should_break = True

        if should_break:
            flush(buf)
            buf = []
            buf_text = ""

    flush(buf)
    return cues


def format_srt_time(seconds):
    """HH:MM:SS,mmm with rounded milliseconds (1.9999s -> 00:00:02,000)."""
    total_ms = round(seconds * 1000)
    h, rem = divmod(total_ms, 3_600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def render_srt(cues):
    """cues -> SRT string: 1-indexed, HH:MM:SS,mmm timestamps."""
    return "\n".join(
        f"{i + 1}\n{format_srt_time(start)} --> {format_srt_time(end)}\n{text}\n"
        for i, (start, end, text) in enumerate(cues)
    ) + "\n"


def build_timing(sections, durations, total_duration):
    """Sections + per-section durations -> timing.json dict.

    With per-section synthesis the section boundaries are exact by
    construction: start = cumulative duration, end = next start.
    """
    fps = 30
    parts = []
    t = 0.0
    for sec, dur in zip(sections, durations):
        start = round(t, 4)
        t += dur
        parts.append({
            "name": sec["name"],
            "label": sec["label"],
            "text": sec["text"],
            "start_time": start,
            "end_time": round(t, 4),
            "duration": round(dur, 4),
            "start_frame": int(start * fps),
            "duration_frames": int(dur * fps),
            "is_silent": False,
        })
    return {
        "total_duration": total_duration,
        "fps": fps,
        "total_frames": int(total_duration * fps),
        "sections": parts,
    }


# ---------------------------------------------------------------------------
# CLI: Azure synthesis per section, ffmpeg concat, SRT/timing/cues output
# ---------------------------------------------------------------------------

def _synth_azure_once(ssml, voice, part_file):
    """Synthesize one section; returns (wav_duration, raw_100ns_boundaries)."""
    import azure.cognitiveservices.speech as speechsdk

    key = os.environ.get("AZURE_SPEECH_KEY")
    region = os.environ.get("AZURE_SPEECH_REGION")
    if not key or not region:
        sys.exit("Set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION first")
    config = speechsdk.SpeechConfig(subscription=key, region=region)
    config.SpeechSynthesisVoiceName = voice
    audio = speechsdk.audio.AudioOutputConfig(filename=part_file)
    synth = speechsdk.SpeechSynthesizer(speech_config=config, audio_config=audio)
    boundaries = []

    def cb(evt):
        boundaries.append({
            "offset": evt.audio_offset,
            "duration": evt.duration.total_seconds() * 10000000.0,
            "text": evt.text,
        })

    synth.synthesis_word_boundary.connect(cb)
    result = synth.speak_ssml_async(ssml).get()
    if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
        detail = result.cancellation_details
        err = detail.error_details if detail else ""
        raise RuntimeError(f"Azure synthesis failed: {result.reason} {err}")
    probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", part_file],
        capture_output=True, text=True)
    return (float(probe.stdout.strip()) if probe.stdout.strip() else 0.0), boundaries


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", help="podcast.txt path")
    ap.add_argument("output_dir", help="where to write wav/srt/timing.json/cues.json")
    ap.add_argument("--voice", default=os.environ.get("TTS_VOICE", "zh-CN-XiaoxiaoNeural"))
    ap.add_argument("--style", default=os.environ.get("TTS_STYLE", ""))
    ap.add_argument("--rate", default=os.environ.get("TTS_RATE", "+0%"))
    ap.add_argument("--phonemes", help="explicit phoneme dict (replaces project-level)")
    ap.add_argument("--aliases", help="explicit alias dict (replaces project-level)")
    ap.add_argument("--check", action="store_true", help="lint only — no synthesis")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        script = f.read()
    sections = parse_sections(script)
    phoneme_dict = load_phoneme_dict(args.input, args.phonemes)
    alias_dict = load_aliases(args.input, args.aliases)
    merged_aliases = {**PRONUNCIATION_ALIASES, **alias_dict}

    print(f"Sections: {len(sections)} ({', '.join(s['name'] for s in sections)})")
    if args.check:
        print("Lint mode: no synthesis.")
        return 0

    os.makedirs(args.output_dir, exist_ok=True)
    part_files = []
    all_boundaries = []
    accumulated = 0.0
    durations = []

    for i, sec in enumerate(sections):
        sat_text = strip_markers(sec["text"])
        spoken, pairs = pronounce(sat_text, merged_aliases)
        ssml = build_ssml(spoken, args.voice, style=args.style or None,
                          rate=args.rate, phonemes=phoneme_dict)
        part_file = os.path.join(args.output_dir, f"part_{i}.wav")
        part_files.append(part_file)
        seg_dur, raw = _synth_azure_once(ssml, args.voice, part_file)
        print(f"  ✓ {sec['name']} ({len(sec['text'])} chars, {seg_dur:.1f}s)")
        merged = map_boundaries_to_display(
            merge_boundaries(sat_text, raw, base_offset=accumulated), pairs)
        all_boundaries.extend(merged)
        durations.append(seg_dur)
        accumulated += seg_dur

    total = accumulated
    concat_list = os.path.join(args.output_dir, "concat_list.txt")
    with open(concat_list, "w") as f:
        for pf in part_files:
            f.write(f"file '{os.path.basename(pf)}'\n")
    wav = os.path.join(args.output_dir, "podcast_audio.wav")
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i",
         os.path.basename(concat_list), "-c", "copy", os.path.basename(wav)],
        capture_output=True, text=True, cwd=args.output_dir, check=True)

    # Cues: per section so a cue never spans sections. Offsets are absolute.
    starts = []
    t = 0.0
    for d in durations:
        starts.append(t)
        t += d
    cue_secs = []
    for sec_idx, sec_start in enumerate(starts):
        sec_end = sec_start + durations[sec_idx]
        sec_boundaries = [wb for wb in all_boundaries if sec_start <= wb["offset"] < sec_end]
        for c in build_cues(sec_boundaries):
            cue_secs.append((c, sec_idx))

    srt = render_srt([c for c, _ in cue_secs])
    with open(os.path.join(args.output_dir, "podcast_audio.srt"), "w", encoding="utf-8") as f:
        f.write(srt)

    timing = build_timing(sections, durations, total)
    with open(os.path.join(args.output_dir, "timing.json"), "w", encoding="utf-8") as f:
        json.dump(timing, f, ensure_ascii=False, indent=2)

    cue_data = []
    for (start, end, text), sec_idx in cue_secs:
        cue_data.append({
            "text": text,
            "start": round(start, 3),
            "end": round(end, 3),
            "frame": round(start * 30),
            "section_frame": round((start - starts[sec_idx]) * 30),
            "section": sections[sec_idx]["name"],
        })
    with open(os.path.join(args.output_dir, "cues.json"), "w", encoding="utf-8") as f:
        json.dump({"fps": 30, "cues": cue_data}, f, ensure_ascii=False, indent=2)

    print(f"\n✓ 总时长: {total:.1f}s ({timing['total_frames']} 帧 @ 30fps)")
    print(f"✓ 字幕: {os.path.join(args.output_dir, 'podcast_audio.srt')} ({len(cue_secs)} 条)")
    print(f"✓ 时间轴: {os.path.join(args.output_dir, 'timing.json')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
