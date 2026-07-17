#!/usr/bin/env python3
"""Audit alignment between kinetic-typography beats in a Remotion .tsx file
and the actual narration timing recorded in podcast_audio.srt.

Why this exists
---------------
Beat scheduling in kinetic-typography videos works best when each beat's
`startSec` is sourced from the SRT timestamps (where the narrator actually
says the corresponding words). Estimating with relative weights — even good
ones — drifts by 2-5 seconds per section, which is enough to make the visible
text lag the audio by a full punch line.

This script reads the beat data from your video component, joins it with the
SRT, and prints a side-by-side report showing what's on screen vs what the
narrator is saying at each beat. Flags any beat where the time gap to the
nearest matching SRT entry exceeds a threshold.

Usage
-----
  python3 audit_beat_sync.py <video.tsx> <timing.json> [<podcast_audio.srt>]

If the SRT path is omitted, it's resolved from the timing.json directory.

Beat data format expected in the .tsx file:
  - Top-level const arrays named like  HERO_BEATS / ENTRY_CHEAP_BEATS / ...
  - Each beat is a JS object literal with  startSec: <number>, lines: [...]
  - Section ↔ beat-array mapping comes from SECTION_CONFIG (a top-level const
    object literal), with `name` matching the section name in timing.json.

If your video uses different conventions, adapt the regexes near the top.
"""
from __future__ import annotations
import argparse
import sys
import re
import json
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cli_envelope  # noqa: E402


# Regex helpers -------------------------------------------------------------

# Match: const HERO_BEATS: Beat[] = [ ... ]
_BEATS_CONST = re.compile(
    r'const\s+([A-Z][A-Z0-9_]*_BEATS)\s*[:=][^=]*=\s*\[(.*?)\n\]\s*$',
    re.DOTALL | re.MULTILINE)

# Match a single beat object: { ... startSec: 1.23 ... lines: [ ... ] ... }
_BEAT_OBJECT = re.compile(
    r'\{\s*([^{}]*?startSec\s*:\s*[\d.]+[^{}]*?lines\s*:\s*\[[^\]]*?\][^{}]*?)\}',
    re.DOTALL)

# Match SECTION_CONFIG mapping: { hero: { beats: HERO_BEATS, ... }, ... }
_SECTION_CONFIG = re.compile(
    r'const\s+SECTION_CONFIG[^=]*=\s*\{(.*?)\n\}\s*$',
    re.DOTALL | re.MULTILINE)

_CONFIG_ENTRY = re.compile(
    r'(\w+)\s*:\s*\{\s*beats\s*:\s*([A-Z][A-Z0-9_]*_BEATS)',
    re.DOTALL)


def parse_beats(tsx_text: str):
    """Return {name: BEATS_NAME} and {BEATS_NAME: [(startSec, summary), ...]}."""
    name_to_beats = {}
    beats_arrays = {}

    for m in _BEATS_CONST.finditer(tsx_text):
        beats_name = m.group(1)
        body = m.group(2)
        items = []
        for bm in _BEAT_OBJECT.finditer(body):
            obj_body = bm.group(1)
            start = re.search(r'startSec\s*:\s*([\d.]+)', obj_body)
            if not start:
                continue
            start_sec = float(start.group(1))
            # Extract human-readable summary of beat lines
            lines = re.findall(r"t\s*:\s*['\"](.*?)['\"]", obj_body)
            summary = ' / '.join(lines)
            items.append((start_sec, summary))
        beats_arrays[beats_name] = items

    cm = _SECTION_CONFIG.search(tsx_text)
    if cm:
        for em in _CONFIG_ENTRY.finditer(cm.group(1)):
            name_to_beats[em.group(1)] = em.group(2)

    return name_to_beats, beats_arrays


# SRT helpers ---------------------------------------------------------------

_SRT_BLOCK = re.compile(
    r'\d+\n(\d+:\d+:\d+),(\d+)\s*-->\s*(\d+:\d+:\d+),(\d+)\n(.+?)(?=\n\n|\Z)',
    re.DOTALL)


def parse_srt(srt_text: str):
    """Return list of (start_sec, end_sec, text) tuples."""
    out = []
    for m in _SRT_BLOCK.finditer(srt_text):
        h, mn, s = m.group(1).split(':')
        ms = m.group(2)
        start = int(h) * 3600 + int(mn) * 60 + int(s) + int(ms) / 1000.0
        h2, mn2, s2 = m.group(3).split(':')
        end = int(h2) * 3600 + int(mn2) * 60 + int(s2) + int(m.group(4)) / 1000.0
        text = m.group(5).strip().replace('\n', ' ')
        out.append((start, end, text))
    return out


def srt_overlap(subs, range_start, range_end):
    """Return all SRT entries overlapping the given range, as concatenated text."""
    parts = []
    for st, en, txt in subs:
        if en <= range_start or st >= range_end:
            continue
        parts.append(txt)
    return ' / '.join(parts)


# Main ----------------------------------------------------------------------

def audit(tsx_path, timing_path, srt_path, drift_warn=1.5):
    """Run the audit. Returns (issues_count, result_dict).

    Raises ValueError if no SECTION_CONFIG entries with `beats:` are found
    in the .tsx — main() converts this into an 'input_invalid' envelope.
    """
    tsx_text = open(tsx_path, 'r', encoding='utf-8').read()
    timing = json.loads(open(timing_path, 'r', encoding='utf-8').read())
    srt_text = open(srt_path, 'r', encoding='utf-8').read()
    subs = parse_srt(srt_text)

    name_to_beats, beats_arrays = parse_beats(tsx_text)

    if not name_to_beats:
        raise ValueError(
            f"No SECTION_CONFIG entries with `beats:` found in {tsx_path}"
        )

    # Header
    print(f"\nAudit: {os.path.basename(tsx_path)}")
    print(f"  timing.json: {timing['total_duration']:.2f}s, {len(timing['sections'])} sections")
    print(f"  SRT: {len(subs)} subtitle entries")
    print('=' * 100)

    issues = 0
    section_records = []
    for sec in timing['sections']:
        name = sec['name']
        beats_name = name_to_beats.get(name)
        if not beats_name:
            print(f"\n[{name}] no beats array mapped (skipped)")
            section_records.append({
                "name": name, "beats_array": None,
                "status": "no_mapping", "beats": [],
            })
            continue
        items = beats_arrays.get(beats_name, [])
        if not items:
            print(f"\n[{name}] beats array '{beats_name}' empty or unparseable")
            section_records.append({
                "name": name, "beats_array": beats_name,
                "status": "unparseable", "beats": [],
            })
            continue
        sec_start = sec['start_time']
        sec_end = sec['start_time'] + sec['duration']
        print(f"\n[{name}]  {sec_start:.2f}-{sec_end:.2f}s  ({len(items)} beats)")
        print(f"  {'BEAT-START':>10}  {'SHOWN':<32}  {'NARRATION (overlap)':<60}")
        beat_records = []
        items_sorted = sorted(items, key=lambda x: x[0])
        for i, (start_sec, shown) in enumerate(items_sorted):
            abs_start = sec_start + start_sec
            next_start = sec_start + items_sorted[i + 1][0] if i + 1 < len(items_sorted) else sec_end
            narration = srt_overlap(subs, abs_start, next_start)
            shown_short = shown[:30] + '..' if len(shown) > 32 else shown
            narr_short = narration[:58] + '..' if len(narration) > 60 else narration
            flag = ''
            # Heuristic warning: beat starts too far from any SRT entry start
            nearest = min((abs(s - abs_start) for s, _, _ in subs), default=99)
            beat_ok = nearest <= drift_warn
            if not beat_ok:
                flag = f' ⚠ drift {nearest:.1f}s'
                issues += 1
            print(f"  {abs_start:6.2f}s+0  {shown_short:<32}  {narr_short:<60}{flag}")
            beat_records.append({
                "start_sec_relative": round(start_sec, 2),
                "start_sec_absolute": round(abs_start, 2),
                "shown": shown,
                "narration_overlap": narration,
                "nearest_srt_distance_seconds": round(nearest, 2),
                "ok": beat_ok,
            })
        section_records.append({
            "name": name, "beats_array": beats_name,
            "status": "audited", "beats": beat_records,
        })

    print('\n' + '=' * 100)
    if issues:
        print(f"⚠️  {issues} beats more than {drift_warn}s away from nearest SRT boundary.")
        print("   Consider adjusting their startSec to match a nearby SRT entry start.")
    else:
        print("✅ All beats land within {:.1f}s of an SRT boundary.".format(drift_warn))

    audited = [r for r in section_records if r['status'] == 'audited']
    result = {
        "tsx": tsx_path,
        "timing": timing_path,
        "srt": srt_path,
        "drift_threshold_seconds": drift_warn,
        "total_duration_seconds": round(timing['total_duration'], 2),
        "srt_entry_count": len(subs),
        "issues_count": issues,
        "summary": {
            "sections_total": len(timing['sections']),
            "sections_audited": len(audited),
            "sections_skipped_no_mapping": sum(1 for r in section_records if r['status'] == 'no_mapping'),
            "sections_unparseable": sum(1 for r in section_records if r['status'] == 'unparseable'),
            "beats_audited": sum(len(r['beats']) for r in audited),
            "beats_with_drift": issues,
        },
        "sections": section_records,
    }
    return issues, result


def build_parser():
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Beat data format and SECTION_CONFIG conventions: see the module docstring.",
    )
    parser.add_argument('tsx', help='Path to the Remotion video.tsx file containing beat arrays')
    parser.add_argument('timing', help='Path to timing.json (output of generate_tts.py)')
    parser.add_argument('srt', nargs='?', default=None,
                        help='Path to podcast_audio.srt (defaults to <timing.json dir>/podcast_audio.srt)')
    parser.add_argument('--drift-warn', type=float, default=1.5, metavar='SECONDS',
                        help='Drift threshold in seconds; beats more than this far from any '
                             'SRT entry start are flagged (default: 1.5)')
    cli_envelope.add_format_arg(parser)
    return parser


def main():
    args = build_parser().parse_args()
    started_at = time.time()
    json_mode = cli_envelope.use_json(args)
    if json_mode:
        sys.stdout = sys.stderr  # route audit table off stdout in JSON mode
    try:
        srt = args.srt or os.path.join(os.path.dirname(args.timing), 'podcast_audio.srt')
        missing = [p for p in (args.tsx, args.timing, srt) if not os.path.exists(p)]
        if missing:
            for p in missing:
                print(f"Not found: {p}", file=sys.stderr)
            sys.stdout = sys.__stdout__
            sys.exit(cli_envelope.emit_error(
                args, "input_not_found",
                f"{len(missing)} required file(s) not found",
                extra={"missing": missing,
                       "tsx": args.tsx, "timing": args.timing, "srt": srt},
                started_at=started_at,
            ))

        try:
            issues, result = audit(args.tsx, args.timing, srt, drift_warn=args.drift_warn)
        except ValueError as exc:
            # parse_beats found no SECTION_CONFIG entries with `beats:`
            sys.stdout = sys.__stdout__
            sys.exit(cli_envelope.emit_error(
                args, "input_invalid", str(exc),
                field="tsx",
                extra={"tsx": args.tsx},
                started_at=started_at,
            ))
        except json.JSONDecodeError as exc:
            sys.stdout = sys.__stdout__
            sys.exit(cli_envelope.emit_error(
                args, "input_invalid",
                f"timing.json is malformed: {exc}",
                field="timing", extra={"timing": args.timing},
                started_at=started_at,
            ))
    finally:
        sys.stdout = sys.__stdout__

    if issues:
        # Audit completed; the *gate* failed — beats drift exceeds threshold.
        sys.exit(cli_envelope.emit_error(
            args, "validation_failed",
            f"{issues} beat(s) more than {args.drift_warn}s from nearest SRT boundary",
            extra=result,
            started_at=started_at,
        ))
    sys.exit(cli_envelope.emit_success(args, result, started_at=started_at))


if __name__ == '__main__':
    main()
