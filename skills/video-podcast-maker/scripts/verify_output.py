#!/usr/bin/env python3
"""End-of-pipeline verification + auto-fix for a video project.

Checks that all expected files exist and meet specs, auto-fixes common
omissions (e.g. final_video.mp4 missing because Step 10.1 skipped subtitles
without aliasing), and prints a clean acceptance report.

Usage:
  python3 verify_output.py videos/<name>/
  python3 verify_output.py videos/<name>/ --strict     # fail on any warning
  python3 verify_output.py videos/<name>/ --no-fix     # report only, do not auto-fix
  python3 verify_output.py videos/<name>/ --format json  # machine-readable envelope

Exit codes:
  0 = all critical files present and valid
  1 = critical missing or invalid
  2 = warnings only (use --strict to treat as failure)
"""

from __future__ import annotations
import os
import sys
import json
import time
import argparse
import shutil
import subprocess
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cli_envelope  # noqa: E402


CORE_REQUIRED = [
    "podcast.txt",
    "podcast_audio.wav",
    "podcast_audio.srt",
    "timing.json",
    "publish_info.md",
]

# Per-platform artifact requirements: long-form platforms (bilibili/youtube)
# and xiaohongshu need the horizontal render chain (output.mp4 +
# final_video.mp4); shorts-only platforms (douyin, weixin-channels) have no
# long-form video and must ship the shorts/ outputs instead. Keep keys in
# sync with PLATFORM_SECTIONS.
PLATFORM_ARTIFACTS = {
    "bilibili": {
        "required": ("output.mp4", "final_video.mp4"),
        "thumbnails": ("16x9", "4x3"),
    },
    "youtube": {
        "required": ("output.mp4", "final_video.mp4"),
        "thumbnails": ("16x9", "4x3"),
    },
    "xiaohongshu": {
        "required": ("output.mp4", "final_video.mp4"),
        "thumbnails": ("3x4",),
    },
    "douyin": {
        "required": ("shorts",),
        "thumbnails": ("9x16",),
    },
    "weixin-channels": {
        "required": ("shorts",),
        "thumbnails": ("9x16",),
    },
}

# Per aspect ratio, accept either the Remotion-generated or AI-generated
# thumbnail name. 3x4/9x16 have no AI variant today (Remotion-only).
THUMBNAIL_ALTERNATIVES = {
    "16x9": ("thumbnail_remotion_16x9.png", "thumbnail_ai_16x9.png"),
    "4x3": ("thumbnail_remotion_4x3.png", "thumbnail_ai_4x3.png"),
    "3x4": ("thumbnail_remotion_3x4.png",),
    "9x16": ("thumbnail_remotion_9x16.png",),
}

OPTIONAL = [
    "video_with_bgm.mp4",
    "bgm.mp3",
    "topic_definition.md",
    "topic_research.md",
    "phonemes.json",
]

EXPECTED_RES = [(3840, 2160), (2160, 3840)]  # horizontal or vertical 4K
THUMB_16x9 = (1920, 1080)
THUMB_4x3 = (1200, 900)
THUMB_3x4 = (1080, 1440)
THUMB_9x16 = (1080, 1920)

# Per-platform required publish_info.md section headings. Keep keys in sync
# with prefs_schema.json::global.platform and the format tables in
# references/workflow-publish.md → "Publish Info Format by Platform".
PLATFORM_SECTIONS = {
    "bilibili": ("## 标题", "## 标签", "## 简介", "## 章节"),
    "youtube": ("## Title", "## Tags", "## Description", "## Chapters"),
    "xiaohongshu": ("## 标题", "## 正文", "## 话题标签"),
    "douyin": ("## 文案", "## 话题标签"),
    "weixin-channels": ("## 文案", "## 话题标签"),
}
DEFAULT_PLATFORM = "bilibili"


def _resolve_platform(seed=True):
    """Read `global.platform` from user_prefs.json (shared state dir).

    Falls back to bilibili if missing or malformed. With seed=False
    (--no-fix preview) the state file is read without creating it, so a
    read-only verify never mutates the filesystem.
    """
    from _state import get_state_dir, resolve_state_file

    if seed:
        prefs_path = resolve_state_file(
            "user_prefs.json", template_filename="user_prefs.template.json"
        )
    else:
        prefs_path = get_state_dir() / "user_prefs.json"
    try:
        with open(prefs_path, encoding="utf-8") as f:
            prefs = json.load(f)
    except (OSError, json.JSONDecodeError):
        return DEFAULT_PLATFORM
    platform = (prefs.get("global", {}) or {}).get("platform")
    if platform in PLATFORM_SECTIONS:
        return platform
    return DEFAULT_PLATFORM


def ffprobe_video(path):
    """Return (width, height, duration, audio_codec) or None on failure.

    For audio-only inputs (e.g. .wav), use ffprobe_audio() instead — this
    function returns None when no video stream is present.
    """
    try:
        out = subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_streams",
                "-show_format",
                str(path),
            ]
        ).decode()
        data = json.loads(out)
        v = next((s for s in data["streams"] if s["codec_type"] == "video"), None)
        a = next((s for s in data["streams"] if s["codec_type"] == "audio"), None)
        if not v:
            return None
        num, _, den = v.get("r_frame_rate", "0/1").partition("/")
        return {
            "width": int(v["width"]),
            "height": int(v["height"]),
            "duration": float(data["format"]["duration"]),
            "video_codec": v["codec_name"],
            "audio_codec": a["codec_name"] if a else None,
            "fps": (float(num) / float(den)) if float(den or 1) else None,
            "pix_fmt": v.get("pix_fmt"),
        }
    except (subprocess.CalledProcessError, KeyError, ValueError):
        return None


def ffprobe_audio(path):
    """Return {'duration': float, 'audio_codec': str|None} or None on failure.

    Use for WAV/MP3 files. Probes format duration directly so it works for
    container-only audio that has no video stream.
    """
    try:
        out = subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_streams",
                "-show_format",
                str(path),
            ]
        ).decode()
        data = json.loads(out)
        a = next((s for s in data["streams"] if s["codec_type"] == "audio"), None)
        return {
            "duration": float(data["format"]["duration"]),
            "audio_codec": a["codec_name"] if a else None,
        }
    except (subprocess.CalledProcessError, KeyError, ValueError):
        return None


def png_size(path):
    """Return (width, height) by parsing PNG header. No external deps."""
    try:
        with open(path, "rb") as f:
            header = f.read(24)
        if header[:8] != b"\x89PNG\r\n\x1a\n":
            return None
        return (
            int.from_bytes(header[16:20], "big"),
            int.from_bytes(header[20:24], "big"),
        )
    except OSError:
        return None


def auto_fix(video_dir):
    """Attempt to recover from known omissions. Returns list of fix descriptions.

    Non-destructive by design: only writes a new file (final_video.mp4) when
    it does not already exist, by copying an upstream artifact that was
    produced earlier in the pipeline. No existing file is overwritten, no
    user data is mutated. This is why no --yes gate is required despite the
    general CLI convention that destructive ops gate behind explicit consent
    (CLAUDE.md "Destructive ops"). To preview without writing, pass --no-fix.
    """
    fixes = []
    final_mp4 = video_dir / "final_video.mp4"
    bgm_mp4 = video_dir / "video_with_bgm.mp4"
    output_mp4 = video_dir / "output.mp4"

    # 1) final_video.mp4 missing but video_with_bgm.mp4 exists → alias (subtitles skipped path)
    if not final_mp4.exists() and bgm_mp4.exists():
        shutil.copy2(bgm_mp4, final_mp4)
        fixes.append(
            "Created final_video.mp4 from video_with_bgm.mp4 (subtitles skipped)"
        )

    # 2) final_video.mp4 missing AND no BGM mix → fall back to output.mp4 (no BGM path)
    elif not final_mp4.exists() and output_mp4.exists():
        shutil.copy2(output_mp4, final_mp4)
        fixes.append(
            "Created final_video.mp4 from output.mp4 (no BGM mix; consider running Step 9.5)"
        )

    return fixes


# Alpha-capable pixel formats accepted for overlay assets
# (WebM VP9 → yuva420p; ProRes 4444 → yuva444p10le; PNG-sequence overlays are
# directories of RGBA frames and are not probed here).
OVERLAY_ALPHA_PIX_FMTS = {"yuva420p", "yuva444p10le", "yuva422p10le", "argb", "rgba"}
OVERLAY_FPS = 30


def check_overlay_assets(video_dir, manifest):
    """Spec-check resolved overlay assets (Hyperframes renders).

    Returns (errors, warnings, details). An overlay without alpha would
    cover the whole composition, and an fps mismatch breaks audio-master
    sync — both are errors. Duration/resolution deviations are warnings.
    """
    errors, warnings, details = [], [], {}
    for a in (manifest or {}).get("assets", []):
        if (
            a.get("type") != "overlay"
            or a.get("status") != "resolved"
            or not a.get("path")
        ):
            continue
        label = a.get("id", a.get("path"))
        path = Path(video_dir) / a["path"]
        if path.is_dir():
            continue  # PNG-sequence overlays: presence checked by manifest validation
        info = ffprobe_video(path)
        if info is None:
            errors.append(f"overlay {label}: ffprobe failed on {a['path']}")
            continue
        details[label] = info
        if info["pix_fmt"] not in OVERLAY_ALPHA_PIX_FMTS:
            errors.append(
                f"overlay {label}: pix_fmt {info['pix_fmt']} has no alpha channel "
                f"(expected one of {sorted(OVERLAY_ALPHA_PIX_FMTS)})"
            )
        if info["fps"] is None or abs(info["fps"] - OVERLAY_FPS) > 0.01:
            errors.append(f"overlay {label}: fps {info['fps']} != {OVERLAY_FPS}")
        declared = a.get("duration_s")
        if declared is not None and abs(info["duration"] - declared) > 0.15:
            warnings.append(
                f"overlay {label}: duration {info['duration']:.2f}s vs manifest "
                f"{declared}s — realign to the section window"
            )
        if (info["width"], info["height"]) not in EXPECTED_RES:
            warnings.append(
                f"overlay {label}: {info['width']}x{info['height']} is not full-frame 4K"
            )
    return errors, warnings, details


def verify(video_dir, strict=False, do_auto_fix=True):
    """Run all checks. Returns (exit_code, result_dict).

    Prints a human-readable report on stdout. Caller wraps stdout with a
    stderr redirect when emitting a JSON envelope so the report becomes
    diagnostic chatter and only the envelope reaches the agent.

    The returned dict captures every structured fact an agent or
    orchestrator needs to decide "publish or fix":
      video_dir, strict, auto_fix_enabled,
      required_files: {present, missing},
      optional_files_present,
      fixes_applied,
      final_video: {...} | None,
      thumbnails: {filename: {present, size, expected, ok}},
      audio_timing: {wav_duration, timing_duration, drift_seconds, sections_count, ok} | None,
      publish_info: {promo_present, sections_present, sections_missing} | None,
      warnings, errors
    """
    print(f"\n{'=' * 70}")
    print(f"Verifying: {video_dir}")
    print("=" * 70)

    result = {
        "video_dir": str(video_dir),
        "strict": strict,
        "auto_fix_enabled": do_auto_fix,
        "required_files": {"present": [], "missing": []},
        "optional_files_present": [],
        "fixes_applied": [],
        "final_video": None,
        "thumbnails": {},
        "audio_timing": None,
        "publish_info": None,
        "warnings": [],
        "errors": [],
    }

    if not video_dir.is_dir():
        print(f"✗ Directory not found: {video_dir}")
        result["errors"].append(f"Directory not found: {video_dir}")
        return 1, result

    # Auto-fix first so subsequent checks see the patched state
    if do_auto_fix:
        fixes = auto_fix(video_dir)
        result["fixes_applied"] = fixes
        if fixes:
            print("\n--- Auto-fix applied ---")
            for f in fixes:
                print(f"  ⚙ {f}")
    else:
        print("\n--- Auto-fix skipped (--no-fix) ---")

    platform = _resolve_platform(seed=do_auto_fix)
    required = CORE_REQUIRED + list(PLATFORM_ARTIFACTS[platform]["required"])

    print("\n--- Required files ---")
    for fname in required:
        if fname == "shorts":
            # shorts-only platforms (douyin, weixin-channels): the deliverable
            # is the 9:16 shorts set, not a horizontal long-form render.
            shorts_dir = video_dir / "shorts"
            mp4s = sorted(shorts_dir.glob("*.mp4")) if shorts_dir.is_dir() else []
            if mp4s:
                print(f"  ✓ shorts/          {len(mp4s)} short(s)")
                result["required_files"]["present"].append("shorts")
            else:
                print("  ✗ shorts/          MISSING (no .mp4 shorts — run Step 11)")
                result["required_files"]["missing"].append("shorts")
            continue
        p = video_dir / fname
        if p.exists():
            size = p.stat().st_size
            size_str = (
                f"{size / 1024 / 1024:.1f} MB"
                if size > 1024 * 1024
                else f"{size / 1024:.1f} KB"
            )
            print(f"  ✓ {fname:<35} {size_str}")
            result["required_files"]["present"].append(fname)
        else:
            print(f"  ✗ {fname:<35} MISSING")
            result["required_files"]["missing"].append(fname)

    # Thumbnails: per aspect ratio, accept Remotion OR AI naming. Only the
    # platform's required ratios are checked.
    for aspect in PLATFORM_ARTIFACTS[platform]["thumbnails"]:
        names = THUMBNAIL_ALTERNATIVES[aspect]
        present = [n for n in names if (video_dir / n).exists()]
        if present:
            for n in present:
                size = (video_dir / n).stat().st_size
                size_str = (
                    f"{size / 1024 / 1024:.1f} MB"
                    if size > 1024 * 1024
                    else f"{size / 1024:.1f} KB"
                )
                print(f"  ✓ {n:<35} {size_str}")
                result["required_files"]["present"].append(n)
        else:
            missing_label = " OR ".join(names)
            print(f"  ✗ thumbnail {aspect:<23} MISSING ({missing_label})")
            result["required_files"]["missing"].append(missing_label)

    print("\n--- Optional files ---")
    for fname in OPTIONAL:
        p = video_dir / fname
        if p.exists():
            print(f"  ✓ {fname}")
            result["optional_files_present"].append(fname)

    warnings = []
    errors = list(result["required_files"]["missing"])

    # Final video specs
    print("\n--- Final video (final_video.mp4) ---")
    final_mp4 = video_dir / "final_video.mp4"
    if final_mp4.exists():
        info = ffprobe_video(final_mp4)
        if info:
            res_ok = (info["width"], info["height"]) in EXPECTED_RES
            res_marker = "✓" if res_ok else "✗"
            expected_str = " or ".join(f"{w}x{h}" for w, h in EXPECTED_RES)
            print(
                f"  {res_marker} Resolution: {info['width']}x{info['height']} (expected {expected_str})"
            )
            if not res_ok:
                errors.append(f"Resolution {info['width']}x{info['height']} != 4K")
            print(
                f"  ✓ Duration: {info['duration']:.1f}s ({info['duration'] / 60:.1f} min)"
            )
            # Render contract: h264 + aac at 30fps (workflow-production.md Step 9).
            codec_ok = info["video_codec"] == "h264"
            audio_ok = info["audio_codec"] == "aac"
            fps_ok = info["fps"] is not None and abs(info["fps"] - 30) < 0.5
            print(f"  {'✓' if codec_ok else '✗'} Video codec: {info['video_codec']} (expected h264)")
            print(
                f"  {'✓' if audio_ok else '✗'} Audio codec: {info['audio_codec'] or 'NONE'} (expected aac)"
            )
            print(f"  {'✓' if fps_ok else '✗'} FPS: {info['fps']} (expected ~30)")
            if not codec_ok:
                errors.append(f"final_video.mp4 video codec {info['video_codec']} != h264")
            if not audio_ok:
                errors.append(
                    f"final_video.mp4 audio codec {info['audio_codec'] or 'NONE'} != aac"
                )
            if not fps_ok:
                errors.append(f"final_video.mp4 fps {info['fps']} != 30")
            result["final_video"] = {
                "width": info["width"],
                "height": info["height"],
                "duration_seconds": round(info["duration"], 2),
                "video_codec": info["video_codec"],
                "audio_codec": info["audio_codec"],
                "fps": info["fps"],
                "resolution_ok": res_ok,
                "codec_ok": codec_ok,
                "audio_ok": audio_ok,
                "fps_ok": fps_ok,
            }
        else:
            errors.append("ffprobe failed on final_video.mp4")
            print("  ✗ ffprobe failed")

    # Thumbnail specs — check every alternative that's actually on disk.
    # Only the platform's required ratios are checked; a ratio is missing
    # only when NEITHER of its variants is present.
    print("\n--- Thumbnails ---")
    aspect_specs = {
        "16x9": THUMB_16x9,
        "4x3": THUMB_4x3,
        "3x4": THUMB_3x4,
        "9x16": THUMB_9x16,
    }
    for aspect in PLATFORM_ARTIFACTS[platform]["thumbnails"]:
        names = THUMBNAIL_ALTERNATIVES[aspect]
        expected = aspect_specs[aspect]
        any_present = False
        for fname in names:
            p = video_dir / fname
            thumb_record = {
                "present": False,
                "size": None,
                "expected": list(expected),
                "ok": False,
            }
            if p.exists():
                any_present = True
                thumb_record["present"] = True
                sz = png_size(p)
                if sz is not None and sz == expected:
                    print(f"  ✓ {fname}: {sz[0]}x{sz[1]}")
                    thumb_record["size"] = list(sz)
                    thumb_record["ok"] = True
                elif sz:
                    print(
                        f"  ⚠ {fname}: {sz[0]}x{sz[1]} (expected {expected[0]}x{expected[1]})"
                    )
                    warnings.append(f"{fname} size {sz[0]}x{sz[1]} != {expected}")
                    thumb_record["size"] = list(sz)
                else:
                    print(f"  ✗ {fname}: cannot read PNG header")
                    errors.append(f"{fname} unreadable")
            result["thumbnails"][fname] = thumb_record
        if not any_present:
            errors.append(f"thumbnail {aspect} missing (need one of {list(names)})")

    # Audio/timing alignment — WAV has no video stream so we use the
    # audio-only probe (ffprobe_video would return None and the drift
    # check below would never fire).
    print("\n--- Audio / timing alignment ---")
    wav = video_dir / "podcast_audio.wav"
    timing_path = video_dir / "timing.json"
    if wav.exists() and timing_path.exists():
        wav_info = ffprobe_audio(wav)
        try:
            with open(timing_path) as f:
                timing = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"  ✗ timing.json unreadable: {e}")
            errors.append(f"timing.json unreadable: {e}")
            timing = None
        if wav_info is None:
            print("  ✗ ffprobe failed on podcast_audio.wav")
            errors.append("ffprobe failed on podcast_audio.wav")
        elif timing is not None:
            wav_dur = wav_info["duration"]
            timing_dur = timing.get("total_duration", 0)
            drift = wav_dur - timing_dur
            drift_ok = abs(drift) < 0.5
            if drift_ok:
                print(
                    f"  ✓ WAV {wav_dur:.2f}s ≈ timing.json {timing_dur:.2f}s (drift {drift:+.2f}s)"
                )
            else:
                print(
                    f"  ✗ WAV {wav_dur:.2f}s vs timing.json {timing_dur:.2f}s (drift {drift:+.2f}s)"
                )
                errors.append(
                    f"Audio/timing drift {drift:+.2f}s — last sections may truncate"
                )
            sec_count = len(timing.get("sections", []))
            print(f"  ✓ {sec_count} sections registered in timing.json")
            result["audio_timing"] = {
                "wav_duration": round(wav_dur, 2),
                "timing_duration": round(timing_dur, 2),
                "drift_seconds": round(drift, 2),
                "sections_count": sec_count,
                "ok": drift_ok,
            }

    # Final video vs audio — the rendered/mixed output must match the master clock.
    print("\n--- Final video / audio sync ---")
    if final_mp4.exists() and wav.exists():
        info = ffprobe_video(final_mp4)
        wav_info_final = ffprobe_audio(wav)
        if info is None:
            print("  ✗ ffprobe failed on final_video.mp4")
        elif wav_info_final is None:
            print("  ✗ ffprobe failed on podcast_audio.wav")
        else:
            final_dur = info["duration"]
            wav_dur = wav_info_final["duration"]
            sync_drift = final_dur - wav_dur
            sync_ok = abs(sync_drift) < 0.5
            if sync_ok:
                print(
                    f"  ✓ final_video {final_dur:.2f}s ≈ WAV {wav_dur:.2f}s (drift {sync_drift:+.2f}s)"
                )
            else:
                print(
                    f"  ✗ final_video {final_dur:.2f}s vs WAV {wav_dur:.2f}s (drift {sync_drift:+.2f}s)"
                )
                errors.append(f"Final video/audio sync drift {sync_drift:+.2f}s")
            result["final_video_sync"] = {
                "final_duration": round(final_dur, 2),
                "wav_duration": round(wav_dur, 2),
                "drift_seconds": round(sync_drift, 2),
                "ok": sync_ok,
            }

    # Publish info sanity — required sections depend on which platform the
    # user is targeting. Falls back to bilibili if user_prefs.json is missing
    # or the platform key is unrecognized.
    print(f"\n--- publish_info.md (platform: {platform}) ---")
    pub = video_dir / "publish_info.md"
    if pub.exists():
        text = pub.read_text(encoding="utf-8")
        promo = "github.com/Agents365-ai/video-podcast-maker"
        promo_present = promo in text
        if promo_present:
            print("  ✓ Promo line present")
        else:
            print(
                f"  ⚠ Promo line missing — first description line should reference {promo}"
            )
            warnings.append("publish_info.md missing required promo line")
        sections_required = PLATFORM_SECTIONS[platform]
        sections_present = []
        sections_missing = []
        for required_section in sections_required:
            if required_section in text:
                print(f"  ✓ {required_section}")
                sections_present.append(required_section)
            else:
                print(f"  ⚠ {required_section} section missing")
                warnings.append(f"publish_info.md missing {required_section}")
                sections_missing.append(required_section)
        result["publish_info"] = {
            "platform": platform,
            "promo_present": promo_present,
            "sections_present": sections_present,
            "sections_missing": sections_missing,
        }

    # Asset manifest (Step 5) — only checked when a manifest exists;
    # text-only videos have none and that is valid.
    from assets import validate_manifest

    m_errors, m_warnings, m_manifest = validate_manifest(video_dir)
    if m_manifest is not None or m_errors:
        print("\n--- Asset manifest (assets/manifest.json) ---")
        for e in m_errors:
            print(f"  ✗ {e}")
            errors.append(f"asset manifest: {e}")
        for w in m_warnings:
            print(f"  ⚠ {w}")
            warnings.append(f"asset manifest: {w}")
        if not m_errors and m_manifest is not None:
            count = len(m_manifest.get("assets", []))
            print(f"  ✓ {count} assets registered, no errors")
        o_errors, o_warnings, o_details = check_overlay_assets(video_dir, m_manifest)
        for e in o_errors:
            print(f"  ✗ {e}")
            errors.append(f"asset manifest: {e}")
        for w in o_warnings:
            print(f"  ⚠ {w}")
            warnings.append(f"asset manifest: {w}")
        result["asset_manifest"] = {
            "present": m_manifest is not None,
            "asset_count": len(m_manifest.get("assets", [])) if m_manifest else 0,
            "errors": m_errors + o_errors,
            "warnings": m_warnings + o_warnings,
            "overlays": o_details,
        }

    result["warnings"] = warnings
    result["errors"] = errors

    # Summary
    print(f"\n{'=' * 70}")
    if errors:
        print(f"❌ FAILED  {len(errors)} critical issue(s):")
        for e in errors:
            print(f"   - {e}")
        return 1, result
    elif warnings and strict:
        print(f"⚠️  WARNINGS (--strict):  {len(warnings)} issue(s):")
        for w in warnings:
            print(f"   - {w}")
        return 1, result
    elif warnings:
        print(f"✓ ACCEPTED with {len(warnings)} warning(s):")
        for w in warnings:
            print(f"   - {w}")
        print("\nReady to publish.")
        return 2, result
    else:
        print("✅ ACCEPTED  All required files present and meet specs.")
        print("\nReady to publish.")
        return 0, result


def build_parser():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("video_dir", help="Path to videos/<name>/")
    parser.add_argument("--strict", action="store_true", help="Fail on any warning")
    parser.add_argument(
        "--no-fix",
        dest="auto_fix",
        action="store_false",
        help="Skip the auto-fix step (preview only). Without this flag, "
        "verify will create final_video.mp4 from video_with_bgm.mp4 "
        "or output.mp4 if missing.",
    )
    cli_envelope.add_format_arg(parser)
    return parser


def main():
    args = build_parser().parse_args()

    started_at = time.time()
    json_mode = cli_envelope.use_json(args)
    if json_mode:
        # Route the prose report off stdout so the JSON envelope is the only
        # payload an agent parses. cli_envelope captured the real stdout at
        # import time, so emit_* still reaches it.
        sys.stdout = sys.stderr
    try:
        try:
            exit_code, result = verify(
                Path(args.video_dir),
                strict=args.strict,
                do_auto_fix=args.auto_fix,
            )
        except Exception as exc:
            # Catch-all: convert unexpected exceptions to a structured envelope
            # in JSON mode so an agent never sees an empty stdout + traceback.
            # In prose mode re-raise so the user gets the full traceback.
            if not json_mode:
                raise
            sys.stdout = sys.__stdout__
            sys.exit(
                cli_envelope.emit_error(
                    args,
                    "internal_error",
                    f"{type(exc).__name__}: {exc}",
                    extra={"video_dir": str(args.video_dir)},
                    started_at=started_at,
                )
            )
    finally:
        sys.stdout = sys.__stdout__

    if not cli_envelope.use_json(args):
        sys.exit(exit_code)

    if exit_code in (0, 2):
        # 0 = clean; 2 = warnings only, still publishable. Both emit success.
        # exit_code is preserved out-of-band so existing shell consumers
        # documented in workflow-publish.md keep working.
        sys.exit(
            cli_envelope.emit_success(
                args,
                result,
                started_at=started_at,
                exit_code=exit_code,
            )
        )

    # exit_code == 1: critical missing/invalid, OR warnings under --strict
    if result["errors"]:
        message = f"{len(result['errors'])} critical issue(s) in {result['video_dir']}"
    else:
        message = f"{len(result['warnings'])} warning(s) treated as errors (--strict)"
    sys.exit(
        cli_envelope.emit_error(
            args,
            "validation_failed",
            message,
            extra={
                "video_dir": result["video_dir"],
                "missing_required": result["required_files"]["missing"],
                "errors": result["errors"],
                "warnings": result["warnings"],
                "fixes_applied": result["fixes_applied"],
                "strict": result["strict"],
                "final_video": result["final_video"],
                "thumbnails": result["thumbnails"],
                "audio_timing": result["audio_timing"],
                "publish_info": result["publish_info"],
            },
            started_at=started_at,
        )
    )


if __name__ == "__main__":
    main()
