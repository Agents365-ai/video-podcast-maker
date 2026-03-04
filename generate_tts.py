#!/usr/bin/env python3
"""
TTS Script for Video Podcast Maker (Azure + CosyVoice)
Generates audio from podcast.txt and creates SRT subtitles + timing.json for Remotion sync
"""
import os
import sys
import json
import argparse
import subprocess
import re
import time
import uuid
from xml.sax.saxutils import escape



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

    # Use placeholders to prevent nested replacements
    placeholders = {}
    result = text

    for i, word in enumerate(sorted_words):
        if word not in result:
            continue
        placeholder = f"__PH_{i}__"
        placeholders[placeholder] = (word, phoneme_dict[word])
        result = result.replace(word, placeholder)

    # Replace placeholders with actual phoneme tags
    for placeholder, (word, pinyin) in placeholders.items():
        sapi_pinyin = pinyin_to_sapi(pinyin)
        phoneme_tag = f'<phoneme alphabet="sapi" ph="{sapi_pinyin}">{word}</phoneme>'
        result = result.replace(placeholder, phoneme_tag)

    return result


# Built-in pronunciation fixes (技术术语 + 易错多音字)
BUILTIN_POLYPHONES = {
    # "行" as háng (row/line)
    '一行命令': 'yì háng mìng lìng',
    '一行代码': 'yì háng dài mǎ',
    '一行': 'yì háng',
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
    '重置': 'chóng zhì',
    # "行" as xíng (execute/walk)
    '执行器': 'zhí xíng qì',
    '执行': 'zhí xíng',
    '运行': 'yùn xíng',
    '并行': 'bìng xíng',
    '可行': 'kě xíng',
    '行为': 'xíng wéi',
    # 技术术语 (用户可扩展)
    # 添加更多...
}



parser = argparse.ArgumentParser(
    description='Generate TTS audio from podcast script',
    epilog='Environment: AZURE_SPEECH_KEY (required), AZURE_SPEECH_REGION (default: eastasia), TTS_RATE (default: +5%, range: -50% to +200%)'
)
parser.add_argument('--input', '-i', default='podcast.txt', help='Input script file (default: podcast.txt)')
parser.add_argument('--output-dir', '-o', default='.', help='Output directory for podcast_audio.wav, podcast_audio.srt, timing.json (default: current dir)')
parser.add_argument('--phonemes', '-p', default=None, help='Phoneme dictionary JSON file (default: phonemes.json in input dir)')
parser.add_argument('--backend', '-b', default=None,
    help='TTS backend: azure or cosyvoice (default: env TTS_BACKEND or azure)')

args = parser.parse_args()

BACKEND = args.backend or os.environ.get("TTS_BACKEND", "azure")
print(f"TTS backend: {BACKEND}")

if BACKEND == "azure":
    key = os.environ.get("AZURE_SPEECH_KEY")
    region = os.environ.get("AZURE_SPEECH_REGION", "eastasia")
    if not key:
        print("Error: AZURE_SPEECH_KEY not set", file=sys.stderr)
        sys.exit(1)
elif BACKEND == "cosyvoice":
    if not os.environ.get("DASHSCOPE_API_KEY"):
        print("Error: DASHSCOPE_API_KEY not set", file=sys.stderr)
        sys.exit(1)
else:
    print(f"Error: Unknown backend '{BACKEND}'. Use 'azure' or 'cosyvoice'", file=sys.stderr)
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


def synth_azure(chunks, phoneme_dict, speech_rate, output_dir):
    import azure.cognitiveservices.speech as speechsdk

    config = speechsdk.SpeechConfig(subscription=key, region=region)
    config.SpeechSynthesisVoiceName = "zh-CN-XiaoxiaoMultilingualNeural"
    part_files = []
    word_boundaries = []
    accumulated_duration = 0

    for i, chunk in enumerate(chunks):
        part_file = os.path.join(output_dir, f"part_{i}.wav")
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

        chunk_with_phonemes = apply_phonemes(chunk, phoneme_dict)
        processed = mark_english_terms(chunk_with_phonemes)

        ssml = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"
                   xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="zh-CN">
            <voice name="zh-CN-XiaoxiaoMultilingualNeural">
                <mstts:express-as style="gentle">
                    <prosody rate="{speech_rate}">{processed}</prosody>
                </mstts:express-as>
            </voice>
        </speak>"""

        success = False
        for attempt in range(1, 4):
            result = synth.speak_ssml_async(ssml).get()
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                chunk_duration = result.audio_duration.total_seconds()
                print(f"  ✓ Part {i + 1}/{len(chunks)} done ({len(chunk)} chars, {chunk_duration:.1f}s)")
                accumulated_duration += chunk_duration
                success = True
                break
            else:
                details = result.cancellation_details.error_details
                print(f"  ✗ Part {i + 1} failed (attempt {attempt}/3): {details}")
                if attempt < 3:
                    time.sleep(attempt * 2)

        if not success:
            raise RuntimeError(f"Part {i + 1} synthesis failed")

    return part_files, word_boundaries, accumulated_duration


def synth_cosyvoice(chunks, phoneme_dict, speech_rate, output_dir):
    import struct
    import json as _json
    from dashscope.audio.tts_v2 import SpeechSynthesizer, ResultCallback, AudioFormat

    # Convert speech rate from Azure format "+5%" to CosyVoice format 1.05
    rate_match = re.match(r'([+-]?\d+)%', speech_rate)
    cosy_rate = 1.0 + int(rate_match.group(1)) / 100.0 if rate_match else 1.0
    cosy_rate = max(0.5, min(2.0, cosy_rate))

    model = os.environ.get("COSYVOICE_MODEL", "cosyvoice-v3-flash")
    voice = os.environ.get("COSYVOICE_VOICE", "longxiaochun_v3")
    sample_rate = 48000

    part_files = []
    word_boundaries = []
    accumulated_duration = 0

    for i, chunk in enumerate(chunks):
        part_file = os.path.join(output_dir, f"part_{i}.wav")
        part_files.append(part_file)

        success = False
        for attempt in range(1, 4):
            try:
                audio_buf = bytearray()
                sentence_words = {}

                class Callback(ResultCallback):
                    def on_event(self, message):
                        d = _json.loads(message)
                        sentence = d.get('payload', {}).get('output', {}).get('sentence', {})
                        words = sentence.get('words', [])
                        idx = sentence.get('index', 0)
                        if words:
                            sentence_words[idx] = words
                    def on_data(self, data):
                        audio_buf.extend(data)
                    def on_error(self, message):
                        raise RuntimeError(f"CosyVoice error: {message}")

                synth = SpeechSynthesizer(
                    model=model,
                    voice=voice,
                    format=AudioFormat.PCM_48000HZ_MONO_16BIT,
                    speech_rate=cosy_rate,
                    callback=Callback(),
                    additional_params={'word_timestamp_enabled': True},
                )
                synth.streaming_call(chunk)
                synth.streaming_complete()

                if not audio_buf:
                    raise RuntimeError("No audio data received")

                # Write proper WAV from PCM
                pcm_data = bytes(audio_buf)
                data_size = len(pcm_data)
                wav_header = struct.pack('<4sI4s4sIHHIIHH4sI',
                    b'RIFF', 36 + data_size, b'WAVE',
                    b'fmt ', 16, 1, 1, sample_rate,
                    sample_rate * 2, 2, 16,
                    b'data', data_size)
                with open(part_file, 'wb') as f:
                    f.write(wav_header + pcm_data)

                chunk_duration = data_size / (sample_rate * 2)

                # Convert deduplicated word timestamps to word_boundaries format
                for idx in sorted(sentence_words.keys()):
                    for w in sentence_words[idx]:
                        word_boundaries.append({
                            "text": w["text"],
                            "offset": accumulated_duration + w["begin_time"] / 1000.0,
                            "duration": (w["end_time"] - w["begin_time"]) / 1000.0,
                        })

                print(f"  ✓ Part {i + 1}/{len(chunks)} done ({len(chunk)} chars, {chunk_duration:.1f}s)")
                accumulated_duration += chunk_duration
                success = True
                break
            except Exception as e:
                print(f"  ✗ Part {i + 1} failed (attempt {attempt}/3): {e}")
                if attempt < 3:
                    time.sleep(attempt * 2)

        if not success:
            raise RuntimeError(f"Part {i + 1} synthesis failed")

    return part_files, word_boundaries, accumulated_duration


# TTS synthesis
if BACKEND == "azure":
    part_files, word_boundaries, total_duration = synth_azure(chunks, phoneme_dict, SPEECH_RATE, args.output_dir)
elif BACKEND == "cosyvoice":
    part_files, word_boundaries, total_duration = synth_cosyvoice(chunks, phoneme_dict, SPEECH_RATE, args.output_dir)
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
