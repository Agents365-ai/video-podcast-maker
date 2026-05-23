"""SRT subtitle and timing.json generation."""
import os
import re
import json
import subprocess


def format_time(seconds):
    """Format seconds to SRT timestamp: HH:MM:SS,mmm"""
    h, m = int(seconds // 3600), int((seconds % 3600) // 60)
    s, ms = int(seconds % 60), int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


# Punctuation sets for Chinese subtitle breaking
STRONG_PUNCTS = set("。！？")     # Sentence-ending punctuation
WEAK_PUNCTS = set("，；、：")      # Clause-separating punctuation
ALL_PUNCTS = STRONG_PUNCTS | WEAK_PUNCTS


def write_srt(word_boundaries, output_path):
    """Generate SRT subtitle file from word boundaries.

    Strategy: accumulate words into a buffer, break at natural punctuation
    boundaries to produce complete sentences or phrases. When forced to break
    (text too long), backtrack to the last punctuation position instead of
    cutting mid-phrase.
    """
    srt_lines = []
    subtitle_idx = 1

    # Buffer: list of (text, offset, duration) tuples
    buf = []
    buf_text = ""

    def flush(entries):
        """Write accumulated entries as one subtitle line."""
        nonlocal subtitle_idx
        if not entries:
            return
        text = "".join(e[0] for e in entries)
        clean = re.sub(r"""^[，。！？、：；""''…—\s]+|[，。！？、：；""''…—\s]+$""", '', text.strip())
        if not clean:
            return
        start = entries[0][1]
        last = entries[-1]
        end = last[1] + last[2]
        srt_lines.append(f"{subtitle_idx}\n{format_time(start)} --> {format_time(end)}\n{clean}\n\n")
        subtitle_idx += 1

    def find_last_punct_index(entries, punct_set):
        """Find the index of the last entry whose text is in punct_set."""
        for j in range(len(entries) - 1, -1, -1):
            if entries[j][0] in punct_set:
                return j
        return -1

    for i, wb in enumerate(word_boundaries):
        buf.append((wb["text"], wb["offset"], wb["duration"]))
        buf_text += wb["text"]
        text_len = len(buf_text)
        is_last = i == len(word_boundaries) - 1

        is_strong = wb["text"] in STRONG_PUNCTS
        is_weak = wb["text"] in WEAK_PUNCTS

        should_break = False
        if is_last:
            should_break = True
        elif is_strong and text_len >= 10:
            # Break at sentence end if we have enough text
            should_break = True
        elif is_weak and text_len >= 20:
            # Break at comma/semicolon if reasonably long
            should_break = True
        elif text_len >= 40:
            # Forced break — but backtrack to last punctuation
            # Try strong punctuation first, then weak
            strong_idx = find_last_punct_index(buf, STRONG_PUNCTS)
            weak_idx = find_last_punct_index(buf, WEAK_PUNCTS)
            break_idx = strong_idx if strong_idx >= 0 else weak_idx

            if break_idx >= 0 and break_idx > 0:
                # Split: flush up to break_idx (inclusive), keep the rest
                flush(buf[:break_idx + 1])
                remaining = buf[break_idx + 1:]
                buf = remaining
                buf_text = "".join(e[0] for e in buf)
                continue
            else:
                # No punctuation found at all — hard break
                should_break = True

        if should_break:
            flush(buf)
            buf = []
            buf_text = ""

    # Flush any remaining
    flush(buf)

    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(srt_lines)
    print(f"Subtitles: {output_path} ({len(srt_lines)} entries)")


def write_timing(sections, total_duration, speech_rate, output_path):
    """Generate timing.json for Remotion sync."""
    timing_data = {
        'total_duration': total_duration,
        'fps': 30,
        'total_frames': int(total_duration * 30),
        'speech_rate': speech_rate,
        'sections': [
            {
                'name': s['name'],
                'label': s.get('label', s['name']),
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

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(timing_data, f, indent=2, ensure_ascii=False)

    print(f"\nTiming: {output_path}")
    print("\nSection times:")
    for s in timing_data['sections']:
        print(f"  {s['name']}: {s['start_time']:.1f}s - {s['end_time']:.1f}s ({s['duration']:.1f}s)")
    print(f"\nTotal duration: {total_duration:.1f}s ({timing_data['total_frames']} frames @ 30fps)")


def ffprobe_duration(wav_path):
    """Return WAV duration in seconds via ffprobe, or None if probe fails."""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
             '-of', 'csv=p=0', wav_path],
            capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except (subprocess.CalledProcessError, ValueError, FileNotFoundError):
        return None


def reconcile_timing_with_wav(timing_path, wav_path, drift_threshold=0.5):
    """Reconcile timing.json with the actual concatenated WAV duration.

    Azure (and other backends) sometimes under-report `audio_duration` when SSML
    tags like <break>, <phoneme>, or nested <lang>/<say-as> are present. Without
    reconciliation, timing.json drifts from the real audio — sections shift
    earlier than they should and the last seconds get cut off in Remotion.

    Strategy: ffprobe the actual WAV. If drift > threshold, scale every
    section's start/end/duration uniformly. Cheap and conservative — preserves
    relative section proportions exactly.

    Returns: (scale_factor, real_duration) or (1.0, reported) if no rescale.
    """
    real = ffprobe_duration(wav_path)
    if real is None:
        print(f"Warning: ffprobe failed on {wav_path}; timing.json left unchanged")
        return 1.0, None
    with open(timing_path, 'r', encoding='utf-8') as f:
        timing = json.load(f)
    reported = timing['total_duration']
    drift = real - reported
    if abs(drift) < drift_threshold:
        print(f"Timing OK: ffprobe {real:.2f}s vs reported {reported:.2f}s (drift {drift:+.2f}s)")
        return 1.0, real
    scale = real / reported
    fps = timing.get('fps', 30)
    for s in timing['sections']:
        s['start_time'] = round(s['start_time'] * scale, 3)
        s['end_time'] = round(s['end_time'] * scale, 3)
        s['duration'] = round(s['duration'] * scale, 3)
        s['start_frame'] = int(s['start_time'] * fps)
        s['duration_frames'] = int(s['duration'] * fps)
    timing['total_duration'] = real
    timing['total_frames'] = int(real * fps)
    with open(timing_path, 'w', encoding='utf-8') as f:
        json.dump(timing, f, indent=2, ensure_ascii=False)
    print(f"Timing rescaled: scale={scale:.4f}  reported {reported:.2f}s -> actual {real:.2f}s  (drift {drift:+.2f}s)")
    print(f"  -> {timing['total_frames']} frames @ {fps}fps")
    return scale, real
