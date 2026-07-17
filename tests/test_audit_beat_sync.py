"""Tests for scripts/audit_beat_sync.py — beat-vs-narration drift gate.

Covers the three pure parsers (parse_beats, parse_srt, srt_overlap) and the
end-to-end audit() contract: result-dict shape, drift counting, and the
ValueError raised when the .tsx has no SECTION_CONFIG with beats.
"""
import json
import textwrap
from pathlib import Path

import pytest

# scripts/ is on sys.path via tests/conftest.py
from audit_beat_sync import audit, parse_beats, parse_srt, srt_overlap  # noqa: E402


# --- Fixture builders --------------------------------------------------------

# NOTE: the _BEATS_CONST and _SECTION_CONFIG regexes anchor on "]" / "}" sitting
# alone at end-of-line (re.MULTILINE), so the closing bracket cannot be followed
# by ";" on the same line. Real Video.tsx files in templates/presets/ are
# formatted this way too.
CLEAN_TSX = textwrap.dedent("""\
    import React from 'react';

    const HERO_BEATS: Beat[] = [
      { startSec: 0.0, lines: ['Hello world this is a test'] },
      { startSec: 2.0, lines: ['Second beat content'] }
    ]

    const SECTION_CONFIG: Record<string, Section> = {
      hero: { beats: HERO_BEATS, label: 'Intro' }
    }
""")

# Same tsx but the second beat is far from any SRT entry (drift > threshold).
DRIFT_TSX = textwrap.dedent("""\
    const HERO_BEATS: Beat[] = [
      { startSec: 0.0, lines: ['First beat string'] },
      { startSec: 8.0, lines: ['Beat eight far from any srt'] }
    ]

    const SECTION_CONFIG: Record<string, Section> = {
      hero: { beats: HERO_BEATS, label: 'Intro' }
    }
""")

NO_CONFIG_TSX = textwrap.dedent("""\
    const HERO_BEATS: Beat[] = [
      { startSec: 0.0, lines: ['orphan'] }
    ]
""")

CLEAN_SRT = textwrap.dedent("""\
    1
    00:00:00,000 --> 00:00:01,500
    Hello world this is a test

    2
    00:00:02,000 --> 00:00:03,500
    Second beat content

    3
    00:00:04,000 --> 00:00:05,000
    Tail filler
""")


def _write(tmp_path: Path, tsx: str, srt: str = CLEAN_SRT, total_duration: float = 5.0):
    tsx_path = tmp_path / 'video.tsx'
    timing_path = tmp_path / 'timing.json'
    srt_path = tmp_path / 'podcast_audio.srt'
    tsx_path.write_text(tsx, encoding='utf-8')
    srt_path.write_text(srt, encoding='utf-8')
    timing_path.write_text(json.dumps({
        'total_duration': total_duration,
        'sections': [{'name': 'hero', 'start_time': 0.0, 'duration': total_duration}],
    }), encoding='utf-8')
    return tsx_path, timing_path, srt_path


# --- Pure parsers ------------------------------------------------------------

def test_parse_srt_extracts_each_block():
    subs = parse_srt(CLEAN_SRT)
    assert len(subs) == 3
    assert subs[0] == (0.0, 1.5, 'Hello world this is a test')
    assert subs[1][0] == pytest.approx(2.0)
    assert subs[2][2] == 'Tail filler'


def test_parse_beats_finds_array_and_section_mapping():
    name_to_beats, beats_arrays = parse_beats(CLEAN_TSX)
    assert name_to_beats == {'hero': 'HERO_BEATS'}
    assert 'HERO_BEATS' in beats_arrays
    starts = [start for start, _ in beats_arrays['HERO_BEATS']]
    assert starts == [0.0, 2.0]


def test_parse_beats_returns_empty_mapping_when_no_section_config():
    name_to_beats, beats_arrays = parse_beats(NO_CONFIG_TSX)
    # Beats array is found but the audit() caller will raise — see
    # test_audit_raises_on_missing_section_config.
    assert name_to_beats == {}
    assert 'HERO_BEATS' in beats_arrays


def test_srt_overlap_concatenates_entries_in_range():
    subs = parse_srt(CLEAN_SRT)
    text = srt_overlap(subs, 0.0, 4.0)
    assert 'Hello world' in text
    assert 'Second beat' in text
    assert 'Tail filler' not in text  # starts at 4.0, not strictly inside


def test_srt_overlap_empty_for_disjoint_window():
    subs = parse_srt(CLEAN_SRT)
    assert srt_overlap(subs, 100.0, 200.0) == ''


# --- End-to-end audit() ------------------------------------------------------

def test_audit_clean_run_no_drift(tmp_path):
    tsx, timing, srt = _write(tmp_path, CLEAN_TSX, CLEAN_SRT, total_duration=5.0)
    issues, result = audit(str(tsx), str(timing), str(srt), drift_warn=1.5)
    assert issues == 0
    assert result['issues_count'] == 0
    assert result['summary']['sections_audited'] == 1
    assert result['summary']['beats_with_drift'] == 0
    hero = result['sections'][0]
    assert hero['name'] == 'hero'
    assert hero['status'] == 'audited'
    assert all(b['ok'] for b in hero['beats'])


def test_audit_flags_drift_when_beat_far_from_srt(tmp_path):
    # SRT only goes to 5s; beat at 8.0 is 3+s away from any SRT entry start.
    tsx, timing, srt = _write(tmp_path, DRIFT_TSX, CLEAN_SRT, total_duration=10.0)
    issues, result = audit(str(tsx), str(timing), str(srt), drift_warn=1.5)
    assert issues >= 1
    assert result['issues_count'] == issues
    assert result['summary']['beats_with_drift'] == issues
    drift_beats = [b for b in result['sections'][0]['beats'] if not b['ok']]
    assert drift_beats
    assert all(b['nearest_srt_distance_seconds'] > 1.5 for b in drift_beats)


def test_audit_raises_on_missing_section_config(tmp_path):
    tsx, timing, srt = _write(tmp_path, NO_CONFIG_TSX, CLEAN_SRT)
    with pytest.raises(ValueError, match='SECTION_CONFIG'):
        audit(str(tsx), str(timing), str(srt))


def test_audit_records_drift_threshold_in_result(tmp_path):
    tsx, timing, srt = _write(tmp_path, CLEAN_TSX, CLEAN_SRT, total_duration=5.0)
    _, result = audit(str(tsx), str(timing), str(srt), drift_warn=2.5)
    assert result['drift_threshold_seconds'] == 2.5
    assert result['srt_entry_count'] == 3
    assert result['total_duration_seconds'] == 5.0
