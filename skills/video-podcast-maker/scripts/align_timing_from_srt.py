#!/usr/bin/env python3
"""Align an existing timing.json to the actual audio/SRT timestamps.

This performs slide-level alignment: every slide's start time is anchored to
the real moment its content first appears in the synthesized audio/subtitles,
but only within its parent section's time range. If a slide cannot be matched,
it falls back to section-level proportional distribution.

Usage:
  python3 align_timing_from_srt.py videos/<name>
  python3 align_timing_from_srt.py videos/<name> --dry-run

Outputs:
  videos/<name>/timing.json        overwritten with aligned timing
  videos/<name>/timing.json.bak    backup of the original

The in-place rewrite is exempt from the suite's --yes gate (same rationale
as verify_output.py auto-fix): timing.json is a regenerable artifact, the
original is preserved in timing.json.bak, and --dry-run previews the result.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from bisect import bisect_left, bisect_right
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cli_envelope  # noqa: E402


def ffprobe_duration(wav_path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(wav_path)],
        capture_output=True, text=True, check=True,
    )
    return float(result.stdout.strip())


def clean_text(text: str) -> str:
    if not text:
        return ""
    return re.sub(r"[^一-鿿A-Za-z0-9]", "", text).lower()


def parse_srt(path: Path):
    entries = []
    pattern = re.compile(
        r"\d+\s+"
        r"(\d{2}):(\d{2}):(\d{2}),(\d{3}) --> \d{2}:\d{2}:\d{2},\d{3}\s+"
        r"(.+?)(?=\n\n|\Z)",
        re.S,
    )
    text = path.read_text(encoding="utf-8")
    for m in pattern.finditer(text):
        h, mn, s, ms = map(int, m.groups()[:4])
        start = h * 3600 + mn * 60 + s + ms / 1000.0
        body = m.group(5).replace("\n", " ").strip()
        entries.append({"start": start, "text": body, "clean": clean_text(body)})
    return entries


def build_srt_index(entries):
    concat = ""
    offsets = []
    for e in entries:
        offsets.append(len(concat))
        concat += e["clean"]
    return concat, offsets


def find_all_in_srt(key: str, concat: str, offsets, entries, start_idx: int, end_idx: int):
    """Return all (entry_index, start_time, matched_length) matches for key within [start_idx, end_idx]."""
    matches = []
    if len(key) < 4 or start_idx >= len(entries) or end_idx <= start_idx:
        return matches
    search_from = offsets[start_idx]
    search_to = offsets[min(end_idx, len(entries) - 1)] if end_idx < len(entries) else len(concat)

    pos = concat.find(key, search_from)
    while pos != -1 and pos < search_to:
        idx = max(0, min(len(entries) - 1, bisect_right(offsets, pos) - 1))
        idx = max(idx, start_idx)
        idx = min(idx, end_idx - 1)
        matches.append((idx, entries[idx]["start"], len(key)))
        pos = concat.find(key, pos + 1)
    return matches


def parse_podcast_sections(path: Path):
    text = path.read_text(encoding="utf-8")
    matches = list(re.finditer(r"\[SECTION:(\w[\w-]*)\]", text))
    sections = []
    for i, m in enumerate(matches):
        name = m.group(1)
        start_pos = m.end()
        end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start_pos:end_pos].strip()
        first_text = re.sub(r"\s+", "", content[:80])
        sections.append({"name": name, "first_text": first_text})
    return sections


def _extract_bullets(slide: dict) -> list[str]:
    bullets = slide.get("bullets") or []
    if isinstance(bullets, str):
        return [bullets]
    return [str(b) for b in bullets]


def build_search_keys(slide: dict) -> list[str]:
    """Build a list of search keys for a slide, from specific to generic."""
    raw_keys = []
    for field in ("headline", "sub", "body"):
        val = slide.get(field)
        if val and isinstance(val, str):
            raw_keys.append(val)
    raw_keys.extend(_extract_bullets(slide))

    keys = []
    seen = set()
    for raw in raw_keys:
        cleaned = clean_text(raw)
        if len(cleaned) >= 4 and cleaned not in seen:
            keys.append(cleaned)
            seen.add(cleaned)

    # Fallback: split long text into shorter phrases.
    for raw in raw_keys:
        parts = re.split(r"[，。！？、：；]", raw)
        for p in parts:
            cleaned = clean_text(p)
            if len(cleaned) >= 4 and cleaned not in seen:
                keys.append(cleaned)
                seen.add(cleaned)
    return keys


def find_section_entry_index(start_time: float, entries):
    """Find the first SRT entry whose start >= start_time."""
    idx = bisect_left([e["start"] for e in entries], start_time)
    return min(idx, len(entries) - 1)


def find_real_section_starts(script_sections, entries, concat, offsets, real_duration):
    """Anchor each [SECTION:name] to its first appearance in SRT.

    Prefer the longest substring match to avoid matching a generic phrase that
    also appears in an earlier section before its dedicated section begins.

    Returns a list of dicts with keys: name, start_time, matched.
    """
    real_starts = []
    cursor = 0
    for sec in script_sections:
        key = clean_text(sec["first_text"])[:120]
        matches = find_all_in_srt(key, concat, offsets, entries, cursor, len(entries))
        if matches:
            # Sort by matched substring length (longest first), then earliest time.
            matches.sort(key=lambda m: (m[2], -m[1]), reverse=True)
            cursor, start_time, _ = matches[0]
            cursor += 1
            matched = True
        else:
            start_time = None
            matched = False
        real_starts.append({"name": sec["name"], "start_time": start_time, "matched": matched})

    # Trailing silent sections (empty content, e.g. [SECTION:outro]) never
    # appear in the SRT. Anchor them to the end of the audio — the
    # proportional estimate below would place them mid-audio, and the
    # monotonic clamp would then collapse the previous section's window
    # to the 0.2s minimum, squeezing all of its slides together.
    idx = len(script_sections)
    while idx > 0 and not script_sections[idx - 1]["first_text"] \
            and real_starts[idx - 1]["start_time"] is None:
        real_starts[idx - 1]["start_time"] = real_duration
        idx -= 1

    # Fill missing values with proportional estimates.
    n_sections = len(script_sections)
    last_entry_start = entries[-1]["start"] if entries else 0
    for idx, sec in enumerate(script_sections):
        if real_starts[idx]["start_time"] is not None:
            continue
        target_ratio = idx / n_sections if n_sections else 0
        real_starts[idx]["start_time"] = target_ratio * last_entry_start

    for i in range(len(real_starts)):
        real_starts[i]["start_time"] = max(0.0, real_starts[i]["start_time"])
    for i in range(1, len(real_starts)):
        real_starts[i]["start_time"] = max(
            real_starts[i]["start_time"],
            real_starts[i - 1]["start_time"] + 0.2,
        )
    return real_starts


def map_slides_to_sections(slides, script_sections, real_starts, real_duration):
    """Map each slide to a section index. Prefer explicit 'section' field."""
    section_name_to_idx = {s["name"]: i for i, s in enumerate(script_sections)}
    section_boundaries = [s["start_time"] for s in real_starts] + [real_duration]

    def original_start(slide):
        fps = slide.get("fps", 30)
        return slide.get("start_time", slide.get("start_frame", 0) / fps)

    mappings = []
    using_explicit = 0
    for slide in slides:
        sec_name = slide.get("section")
        if sec_name and sec_name in section_name_to_idx:
            mappings.append(section_name_to_idx[sec_name])
            using_explicit += 1
        else:
            orig = original_start(slide)
            idx = bisect_right(section_boundaries, orig) - 1
            idx = max(0, min(idx, len(script_sections) - 1))
            mappings.append(idx)

    return mappings, using_explicit


def pick_monotonic_matches(slides, slide_indices, keys_list, entries, concat, offsets,
                           sec_start, sec_end, orig_starts):
    """For slides in one section, pick a monotonic sequence of SRT matches."""
    start_idx = find_section_entry_index(sec_start, entries)
    end_idx = find_section_entry_index(sec_end, entries)
    if end_idx < len(entries) - 1:
        end_idx += 1

    n = len(slide_indices)
    # candidates[i] = list of (srt_idx, time) for slide i
    candidates = []
    for i, slide_idx in enumerate(slide_indices):
        cands = []
        for key in keys_list[slide_idx]:
            cands.extend(find_all_in_srt(key, concat, offsets, entries, start_idx, end_idx))
        # Deduplicate and keep earliest per srt_idx.
        seen = set()
        unique = []
        for srt_idx, t, _ in sorted(cands, key=lambda x: x[1]):
            if srt_idx not in seen:
                unique.append((srt_idx, t))
                seen.add(srt_idx)
        # Prefer candidates close to original start_time.
        orig = orig_starts[slide_idx]
        unique.sort(key=lambda x: (abs(x[1] - orig), x[1]))
        candidates.append(unique[:10])  # limit search space

    # Greedy monotonic pick is usually enough within one section.
    chosen = [None] * n
    last_time = sec_start
    for i in range(n):
        valid = [(idx, t) for idx, t in candidates[i] if t >= last_time + 0.1]
        if valid:
            # Pick the earliest valid candidate.
            chosen[i] = min(valid, key=lambda x: x[1])
            last_time = chosen[i][1]
        else:
            chosen[i] = None
    return chosen


def distribute_section_time_across_slides(slides, slide_indices, sec_start, sec_end,
                                           already_matched):
    """Fill unmatched slides in a section proportionally around matched anchors."""
    n = len(slide_indices)
    starts = [None] * n

    # Lock in matched positions.
    for i, m in enumerate(already_matched):
        if m is not None:
            starts[i] = m[1]

    # Forward fill: between matched anchors, distribute proportionally.
    # First, assign original durations.
    orig_durs = [max(0.01, slides[slide_indices[i]].get("duration", 1.0)) for i in range(n)]

    # If first slides are unmatched, distribute from sec_start to first match.
    i = 0
    while i < n and starts[i] is None:
        i += 1
    if i > 0:
        first_match_time = starts[i] if i < n else sec_end
        available = first_match_time - sec_start
        total_orig = sum(orig_durs[j] for j in range(i))
        scale = available / total_orig if total_orig > 0 else 0
        t = sec_start
        for j in range(i):
            starts[j] = t
            t += orig_durs[j] * scale

    # Between matches.
    prev_matched = i if i < n and starts[i] is not None else None
    for j in range(i + 1, n):
        if starts[j] is not None:
            if prev_matched is not None:
                available = starts[j] - starts[prev_matched]
                total_orig = sum(orig_durs[k] for k in range(prev_matched, j))
                scale = available / total_orig if total_orig > 0 else 0
                t = starts[prev_matched]
                for k in range(prev_matched + 1, j):
                    t += orig_durs[k] * scale
                    starts[k] = t
            prev_matched = j

    # Tail unmatched after last match.
    if prev_matched is not None and prev_matched < n - 1:
        available = sec_end - starts[prev_matched]
        total_orig = sum(orig_durs[k] for k in range(prev_matched, n))
        scale = available / total_orig if total_orig > 0 else 0
        t = starts[prev_matched]
        for k in range(prev_matched + 1, n):
            t += orig_durs[k] * scale
            starts[k] = t

    # All unmatched.
    if all(s is None for s in starts):
        total_orig = sum(orig_durs)
        available = sec_end - sec_start
        scale = available / total_orig if total_orig > 0 else 0
        t = sec_start
        for j in range(n):
            starts[j] = t
            t += orig_durs[j] * scale

    return [s if s is not None else sec_start for s in starts]


def align_timing(video_dir: Path, dry_run: bool = False):
    """Align timing.json to the real audio/SRT. Returns a structured result dict.

    Raises FileNotFoundError for missing inputs, ValueError for malformed inputs,
    and propagates subprocess.CalledProcessError if ffprobe fails.
    """
    timing_path = video_dir / "timing.json"
    srt_path = video_dir / "podcast_audio.srt"
    wav_path = video_dir / "podcast_audio.wav"
    podcast_path = video_dir / "podcast.txt"
    backup_path = video_dir / "timing.json.bak"

    for p in (timing_path, srt_path, wav_path, podcast_path):
        if not p.exists():
            raise FileNotFoundError(f"{p.name} not found: {p}")

    timing = json.loads(timing_path.read_text(encoding="utf-8"))
    slides = timing.get("sections", timing.get("slides", []))
    if not slides:
        raise ValueError("timing.json contains no sections/slides")

    fps = timing.get("fps", 30)
    real_duration = ffprobe_duration(wav_path)
    entries = parse_srt(srt_path)
    concat, offsets = build_srt_index(entries)
    script_sections = parse_podcast_sections(podcast_path)
    if not script_sections:
        raise ValueError("podcast.txt has no [SECTION:name] markers")

    # --- Step 1: initial section anchors from first_text matching ---
    real_starts = find_real_section_starts(script_sections, entries, concat, offsets, real_duration)

    # Pre-compute search keys and original starts.
    keys_list = [build_search_keys(s) for s in slides]
    orig_starts = [s.get("start_time", s.get("start_frame", 0) / fps) for s in slides]

    # --- Step 2: iterative slide-level alignment + section boundary refinement ---
    final_starts = [0.0] * len(slides)
    matched_flags = [False] * len(slides)
    slide_to_section = [0] * len(slides)
    using_explicit = 0

    for iteration in range(2):
        section_ends = [real_starts[i + 1]["start_time"] if i + 1 < len(real_starts) else real_duration
                        for i in range(len(real_starts))]

        slide_to_section, using_explicit = map_slides_to_sections(
            slides, script_sections, real_starts, real_duration
        )

        # Reset per-iteration state.
        final_starts = [0.0] * len(slides)
        matched_flags = [False] * len(slides)

        for sec_idx, sec in enumerate(script_sections):
            slide_indices = [i for i, s_idx in enumerate(slide_to_section) if s_idx == sec_idx]
            if not slide_indices:
                continue

            sec_start = real_starts[sec_idx]["start_time"]
            sec_end = section_ends[sec_idx]

            chosen = pick_monotonic_matches(
                slides, slide_indices, keys_list, entries, concat, offsets,
                sec_start, sec_end, orig_starts
            )

            # Refine section start from the first SLIDE's real match (not any slide).
            # Only the first slide's appearance in audio defines when the section
            # visually begins. If the first slide has no match, keep current estimate.
            first_match = chosen[0]

            # First section always begins the video at 0.
            if sec_idx == 0:
                real_starts[0]["start_time"] = 0.0
                sec_start = 0.0
            elif first_match is not None:
                new_start = first_match[1]
                prev_end = real_starts[sec_idx - 1]["start_time"] if sec_idx > 0 else 0.0
                next_start = real_starts[sec_idx + 1]["start_time"] if sec_idx + 1 < len(real_starts) else real_duration
                lower_bound = prev_end + 0.2
                upper_bound = next_start - 0.2

                is_matched = real_starts[sec_idx].get("matched", False)
                if is_matched:
                    if new_start < sec_start - 0.5 and new_start >= lower_bound:
                        real_starts[sec_idx]["start_time"] = new_start
                        sec_start = new_start
                else:
                    if abs(new_start - sec_start) > 0.5 and lower_bound <= new_start <= upper_bound:
                        real_starts[sec_idx]["start_time"] = new_start
                        sec_start = new_start

            # Always anchor the first slide of a section to the section boundary.
            chosen[0] = (find_section_entry_index(sec_start, entries), sec_start)

            starts = distribute_section_time_across_slides(
                slides, slide_indices, sec_start, sec_end, chosen
            )

            for pos, slide_idx in enumerate(slide_indices):
                final_starts[slide_idx] = starts[pos]
                real_match = first_match if pos == 0 else chosen[pos]
                if real_match is not None:
                    matched_flags[slide_idx] = True

        # Enforce section monotonicity after refinement.
        for i in range(1, len(real_starts)):
            real_starts[i]["start_time"] = max(
                real_starts[i]["start_time"],
                real_starts[i - 1]["start_time"] + 0.2,
            )

    # --- Step 3: enforce slide-level monotonicity and minimum gap ---
    for i in range(1, len(final_starts)):
        if final_starts[i] <= final_starts[i - 1] + 0.15:
            final_starts[i] = final_starts[i - 1] + 0.15
    if final_starts and final_starts[-1] >= real_duration:
        final_starts[-1] = real_duration - 0.2

    # --- Step 4: write back ---
    for i, start in enumerate(final_starts):
        end = final_starts[i + 1] if i + 1 < len(final_starts) else real_duration
        dur = max(0.15, end - start)
        slides[i]["start_time"] = round(start, 3)
        slides[i]["end_time"] = round(end, 3)
        slides[i]["duration"] = round(dur, 3)
        slides[i]["start_frame"] = int(start * fps)
        slides[i]["duration_frames"] = int(dur * fps)

    timing["total_duration"] = round(real_duration, 3)
    timing["total_frames"] = int(real_duration * fps)

    # --- Report (human-readable; goes to stderr in JSON mode) ---
    matched_count = sum(matched_flags)
    print(f"Audio duration: {real_duration:.3f}s")
    print(f"Slides matched to SRT: {matched_count}/{len(slides)}")
    print(f"Slides using section fallback: {len(slides) - matched_count}")
    if using_explicit:
        print(f"Slides with explicit 'section' field: {using_explicit}/{len(slides)}")

    slide_report = []
    for i, slide in enumerate(slides):
        sec_name = script_sections[slide_to_section[i]]["name"]
        label = slide.get("headline") or slide.get("title") or slide.get("name") or "?"
        source = "SRT" if matched_flags[i] else "fallback"
        print(
            f"  [{sec_name}] {slide['start_time']:7.2f}s - {slide['end_time']:7.2f}s  "
            f"({source}) {label}"[:120]
        )
        slide_report.append({
            "section": sec_name,
            "start": slide["start_time"],
            "end": slide["end_time"],
            "source": source,
            "label": str(label)[:60],
        })

    written = False
    if not dry_run:
        if not backup_path.exists():
            backup_path.write_text(
                json.dumps(json.loads(timing_path.read_text(encoding="utf-8")), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        timing_path.write_text(json.dumps(timing, indent=2, ensure_ascii=False), encoding="utf-8")
        written = True
        print(f"\n✅ Aligned timing.json written. Original backed up to {backup_path}")
    else:
        print("\n(Dry run — no files written)")

    return {
        "video_dir": str(video_dir),
        "audio_duration": round(real_duration, 3),
        "slides_total": len(slides),
        "slides_matched_srt": matched_count,
        "slides_fallback": len(slides) - matched_count,
        "slides_explicit_section": using_explicit,
        "dry_run": dry_run,
        "written": written,
        "backup_path": str(backup_path) if written else None,
        "slides": slide_report,
    }


def build_parser():
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0],
        prog="align_timing_from_srt.py",
    )
    parser.add_argument("video_dir", help="Path to videos/<name> directory")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print report without writing timing.json")
    cli_envelope.add_format_arg(parser)
    return parser


def main():
    started_at = time.time()
    args = build_parser().parse_args()
    video_dir = Path(args.video_dir)

    if shutil.which("ffprobe") is None:
        return cli_envelope.emit_error(
            args, "tool_missing",
            "ffprobe not found on PATH; install ffmpeg to read audio duration.",
            started_at=started_at,
        )

    # Silence the human report in JSON mode so it can't bleed into the envelope.
    json_mode = cli_envelope.use_json(args)
    if json_mode:
        sys.stdout = sys.stderr
    try:
        result = align_timing(video_dir, dry_run=args.dry_run)
    except FileNotFoundError as exc:
        return cli_envelope.emit_error(args, "input_not_found", str(exc),
                                       started_at=started_at)
    except (ValueError, json.JSONDecodeError) as exc:
        return cli_envelope.emit_error(args, "input_invalid", str(exc),
                                       started_at=started_at)
    except subprocess.CalledProcessError as exc:
        return cli_envelope.emit_error(args, "ffmpeg_failed",
                                       f"ffprobe failed on podcast_audio.wav: {exc}",
                                       started_at=started_at)
    except Exception as exc:
        return cli_envelope.emit_error(args, "internal_error", str(exc),
                                       started_at=started_at)
    finally:
        sys.stdout = sys.__stdout__

    return cli_envelope.emit_success(args, result, started_at=started_at)


if __name__ == "__main__":
    sys.exit(main())
