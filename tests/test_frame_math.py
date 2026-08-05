"""Contract test for the Remotion frame math in templates/Video.tsx.

Video.tsx scales sections in TypeScript; this test mirrors the algorithm in
Python and asserts the invariants the template must satisfy:

- rendered total == timing.total_frames + trailing_silent_count * SILENT_FRAMES
- every non-silent section's render start equals its audio start_frame
- the silent budget never enters the narration scaling numerator

Drift history: 5.2.0 paid the silent-outro floor out of the narrated
sections' budget (visuals desynced from audio); round 2 of 5.2.1 put the
silent budget in the scaling numerator (sections stretched, last chapter
crushed, outro appeared ~4.5s early). Both broke these invariants.
"""


SILENT_FRAMES = 150
MIN_FRAMES = 15


def _compensated(sections, total_frames, transition_frames):
    """Mirror of Video.tsx's scaling block (keep in sync with the template)."""
    last_non_silent = max(
        (i for i, s in enumerate(sections) if not s.get("is_silent")), default=-1
    )
    render = [
        s
        for i, s in enumerate(sections)
        if not (s.get("is_silent") and i <= last_non_silent)
    ]
    transition_count = max(0, len(render) - 1)
    effective = transition_frames if transition_frames > 0 else 0
    trailing = sum(1 for s in render if s.get("is_silent"))
    silent_budget = trailing * SILENT_FRAMES
    original = sum(s["duration_frames"] for s in render if not s.get("is_silent"))
    target = total_frames + transition_count * effective + silent_budget
    factor = (target - silent_budget) / original if original > 0 else 1
    out = []
    for s in render:
        if s.get("is_silent"):
            out.append({**s, "duration_frames": SILENT_FRAMES})
        else:
            out.append(
                {
                    **s,
                    "duration_frames": max(
                        MIN_FRAMES, round(s["duration_frames"] * factor)
                    ),
                }
            )
    # Rounding absorption into the last non-silent section.
    diff = target - sum(o["duration_frames"] for o in out)
    if diff:
        for o in reversed(out):
            if not o.get("is_silent"):
                o["duration_frames"] = max(MIN_FRAMES, o["duration_frames"] + diff)
                break
    return out, transition_count, effective


def _assert_invariants(sections, total_frames, transition_frames):
    """Run the mirror and assert the render contract holds.

    Per-section start alignment is tolerant of rounding (each section
    scales by the same factor and rounds independently, so cumulative
    error is bounded by ~0.5 frame per section plus one transition's
    worth of fade). The H1 regression drifted 32 frames PER SECTION,
    growing to 121 frames (4s) by the last section — far beyond the
    bound. The rendered TOTAL must match exactly.
    """
    out, transition_count, effective = _compensated(
        sections, total_frames, transition_frames
    )
    rendered_total = (
        sum(o["duration_frames"] for o in out) - transition_count * effective
    )
    trailing = sum(1 for o in out if o.get("is_silent"))
    assert rendered_total == total_frames + trailing * SILENT_FRAMES, (
        f"rendered {rendered_total} != total_frames {total_frames} + trailing*{SILENT_FRAMES}"
    )
    bound = 2 * effective + len(out)
    cursor = 0  # render start of the next section (each transition eats t)
    for i, o in enumerate(out):
        if not o.get("is_silent"):
            drift = cursor - o["start_frame"]
            assert abs(drift) <= bound, (
                f"section {o['name']}: render start {cursor} drifts {drift} frames "
                f"from audio start {o['start_frame']} (bound {bound})"
            )
        cursor += o["duration_frames"] - (effective if i < len(out) - 1 else 0)
    return out


def _sec(name, frames, start_frame, silent=False):
    return {
        "name": name,
        "duration_frames": frames,
        "start_frame": start_frame,
        "is_silent": silent,
    }


def test_plain_video_sections_stay_aligned():
    sections = [
        _sec("hero", 300, 0),
        _sec("content", 600, 300),
        _sec("body", 600, 900),
        _sec("summary", 300, 1500),
    ]
    _assert_invariants(sections, total_frames=1800, transition_frames=15)


def test_trailing_silent_outro_appends_after_audio():
    sections = [
        _sec("hero", 300, 0),
        _sec("content", 600, 300),
        _sec("body", 600, 900),
        _sec("summary", 300, 1500),
        _sec("outro", 0, 1800, silent=True),
    ]
    out = _assert_invariants(sections, total_frames=1800, transition_frames=15)
    # The outro renders after the narration, not inside it.
    assert out[-1]["duration_frames"] == SILENT_FRAMES
    assert out[-1]["is_silent"] is True


def test_middle_silent_is_dropped_not_rendered():
    # hero -> silent pause -> body + trailing outro: the middle silent is a
    # zero-width pause with nothing to render and must not consume timeline.
    sections = [
        _sec("hero", 300, 0),
        _sec("pause", 0, 300, silent=True),
        _sec("body", 600, 300),
        _sec("outro", 0, 900, silent=True),
    ]
    out = _assert_invariants(sections, total_frames=900, transition_frames=15)
    names = [o["name"] for o in out]
    assert "pause" not in names
    assert names == ["hero", "body", "outro"]


def test_long_video_has_no_cumulative_drift():
    # The round-2 regression: 9 sections with a trailing outro drifted up to
    # 4.5s because the silent budget was in the scaling numerator.
    sections = [_sec(f"s{i}", 600, i * 600) for i in range(9)]
    sections.append(_sec("outro", 0, 5400, silent=True))
    _assert_invariants(sections, total_frames=5400, transition_frames=15)


def test_silent_budget_not_in_scaling_numerator():
    # With a trailing outro, narrated sections must scale to total_frames +
    # transitions ONLY — never to the silent budget on top.
    sections = [
        _sec("hero", 600, 0),
        _sec("body", 600, 600),
        _sec("outro", 0, 1200, silent=True),
    ]
    out, _, _ = _compensated(sections, total_frames=1200, transition_frames=15)
    # Without the bug, 600-frame sections scale by (1200+15)/1200 = 1.0125
    # -> 608 frames; with the bug they'd be stretched toward the 150-budget.
    assert all(
        o["duration_frames"] < 620 for o in out if not o.get("is_silent")
    )
