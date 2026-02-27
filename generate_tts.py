#!/usr/bin/env python3
"""
Azure TTS Script for Video Podcast Maker
Generates audio from podcast.txt and creates SRT subtitles + timing.json for Remotion sync
"""
import os
import sys
import json
import argparse
import azure.cognitiveservices.speech as speechsdk
import subprocess
import re
import time
import uuid
from xml.sax.saxutils import escape

# Import polyphone database
try:
    from polyphone_db import POLYPHONE_DATABASE, find_polyphone_chars, suggest_pronunciation, get_all_polyphone_words
    POLYPHONE_DB_AVAILABLE = True
except ImportError:
    POLYPHONE_DB_AVAILABLE = False


# ============ 多音字处理函数 ============
def load_phoneme_dict(input_file, phoneme_file=None):
    """Load phoneme dictionary from JSON file

    Searches in order:
    1. Explicit --phonemes argument
    2. phonemes.json in same directory as input file
    3. Global ~/.config/video-podcast-maker/phonemes.json
    """
    search_paths = []
    if phoneme_file:
        search_paths.append(phoneme_file)
    search_paths.append(os.path.join(os.path.dirname(input_file), 'phonemes.json'))
    search_paths.append(os.path.expanduser('~/.config/video-podcast-maker/phonemes.json'))

    for path in search_paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"✓ 加载多音字词典: {path} ({len(data)} 条)")
                return data
    return {}


def extract_inline_phonemes(text):
    """Extract inline phoneme markers from text: 执行器[zhí xíng qì]

    Returns: (clean_text, phoneme_dict)
    """
    pattern = r'([\u4e00-\u9fff]+)\[([a-zA-Zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜü\s]+)\]'
    phonemes = {}

    def extract(m):
        word, pinyin = m.group(1), m.group(2)
        phonemes[word] = pinyin
        return word

    clean = re.sub(pattern, extract, text)
    return clean, phonemes


def pinyin_to_sapi(pinyin):
    """Convert pinyin with tone marks to SAPI format with numeric tones

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
        tone = '5'  # neutral tone
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
    """Apply SSML phoneme tags for multi-character words

    Uses SAPI alphabet with numeric tones for Azure TTS compatibility.
    Phoneme dict format: {"执行器": "zhí xíng qì", "重做": "chóng zuò"}
    """
    if not phoneme_dict:
        return text

    # Sort by length (longest first) to avoid partial replacements
    sorted_words = sorted(phoneme_dict.keys(), key=len, reverse=True)

    result = text
    for word in sorted_words:
        pinyin = phoneme_dict[word]
        sapi_pinyin = pinyin_to_sapi(pinyin)
        # Use sapi alphabet (Azure TTS native format)
        phoneme_tag = f'<phoneme alphabet="sapi" ph="{sapi_pinyin}">{word}</phoneme>'
        result = result.replace(word, phoneme_tag)

    return result


# Built-in phoneme dictionary for common polyphones
BUILTIN_POLYPHONES = {
    # "行" as háng (row/line)
    '一行命令': 'yì háng mìng lìng',
    '一行代码': 'yì háng dài mǎ',
    '命令行': 'mìng lìng háng',
    '代码行': 'dài mǎ háng',
    '多行': 'duō háng',
    '行数': 'háng shù',
    '几行': 'jǐ háng',
    # "重" as chóng (repeat)
    '重做': 'chóng zuò',
    '重新': 'chóng xīn',
    '重复': 'chóng fù',
    '重试': 'chóng shì',
    # "行" as xíng (execute)
    '执行器': 'zhí xíng qì',
    '执行': 'zhí xíng',
    '运行': 'yùn xíng',
    '并行': 'bìng xíng',
}


# ============ 多音字扫描功能 ============
def scan_polyphones(text, phoneme_dict):
    """Scan text for polyphone characters and generate report

    Args:
        text: Input text to scan
        phoneme_dict: Already-applied phoneme dictionary

    Returns dict with:
        covered: List of polyphone words already in phoneme_dict
        uncovered: List of detected polyphone occurrences not covered
        suggestions: Dict of word -> pinyin suggestions
        ambiguous: List of characters that couldn't be auto-determined
    """
    if not POLYPHONE_DB_AVAILABLE:
        return {"error": "polyphone_db.py not found", "covered": [], "uncovered": [], "suggestions": {}, "ambiguous": []}

    result = {"covered": [], "uncovered": [], "suggestions": {}, "ambiguous": []}

    # Get all known polyphone words from database
    all_polyphone_words = get_all_polyphone_words()

    # Track covered words (already in phoneme_dict)
    for word in phoneme_dict:
        if any(c in POLYPHONE_DATABASE for c in word):
            result["covered"].append({"word": word, "pinyin": phoneme_dict[word]})

    # Find polyphone characters in text
    polyphone_positions = find_polyphone_chars(text)

    # Track which positions are covered by phoneme_dict words
    covered_positions = set()
    for word in phoneme_dict:
        start = 0
        while True:
            pos = text.find(word, start)
            if pos == -1:
                break
            for i in range(pos, pos + len(word)):
                covered_positions.add(i)
            start = pos + 1

    # Check uncovered polyphone characters
    lines = text.split('\n')
    line_starts = [0]
    for line in lines[:-1]:
        line_starts.append(line_starts[-1] + len(line) + 1)

    def get_line_number(pos):
        for i, start in enumerate(line_starts):
            if i + 1 < len(line_starts) and pos < line_starts[i + 1]:
                return i + 1
            elif i + 1 == len(line_starts) and pos >= start:
                return i + 1
        return 1

    for pos, char in polyphone_positions:
        if pos in covered_positions:
            continue

        # Get surrounding context
        ctx_start = max(0, pos - 10)
        ctx_end = min(len(text), pos + 11)
        context_before = text[ctx_start:pos]
        context_after = text[pos + 1:ctx_end]
        context = text[ctx_start:ctx_end]

        # Try to find matching word pattern
        pinyin, matched_word = suggest_pronunciation(char, context_before, context_after)
        line_num = get_line_number(pos)

        if matched_word:
            # Found a known word pattern
            if matched_word not in result["suggestions"]:
                result["uncovered"].append({
                    "line": line_num,
                    "char": char,
                    "word": matched_word,
                    "context": context.strip(),
                    "suggestion": pinyin
                })
                result["suggestions"][matched_word] = pinyin
        else:
            # Ambiguous - couldn't determine pronunciation
            result["ambiguous"].append({
                "line": line_num,
                "char": char,
                "context": context.strip(),
                "default": pinyin
            })

    return result


def print_polyphone_report(report):
    """Print formatted polyphone scan report"""
    print("\n" + "═" * 50)
    print("           多音字扫描报告")
    print("═" * 50)

    if report.get("error"):
        print(f"\n❌ 错误: {report['error']}")
        return

    # Covered words
    if report["covered"]:
        print(f"\n✅ 已处理 ({len(report['covered'])}):")
        for item in report["covered"][:10]:
            print(f"   {item['word']} → {item['pinyin']}")
        if len(report["covered"]) > 10:
            print(f"   ... 及其他 {len(report['covered']) - 10} 条")

    # Uncovered words with suggestions
    if report["uncovered"]:
        print(f"\n⚠️  检测到未处理多音字 ({len(report['uncovered'])}):")
        for item in report["uncovered"]:
            print(f"   Line {item['line']}: \"{item['word']}\" - 建议: {item['suggestion']}")
            print(f"            上下文: \"{item['context']}\"")

    # Ambiguous characters
    if report["ambiguous"]:
        seen = set()
        unique_ambiguous = []
        for item in report["ambiguous"]:
            key = (item["char"], item["context"][:20])
            if key not in seen:
                seen.add(key)
                unique_ambiguous.append(item)

        print(f"\n❓ 无法自动判断 ({len(unique_ambiguous)}):")
        for item in unique_ambiguous[:5]:
            print(f"   Line {item['line']}: \"{item['char']}\" (默认: {item['default']})")
            print(f"            上下文: \"{item['context']}\"")
        if len(unique_ambiguous) > 5:
            print(f"   ... 及其他 {len(unique_ambiguous) - 5} 处")

    # Summary and suggestions
    if report["suggestions"]:
        print("\n" + "─" * 50)
        print("建议操作:")
        print("  1. 运行 --export-phonemes phonemes.json 导出建议")
        print("  2. 或使用 --auto-fix 自动应用")
        print("  3. 或手动添加到 phonemes.json:")
        print("     {")
        for word, pinyin in list(report["suggestions"].items())[:5]:
            print(f'       "{word}": "{pinyin}",')
        print("     }")

    if not report["uncovered"] and not report["ambiguous"]:
        print("\n✅ 所有多音字已处理完毕!")

    print("═" * 50 + "\n")


parser = argparse.ArgumentParser(
    description='Generate TTS audio from podcast script',
    epilog='Environment: AZURE_SPEECH_KEY (required), AZURE_SPEECH_REGION (default: eastasia), TTS_RATE (default: +5%, range: -50% to +200%)'
)
parser.add_argument('--input', '-i', default='podcast.txt', help='Input script file (default: podcast.txt)')
parser.add_argument('--output-dir', '-o', default='.', help='Output directory for podcast_audio.wav, podcast_audio.srt, timing.json (default: current dir)')
parser.add_argument('--phonemes', '-p', default=None, help='Phoneme dictionary JSON file (default: phonemes.json in input dir)')
parser.add_argument('--scan-polyphones', '-s', action='store_true', help='Scan and report unhandled polyphone characters before TTS')
parser.add_argument('--auto-fix', action='store_true', help='Automatically apply polyphone suggestions (use with --scan-polyphones)')
parser.add_argument('--export-phonemes', type=str, metavar='PATH', help='Export suggested phonemes to JSON file (use with --scan-polyphones)')
parser.add_argument('--scan-only', action='store_true', help='Only scan for polyphones, do not generate TTS')
args = parser.parse_args()

key = os.environ.get("AZURE_SPEECH_KEY")
region = os.environ.get("AZURE_SPEECH_REGION", "eastasia")
if not key:
    print("Error: AZURE_SPEECH_KEY not set", file=sys.stderr)
    print("Add to ~/.zshrc: export AZURE_SPEECH_KEY='your-key'", file=sys.stderr)
    sys.exit(1)
MAX_CHARS = 400

# Speech rate: -50% ~ +200%, or x-slow/slow/medium/fast/x-fast
SPEECH_RATE = os.environ.get("TTS_RATE", "+5%")

# Ensure output directory exists
os.makedirs(args.output_dir, exist_ok=True)

if not os.path.exists(args.input):
    print(f"Error: Input file not found: {args.input}", file=sys.stderr)
    sys.exit(1)

with open(args.input, "r") as f:
    text = f.read().strip()

# ============ 解析章节标记 ============
# 提取每个章节的名称和开头文本用于精确匹配
section_pattern = r'\[SECTION:(\w+)\]'
sections = []
matches = list(re.finditer(section_pattern, text))

for i, match in enumerate(matches):
    section_name = match.group(1)
    start_pos = match.end()
    end_pos = matches[i+1].start() if i+1 < len(matches) else len(text)
    section_text = text[start_pos:end_pos].strip()
    # 提取章节开头的前50个字符用于匹配
    first_text = re.sub(r'\s+', '', section_text[:80])  # 去除空白便于匹配
    # 标记无旁白章节（空内容或仅空白）
    is_silent = len(section_text.strip()) == 0
    sections.append({
        'name': section_name,
        'first_text': first_text,
        'start_time': None,
        'end_time': None,
        'is_silent': is_silent
    })

clean_text = re.sub(section_pattern, '', text).strip()

# Extract inline phoneme markers: 执行器[zhí xíng qì]
clean_text, inline_phonemes = extract_inline_phonemes(clean_text)
if inline_phonemes:
    print(f"✓ 提取内联多音字标注: {len(inline_phonemes)} 条")
    for word, pinyin in inline_phonemes.items():
        print(f"    {word} → {pinyin}")

# Load phoneme dictionary (file-based)
file_phonemes = load_phoneme_dict(args.input, args.phonemes)

# Merge: inline > file > builtin (priority order)
phoneme_dict = {**BUILTIN_POLYPHONES, **file_phonemes, **inline_phonemes}
print(f"✓ 多音字词典: {len(phoneme_dict)} 条 (内置{len(BUILTIN_POLYPHONES)} + 文件{len(file_phonemes)} + 内联{len(inline_phonemes)})")

# ═══ 多音字扫描 ═══
if args.scan_polyphones or args.scan_only:
    if not POLYPHONE_DB_AVAILABLE:
        print("⚠️  警告: polyphone_db.py 未找到，无法进行多音字扫描")
    else:
        report = scan_polyphones(clean_text, phoneme_dict)
        print_polyphone_report(report)

        # Export suggestions to JSON if requested
        if args.export_phonemes and report["suggestions"]:
            export_data = {**file_phonemes, **report["suggestions"]}
            with open(args.export_phonemes, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            print(f"✓ 已导出建议到: {args.export_phonemes} ({len(report['suggestions'])} 条新增)")

        # Auto-fix: apply suggestions to phoneme_dict
        if args.auto_fix and report["suggestions"]:
            phoneme_dict.update(report["suggestions"])
            print(f"✓ 已自动应用 {len(report['suggestions'])} 条多音字建议")

        # Scan-only mode: exit after report
        if args.scan_only:
            print("\n--scan-only 模式: 仅扫描，不生成 TTS")
            sys.exit(0)

        # If uncovered polyphones found and not auto-fix, warn user
        if report["uncovered"] and not args.auto_fix:
            print("⚠️  发现未处理多音字，继续生成 TTS...")
            print("   提示: 使用 --auto-fix 自动应用建议，或 --export-phonemes 导出后手动修改\n")

if not sections:
    sections = [{'name': 'main', 'first_text': '', 'start_time': 0, 'end_time': None}]
    print("提示: 未检测到章节标记 [SECTION:name]，将生成单一章节")
else:
    print(f"检测到 {len(sections)} 个章节: {[s['name'] for s in sections]}")
    for s in sections:
        print(f"  {s['name']}: \"{s['first_text'][:20]}...\"")

# 处理读音替换
clean_text = re.sub(r'([A-Za-z0-9\-]+)，读作["""]([\u4e00-\u9fff]+)["""]', r"\2", clean_text)
print(f"文本长度: {len(clean_text)} 字符")

# 分句分段
sentences = clean_text.replace("；", "。").split("。")
chunks = []
current_chunk = ""

for s in sentences:
    s = s.strip()
    if not s: continue
    if len(current_chunk) + len(s) + 1 < MAX_CHARS:
        current_chunk += s + "。"
    else:
        if current_chunk:
            chunks.append(current_chunk)
        current_chunk = s + "。"
if current_chunk:
    chunks.append(current_chunk)

print(f"分成 {len(chunks)} 段")


def mark_english_terms(text):
    """自动识别并标记英文词汇，保留已有的XML标签"""
    # Preserve existing XML tags by replacing them with placeholders
    # Use UUID-based placeholders to avoid conflicts with text content
    tags = []
    tag_pattern = r'<[^>]+>'
    placeholder_prefix = f"__XMLTAG_{uuid.uuid4().hex[:8]}_"

    def save_tag(m):
        tags.append(m.group(0))
        return f'{placeholder_prefix}{len(tags)-1}__'

    text_with_placeholders = re.sub(tag_pattern, save_tag, text)

    # Escape the text (now without XML tags)
    result = escape(text_with_placeholders)

    # Process multi-word English phrases
    multi_word_phrases = [
        "Claude Code", "Final Cut Pro", "Visual Studio Code", "VS Code",
        "Google Chrome", "Open AI", "OpenAI", "GPT 4", "GPT-4"
    ]
    for phrase in multi_word_phrases:
        escaped = escape(phrase)
        if escaped in result:
            result = result.replace(escaped, f'<lang xml:lang="en-US">{escaped}</lang>')

    # Process individual English words
    pattern = r'\b[A-Za-z][A-Za-z0-9\-\.]*[A-Za-z0-9]\b|\b[A-Za-z]{2,}\b'
    matches = list(re.finditer(pattern, result))

    for match in reversed(matches):
        word = match.group(0)
        start, end = match.start(), match.end()
        before = result[:start]
        last_open = before.rfind('<')
        last_close = before.rfind('>')
        if last_open > last_close:
            continue
        open_tags = before.count('<lang xml:lang="en-US">')
        close_tags = before.count('</lang>')
        if open_tags > close_tags:
            continue
        if word.isdigit() or len(word) == 1:
            continue
        result = result[:start] + f'<lang xml:lang="en-US">{word}</lang>' + result[end:]

    # Restore the saved tags
    for i, tag in enumerate(tags):
        result = result.replace(f'{placeholder_prefix}{i}__', tag)

    return result


# TTS 合成
config = speechsdk.SpeechConfig(subscription=key, region=region)
config.SpeechSynthesisVoiceName = "zh-CN-XiaoxiaoMultilingualNeural"
part_files = []
word_boundaries = []
accumulated_duration = 0

for i, chunk in enumerate(chunks):
    part_file = os.path.join(args.output_dir, f"part_{i}.wav")
    part_files.append(part_file)
    audio = speechsdk.audio.AudioOutputConfig(filename=part_file)
    synth = speechsdk.SpeechSynthesizer(speech_config=config, audio_config=audio)

    def word_boundary_cb(evt):
        word_boundaries.append({
            "text": evt.text,
            "offset": accumulated_duration + evt.audio_offset / 10000000.0,
            "duration": evt.duration.total_seconds(),
        })
    synth.synthesis_word_boundary.connect(word_boundary_cb)

    # 先处理多音字（在原始文本上），再处理英文标记
    # apply_phonemes works on raw text and adds phoneme tags
    chunk_with_phonemes = apply_phonemes(chunk, phoneme_dict)
    # mark_english_terms escapes special chars and adds lang tags
    processed = mark_english_terms(chunk_with_phonemes)

    ssml = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"
               xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="zh-CN">
        <voice name="zh-CN-XiaoxiaoMultilingualNeural">
            <mstts:express-as style="gentle">
                <prosody rate="{SPEECH_RATE}">{processed}</prosody>
            </mstts:express-as>
        </voice>
    </speak>"""

    success = False
    for attempt in range(1, 4):
        result = synth.speak_ssml_async(ssml).get()
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            chunk_duration = result.audio_duration.total_seconds()
            print(f"  ✓ Part {i + 1}/{len(chunks)} 完成 ({len(chunk)} 字, {chunk_duration:.1f}s)")
            accumulated_duration += chunk_duration
            success = True
            break
        else:
            details = result.cancellation_details.error_details
            print(f"  ✗ Part {i + 1} 失败 (尝试 {attempt}/3): {details}")
            if attempt < 3:
                time.sleep(attempt * 2)

    if not success:
        raise RuntimeError(f"Part {i + 1} synthesis failed")

total_duration = accumulated_duration
print(f"\n✓ 收集到 {len(word_boundaries)} 个词边界")
print(f"✓ 总时长: {total_duration:.1f} 秒")

# ============ 精确章节时间匹配 ============
# 使用滑动窗口在 word_boundaries 中搜索每个章节的开头文本
if len(sections) > 1 and word_boundaries:
    print("\n匹配章节时间...")

    wb_texts = [wb['text'] for wb in word_boundaries]

    # 第一个章节从0开始
    sections[0]['start_time'] = 0

    # 关键：按顺序搜索，从上一个匹配位置往后找
    search_start = 0

    for sec_idx, section in enumerate(sections[1:], 1):
        target = section['first_text'][:30]
        target_clean = re.sub(r'[，。！？、：；""''\s]', '', target)

        found = False
        # 从 search_start 开始搜索（确保章节按顺序）
        for i in range(search_start, len(word_boundaries)):
            window = ''
            for j in range(i, min(i + 30, len(word_boundaries))):
                window += wb_texts[j]
                window_clean = re.sub(r'[，。！？、：；""''\s]', '', window)

                # 检查窗口开头是否匹配目标开头（而不是包含）
                if len(window_clean) >= 10 and window_clean.startswith(target_clean[:12]):
                    section['start_time'] = word_boundaries[i]['offset']
                    sections[sec_idx - 1]['end_time'] = section['start_time']
                    search_start = i + 1  # 下一个章节从这里往后找
                    print(f"  ✓ {section['name']}: {section['start_time']:.2f}s (匹配: \"{window[:20]}...\")")
                    found = True
                    break
            if found:
                break

        if not found:
            # 回退：在上个章节后按比例估算
            prev_time = sections[sec_idx - 1]['start_time']
            remaining = total_duration - prev_time
            remaining_sections = len(sections) - sec_idx
            section['start_time'] = prev_time + remaining / (remaining_sections + 1)
            sections[sec_idx - 1]['end_time'] = section['start_time']
            print(f"  ⚠ {section['name']}: {section['start_time']:.2f}s (估算, 未找到: \"{target_clean[:15]}\")")

    # 处理末尾的静音章节（如 outro）
    # 静音章节从音频结束时刻开始，持续时间为0（由Remotion额外添加）
    for i in range(len(sections) - 1, -1, -1):
        if sections[i].get('is_silent', False):
            sections[i]['start_time'] = total_duration
            sections[i]['end_time'] = total_duration
            sections[i]['duration'] = 0
            # 前一个章节的结束时间也是音频结束
            if i > 0:
                sections[i-1]['end_time'] = total_duration
            print(f"  ℹ {sections[i]['name']}: 静音章节，由Remotion额外添加时长")
        else:
            break  # 遇到非静音章节就停止

    # 最后一个有内容的章节结束于音频结尾
    for section in sections:
        if section['end_time'] is None:
            section['end_time'] = total_duration

    # 计算持续时间
    for section in sections:
        if 'duration' not in section or section['duration'] is None:
            section['duration'] = section['end_time'] - section['start_time']
else:
    sections[0]['start_time'] = 0
    sections[0]['end_time'] = total_duration
    sections[0]['duration'] = total_duration

# 合并音频
print("\n合并音频...")
concat_list = os.path.join(args.output_dir, "concat_list.txt")
output_wav = os.path.join(args.output_dir, "podcast_audio.wav")
with open(concat_list, "w") as f:
    for pf in part_files:
        f.write(f"file '{os.path.basename(pf)}'\n")

subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list, "-c", "copy", output_wav], capture_output=True, cwd=args.output_dir)
# Keep part_*.wav and concat_list.txt for debugging - cleanup via Step 14
print(f"✓ 完成: {output_wav}")
print(f"  临时文件保留: {len(part_files)} 个 part_*.wav (手动清理: Step 14)")

# 生成 SRT 字幕
print("\n生成字幕...")
def format_time(seconds):
    h, m = int(seconds // 3600), int((seconds % 3600) // 60)
    s, ms = int(seconds % 60), int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

srt_lines = []
subtitle_idx = 1
current_text = ""
start_time = end_time = 0

for i, wb in enumerate(word_boundaries):
    if not current_text:
        start_time = wb["offset"]
    current_text += wb["text"]
    end_time = wb["offset"] + wb["duration"]

    is_strong = wb["text"] in ["。", "！", "？"]
    is_weak = wb["text"] in ["；", ",", "，"]
    is_last = i == len(word_boundaries) - 1
    text_len = len(current_text)

    should_break = is_last or (is_strong and text_len > 15) or (is_weak and text_len > 25) or text_len > 35

    if should_break:
        # 清理首尾标点
        clean_subtitle = re.sub(r'^[，。！？、：；""''…—\s]+|[，。！？、：；""''…—\s]+$', '', current_text.strip())
        if clean_subtitle:
            srt_lines.append(f"{subtitle_idx}\n{format_time(start_time)} --> {format_time(end_time)}\n{clean_subtitle}\n\n")
            subtitle_idx += 1
        current_text = ""

output_srt = os.path.join(args.output_dir, "podcast_audio.srt")
with open(output_srt, "w", encoding="utf-8") as f:
    f.writelines(srt_lines)
print(f"✓ 字幕: {output_srt} ({len(srt_lines)} 条)")

# 生成 timing.json 供 Remotion 使用
timing_data = {
    'total_duration': total_duration,
    'fps': 30,
    'total_frames': int(total_duration * 30),
    'speech_rate': SPEECH_RATE,
    'sections': [
        {
            'name': s['name'],
            'start_time': round(s['start_time'], 3),
            'end_time': round(s['end_time'], 3),
            'duration': round(s['duration'], 3),
            'start_frame': int(s['start_time'] * 30),
            'duration_frames': int(s['duration'] * 30),
            'is_silent': s.get('is_silent', False)
        }
        for s in sections
    ]
}

output_timing = os.path.join(args.output_dir, "timing.json")
with open(output_timing, "w", encoding="utf-8") as f:
    json.dump(timing_data, f, indent=2, ensure_ascii=False)

print(f"\n✓ 时间轴: {output_timing}")
print("\n章节时间:")
for s in timing_data['sections']:
    print(f"  {s['name']}: {s['start_time']:.1f}s - {s['end_time']:.1f}s ({s['duration']:.1f}s)")

print(f"\n总时长: {total_duration:.1f}s ({timing_data['total_frames']} frames @ 30fps)")
