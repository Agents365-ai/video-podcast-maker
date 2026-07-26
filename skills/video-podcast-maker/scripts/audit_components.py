#!/usr/bin/env python3
"""Audit component usage across produced *Video.tsx files.

Scans a Remotion project's src/remotion/ directory for per-video composition
files and reports which exported components are actually imported and used.

Usage:
    audit_components.py <remotion-project-root> [--threshold N]

Output:
    - Component usage counts across all videos
    - Zero-usage components (candidates for removal)
    - Top-used components

Exit 0: report printed. Exit 2: zero-usage components found (warn-only).
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

# Components exported from templates/components/index.ts
# Keep this list in sync with the actual exports.
COMPONENTS = {
    "Scale4K",
    "FullBleedLayout",
    "PaddedLayout",
    "useEntrance",
    "useExit",
    "useCounter",
    "useBarFill",
    "getPresentation",
    "useFloat",
    "usePulse",
    "useGradientShift",
    "useOpacityWave",
    "useTextReveal",
    "useCharReveal",
    "staggerDelay",
    "useDrawOn",
    "useStaggeredDrawOn",
    "MovingGradient",
    "FloatingShapes",
    "GridPattern",
    "GlowOrb",
    "AccentLine",
    "SplitLayout",
    "StatHighlight",
    "ZigzagCards",
    "CenteredShowcase",
    "MetricsRow",
    "StepProgress",
    "ComparisonCard",
    "Timeline",
    "CodeBlock",
    "QuoteBlock",
    "FeatureGrid",
    "DataBar",
    "StatCounter",
    "FlowChart",
    "IconCard",
    "ChapterProgressBar",
    "MediaSection",
    "MediaGrid",
    "DiagramReveal",
    "AudioWaveform",
    "LottieAnimation",
    "DataTable",
    "ErrorBoundary",
    "Icon",
    "getLucideIcon",
    "isEmoji",
    "ShortIntroCard",
    "ShortCTACard",
    "Subtitles",
    "useTiming",
    "fetchTimingData",
    "useAssets",
    "getAsset",
    "getSectionAssets",
    "assetSrc",
    "AssetImage",
    "AssetVideo",
    "OverlayLayer",
}


def _find_video_files(root: Path) -> list[Path]:
    """Return *Video.tsx files (exclude templates/components themselves)."""
    src = root / "src" / "remotion"
    if not src.is_dir():
        return []
    return [
        f
        for f in src.glob("*Video.tsx")
        if "templates" not in str(f) and "components" not in str(f)
    ]


def _count_usage(files: list[Path]) -> Counter:
    """Count component usage across all video files."""
    counts = Counter()
    patterns = {comp: re.compile(rf"\b{re.escape(comp)}\b") for comp in COMPONENTS}
    for filepath in files:
        text = filepath.read_text(encoding="utf-8")
        for comp, pattern in patterns.items():
            matches = pattern.findall(text)
            if matches:
                counts[comp] += len(matches)
    return counts


def main():
    parser = argparse.ArgumentParser(
        description="Audit component usage across produced video compositions"
    )
    parser.add_argument(
        "project_root",
        type=Path,
        help="Remotion project root (contains src/remotion/)",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=2,
        help="Minimum video count to suppress low-usage warning (default: 2)",
    )
    args = parser.parse_args()

    files = _find_video_files(args.project_root)
    if len(files) < args.threshold:
        print(
            f"Only {len(files)} video file(s) found (threshold {args.threshold}) — "
            "not enough data for a meaningful audit. Build a few more videos first."
        )
        sys.exit(0)

    usage = _count_usage(files)
    total_videos = len(files)

    print(f"Component usage across {total_videos} video(s):\n")
    print(f"{'Component':<24} {'Videos':>7} {'Occurrences':>12}")
    print("-" * 44)

    used = {c for c in COMPONENTS if usage[c] > 0}
    unused = COMPONENTS - used

    for comp in sorted(used, key=lambda c: (-usage[c], c)):
        # Count how many videos use this component
        pattern = re.compile(rf"\b{re.escape(comp)}\b")
        videos_with = sum(
            1 for f in files if pattern.search(f.read_text(encoding="utf-8"))
        )
        print(f"{comp:<24} {videos_with:>6}/{total_videos} {usage[comp]:>11}")

    if unused:
        print(f"\n--- Unused ({len(unused)}) ---")
        for comp in sorted(unused):
            print(f"  {comp}")
        print(f"\n{len(unused)} components have zero usage — candidates for pruning.")
        sys.exit(2)
    else:
        print("\nAll components in use.")


if __name__ == "__main__":
    main()
