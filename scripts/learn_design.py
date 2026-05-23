#!/usr/bin/env python3
"""
Design Reference Learner for Video Podcast Maker
Extracts frames from videos or copies images for coding-agent image analysis.
Manages a design_references/ library and user preference profiles.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cli_envelope  # noqa: E402


# ============ Constants ============

SUPPORTED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
SUPPORTED_VIDEO_EXTS = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv"}
MAX_FRAMES = 8
MAX_VIDEO_SIZE_BYTES = 2 * 1024 * 1024 * 1024  # 2 GB

PREFS_VERSION = "1.6"


# ============ Input Detection ============

def detect_input_type(path):
    """Classify a path or URL as 'url', 'local_video', 'image', 'unsupported', or 'not_found'.

    Returns one of: 'url', 'local_video', 'image', 'unsupported', 'not_found'
    """
    if path and (path.startswith("http://") or path.startswith("https://")):
        return "url"

    if not os.path.exists(path):
        return "not_found"

    ext = os.path.splitext(path)[1].lower()
    if ext in SUPPORTED_VIDEO_EXTS:
        return "local_video"
    if ext in SUPPORTED_IMAGE_EXTS:
        return "image"
    return "unsupported"


def detect_orientation(width, height):
    """Return 'horizontal', 'vertical', or 'square' based on dimensions."""
    if width > height:
        return "horizontal"
    if height > width:
        return "vertical"
    return "square"


# ============ Reference ID Generation ============

def _id_from_url(url):
    """Extract a short, stable ID from a video URL.

    Supports bilibili (BV ID), youtube watch URLs, youtu.be short links.
    Falls back to an 8-char md5 hash for unrecognized URLs.
    """
    # bilibili BV ID
    m = re.search(r"bilibili\.com/video/(BV[\w]+)", url)
    if m:
        return f"bilibili-{m.group(1)}"

    # youtube watch?v=
    m = re.search(r"(?:youtube\.com/watch\?v=)([\w-]+)", url)
    if m:
        return f"youtube-{m.group(1)}"

    # youtu.be short link
    m = re.search(r"youtu\.be/([\w-]+)", url)
    if m:
        return f"youtube-{m.group(1)}"

    # deterministic fallback via md5 (NOT hash() — randomized per process)
    h = hashlib.md5(url.encode()).hexdigest()[:8]
    return f"ref-{h}"


def generate_reference_id(source, name=None, existing_ids=None):
    """Generate a unique reference ID for a given source.

    Args:
        source: URL string, local file path, or None (for image sets).
        name: Optional human name for image sets.
        existing_ids: Set of IDs already in use (for collision avoidance).

    Returns:
        A unique kebab-case reference ID string.
    """
    existing_ids = existing_ids or set()

    if source and (source.startswith("http://") or source.startswith("https://")):
        base = _id_from_url(source)
    elif source and os.path.splitext(source)[1].lower() in (SUPPORTED_VIDEO_EXTS | SUPPORTED_IMAGE_EXTS):
        # Treat any path with a known extension as a local file reference,
        # whether or not the file exists yet (allows ID generation before copy).
        stem = os.path.splitext(os.path.basename(source))[0]
        base = f"local-{stem}"
    else:
        # Image set or unknown
        if name:
            base = f"images-{name}"
        else:
            ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
            base = f"images-{ts}"

    # Collision avoidance: append -2, -3, ...
    candidate = base
    suffix = 2
    while candidate in existing_ids:
        candidate = f"{base}-{suffix}"
        suffix += 1

    return candidate


# ============ Directory Management ============

def create_reference_dir(base_dir, ref_id):
    """Create {base_dir}/{ref_id}/frames/ and return the ref directory path."""
    ref_dir = os.path.join(base_dir, ref_id)
    frames_dir = os.path.join(ref_dir, "frames")
    os.makedirs(frames_dir, exist_ok=True)
    return ref_dir


# ============ Image Handling ============

def copy_images(image_paths, ref_dir):
    """Copy up to MAX_FRAMES images into ref_dir/frames/.

    The first image is also copied as cover.<ext> in ref_dir.
    Returns list of copied frame paths.
    """
    frames_dir = os.path.join(ref_dir, "frames")
    os.makedirs(frames_dir, exist_ok=True)

    selected = image_paths[:MAX_FRAMES]
    copied = []

    for i, src in enumerate(selected):
        ext = os.path.splitext(src)[1].lower()
        dest = os.path.join(frames_dir, f"frame_{i:04d}{ext}")
        shutil.copy2(src, dest)
        copied.append(dest)

        if i == 0:
            cover_dest = os.path.join(ref_dir, f"cover{ext}")
            shutil.copy2(src, cover_dest)

    return copied


# ============ Video Utilities ============

def get_video_duration(video_path):
    """Return duration in seconds via ffprobe. Returns None on failure."""
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                video_path,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return float(result.stdout.strip())
    except (subprocess.CalledProcessError, ValueError, FileNotFoundError):
        return None


def get_video_dimensions(video_path):
    """Return (width, height) via ffprobe. Returns (None, None) on failure."""
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height",
                "-of", "json",
                video_path,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        data = json.loads(result.stdout)
        stream = data["streams"][0]
        return int(stream["width"]), int(stream["height"])
    except (subprocess.CalledProcessError, KeyError, IndexError, json.JSONDecodeError, FileNotFoundError):
        return None, None


def extract_video_frames(video_path, ref_dir):
    """Extract up to MAX_FRAMES representative frames from a video using ffmpeg.

    Builds the ffmpeg command inline (fps=1/interval, scale=-1:1080).
    Returns list of extracted frame paths.
    """
    # Guard: file must exist
    if not os.path.exists(video_path):
        print(f"Error: video not found: {video_path}", file=sys.stderr)
        return []

    # Guard: file size
    size = os.path.getsize(video_path)
    if size > MAX_VIDEO_SIZE_BYTES:
        print(f"Warning: video exceeds 2 GB limit ({size} bytes), skipping frame extraction", file=sys.stderr)
        return []

    duration = get_video_duration(video_path)
    if duration is None or duration <= 0:
        print(f"Error: could not determine duration for {video_path}", file=sys.stderr)
        return []

    frames_dir = os.path.join(ref_dir, "frames")
    os.makedirs(frames_dir, exist_ok=True)

    # Sample frames evenly (1 frame every interval seconds)
    interval = max(1, duration / MAX_FRAMES)
    output_pattern = os.path.join(frames_dir, "frame_%04d.jpg")

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", f"fps=1/{interval:.2f},scale=-1:1080",
        "-frames:v", str(MAX_FRAMES),
        "-q:v", "2",
        output_pattern,
    ]

    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
    except FileNotFoundError:
        print("Error: ffmpeg not found. Install ffmpeg to enable video frame extraction.", file=sys.stderr)
        return []
    except subprocess.CalledProcessError as e:
        print(f"Error: ffmpeg failed: {e.stderr}", file=sys.stderr)
        return []

    # Collect extracted frames
    frames = sorted(
        os.path.join(frames_dir, f)
        for f in os.listdir(frames_dir)
        if f.startswith("frame_") and f.endswith(".jpg")
    )

    # Set cover from first frame
    if frames:
        shutil.copy2(frames[0], os.path.join(ref_dir, "cover.jpg"))

    return frames


# ============ Report I/O ============

def save_report(report, ref_dir):
    """Write report.json to ref_dir."""
    report_path = os.path.join(ref_dir, "report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)


def load_report(ref_dir):
    """Load and return report.json from ref_dir."""
    report_path = os.path.join(ref_dir, "report.json")
    with open(report_path, encoding="utf-8") as f:
        return json.load(f)


# ============ Preferences I/O ============

def _load_template():
    """Load user_prefs.template.json as default structure."""
    template_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "user_prefs.template.json")
    if os.path.exists(template_path):
        with open(template_path, encoding="utf-8") as f:
            return json.load(f)
    return {
        "version": PREFS_VERSION,
        "updated_at": None,
        "global": {},
        "topic_patterns": {},
        "style_profiles": {},
        "design_references": {},
        "learning_history": [],
    }


def _deep_merge(base, override):
    """Merge override into base recursively. Override values take priority."""
    result = base.copy()
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = v
    return result


def _migrate_prefs(prefs):
    """Migrate prefs to current version by merging missing fields from template."""
    if prefs.get("version", "1.0") != PREFS_VERSION:
        template = _load_template()
        # Deep merge: user values override template defaults, template fills gaps
        migrated = _deep_merge(template, prefs)
        migrated["version"] = PREFS_VERSION
        return migrated
    return prefs


def load_prefs(prefs_path):
    """Load user_prefs.json, migrating to current version if needed."""
    if not os.path.exists(prefs_path):
        return _load_template()

    with open(prefs_path, encoding="utf-8") as f:
        prefs = json.load(f)

    return _migrate_prefs(prefs)


def save_prefs(prefs, prefs_path):
    """Save prefs to disk, stamping updated_at with UTC ISO timestamp."""
    prefs["updated_at"] = datetime.now(timezone.utc).isoformat()
    with open(prefs_path, "w", encoding="utf-8") as f:
        json.dump(prefs, f, ensure_ascii=False, indent=2)


# ============ Reference Index Management ============

def add_reference_index(prefs, ref_id, title, source_url, tags):
    """Add or update an entry in prefs["design_references"]."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    prefs.setdefault("design_references", {})[ref_id] = {
        "path": f"design_references/{ref_id}",
        "title": title or ref_id,
        "source_url": source_url,
        "analyzed_at": today,
        "tags": tags or [],
    }


def add_style_profile(prefs, name, description, props_override, preferred_layouts=None,
                      preferred_backgrounds=None, animation_feel=None, density=None,
                      references=None):
    """Create a new style profile or update an existing one.

    When updating: layouts are unioned, props are merged (new wins), other scalar
    fields are overwritten.
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    profiles = prefs.setdefault("style_profiles", {})

    if name in profiles:
        existing = profiles[name]
        # Union preferred_layouts
        old_layouts = existing.get("preferred_layouts") or []
        new_layouts = preferred_layouts or []
        merged_layouts = list(dict.fromkeys(old_layouts + new_layouts))  # preserve order, dedupe
        # Merge props_override (new values win)
        merged_props = {**(existing.get("props_override") or {}), **(props_override or {})}
        existing["description"] = description
        existing["props_override"] = merged_props
        existing["preferred_layouts"] = merged_layouts
        if preferred_backgrounds is not None:
            existing["preferred_backgrounds"] = preferred_backgrounds
        if animation_feel is not None:
            existing["animation_feel"] = animation_feel
        if density is not None:
            existing["density"] = density
        if references is not None:
            existing["references"] = references
        existing["updated_at"] = today
    else:
        profiles[name] = {
            "description": description,
            "props_override": props_override or {},
            "preferred_layouts": preferred_layouts or [],
            "preferred_backgrounds": preferred_backgrounds or [],
            "animation_feel": animation_feel or "gentle",
            "density": density or "balanced",
            "references": references or [],
            "created_at": today,
            "updated_at": today,
        }


def remove_reference(prefs, ref_id, design_refs_base):
    """Remove a reference from the index and clean it from all style profiles.

    Also deletes the reference directory if it exists.
    """
    # Remove from index
    prefs.get("design_references", {}).pop(ref_id, None)

    # Clean from all style profiles
    for profile in prefs.get("style_profiles", {}).values():
        refs = profile.get("references", [])
        if ref_id in refs:
            refs.remove(ref_id)

    # Delete directory
    ref_dir = os.path.join(design_refs_base, ref_id)
    if os.path.isdir(ref_dir):
        shutil.rmtree(ref_dir)


def cleanup_orphaned_references(prefs, design_refs_base):
    """Remove entries from design_references whose directories no longer exist."""
    design_refs = prefs.get("design_references", {})
    orphans = [
        ref_id for ref_id in list(design_refs.keys())
        if not os.path.isdir(os.path.join(design_refs_base, ref_id))
    ]
    for ref_id in orphans:
        design_refs.pop(ref_id, None)


# ============ CLI Display Helpers ============

def _list_references(prefs, design_refs_base):
    """Print all design references with size and summary."""
    refs = prefs.get("design_references", {})
    if not refs:
        print("No design references found.")
        return

    print(f"{'ID':<35} {'Title':<30} {'Analyzed':<12} {'Frames'}")
    print("-" * 95)
    for ref_id, meta in sorted(refs.items()):
        ref_dir = os.path.join(design_refs_base, ref_id)
        frames_dir = os.path.join(ref_dir, "frames")
        frame_count = len(os.listdir(frames_dir)) if os.path.isdir(frames_dir) else 0
        title = (meta.get("title") or "")[:28]
        analyzed = meta.get("analyzed_at", "?")
        print(f"{ref_id:<35} {title:<30} {analyzed:<12} {frame_count}")


def _show_reference(ref_id, design_refs_base):
    """Print report.json for a given reference ID."""
    ref_dir = os.path.join(design_refs_base, ref_id)
    try:
        report = load_report(ref_dir)
        print(json.dumps(report, ensure_ascii=False, indent=2))
    except FileNotFoundError:
        print(f"Error: no report found for '{ref_id}'", file=sys.stderr)
        sys.exit(1)


# ============ CLI Entry Point ============

def _build_parser():
    parser = argparse.ArgumentParser(
        description="Extract design reference frames for coding-agent image analysis."
    )
    parser.add_argument(
        "inputs",
        nargs="*",
        help="URL(s), video file(s), or image file(s) to process",
    )
    parser.add_argument(
        "--name",
        help="Reference name for image sets (used in ID generation)",
    )
    parser.add_argument(
        "--output-dir",
        default="design_references",
        help="Directory to store reference data (default: design_references)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all design references with size and summary",
    )
    parser.add_argument(
        "--show",
        metavar="REF_ID",
        help="Show report.json for a specific reference ID",
    )
    parser.add_argument(
        "--delete",
        metavar="REF_ID",
        help="Delete a design reference (requires --yes; otherwise prints preview).",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirm destructive operations (currently: --delete). Without --yes, "
             "destructive flags print a preview of what would change and exit 3.",
    )
    parser.add_argument(
        "--profile",
        help="Design profile name for categorization (e.g., 'tech-minimal')",
    )
    parser.add_argument(
        "--tags",
        help="Comma-separated tags for filtering (e.g., 'tech,minimal,dark')",
    )
    cli_envelope.add_format_arg(parser)
    return parser


# ============ Structured-data helpers (envelope) ============

def _compute_references_index(prefs, design_refs_base):
    """Return a list of structured records for every design reference.

    Drives both --list prose printing and the --format json envelope.
    """
    refs = prefs.get("design_references", {})
    records = []
    for ref_id, meta in sorted(refs.items()):
        ref_dir = os.path.join(design_refs_base, ref_id)
        frames_dir = os.path.join(ref_dir, "frames")
        frame_count = len(os.listdir(frames_dir)) if os.path.isdir(frames_dir) else 0
        records.append({
            "ref_id": ref_id,
            "title": meta.get("title", ""),
            "analyzed_at": meta.get("analyzed_at"),
            "frame_count": frame_count,
            "tags": meta.get("tags", []),
            "path": meta.get("path", f"design_references/{ref_id}"),
            "source_url": meta.get("source_url"),
            "on_disk": os.path.isdir(ref_dir),
        })
    return records


def _compute_delete_preview(prefs, ref_id, ref_dir):
    """Compute what --delete REF_ID would change.

    Returns a dict suitable for both prose preview and the
    confirmation_required envelope's 'would_delete' slot.
    """
    meta = prefs.get("design_references", {}).get(ref_id, {})
    frames_dir = os.path.join(ref_dir, "frames")
    frame_count = len(os.listdir(frames_dir)) if os.path.isdir(frames_dir) else 0
    used_by = [name for name, profile in prefs.get("style_profiles", {}).items()
               if ref_id in profile.get("references", [])]
    return {
        "ref_id": ref_id,
        "path": ref_dir,
        "on_disk": os.path.isdir(ref_dir),
        "title": meta.get("title", ""),
        "frame_count": frame_count,
        "used_by_profiles": used_by,
    }


def main():
    parser = _build_parser()
    args = parser.parse_args()
    started_at = time.time()
    json_mode = cli_envelope.use_json(args)
    if json_mode:
        # Route prose chatter off stdout so the envelope is the only payload.
        sys.stdout = sys.stderr
    try:
        return _run(parser, args, started_at)
    finally:
        sys.stdout = sys.__stdout__


def _run(parser, args, started_at):
    # Locate prefs file at skill root (one level above scripts/)
    prefs_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "user_prefs.json")
    prefs = load_prefs(prefs_path)
    output_dir = args.output_dir

    # -- List mode --
    if args.list:
        _list_references(prefs, output_dir)
        records = _compute_references_index(prefs, output_dir)
        sys.exit(cli_envelope.emit_success(args, {
            "mode": "list",
            "output_dir": output_dir,
            "references": records,
            "count": len(records),
        }, started_at=started_at))

    # -- Show mode --
    if args.show:
        ref_id = args.show
        ref_dir = os.path.join(output_dir, ref_id)
        try:
            report = load_report(ref_dir)
        except FileNotFoundError:
            sys.exit(cli_envelope.emit_error(
                args, "input_not_found",
                f"no report found for '{ref_id}'",
                field="show",
                extra={"ref_id": ref_id,
                       "expected_path": os.path.join(ref_dir, "report.json")},
                started_at=started_at,
            ))
        print(json.dumps(report, ensure_ascii=False, indent=2))
        sys.exit(cli_envelope.emit_success(args, {
            "mode": "show",
            "ref_id": ref_id,
            "report": report,
        }, started_at=started_at))

    # -- Delete mode (gated by --yes) --
    if args.delete:
        ref_id = args.delete
        ref_dir = os.path.join(output_dir, ref_id)
        in_prefs = ref_id in prefs.get("design_references", {})
        on_disk = os.path.isdir(ref_dir)
        if not in_prefs and not on_disk:
            print(f"Error: reference '{ref_id}' not found in prefs and no directory exists.",
                  file=sys.stderr)
            sys.exit(cli_envelope.emit_error(
                args, "input_not_found",
                f"reference '{ref_id}' not found in prefs and no directory exists",
                field="delete", extra={"ref_id": ref_id},
                started_at=started_at,
            ))

        preview = _compute_delete_preview(prefs, ref_id, ref_dir)

        if not args.yes:
            # Existing prose preview to stderr (preserves the format users see today).
            print(f"Would delete reference: {ref_id}", file=sys.stderr)
            print(f"  path:    {ref_dir}{'' if on_disk else '  (not on disk)'}", file=sys.stderr)
            if preview['title']:
                print(f"  title:   {preview['title']}", file=sys.stderr)
            print(f"  frames:  {preview['frame_count']} file(s)", file=sys.stderr)
            if preview['used_by_profiles']:
                print(f"  used by: {len(preview['used_by_profiles'])} style profile(s) — "
                      f"{', '.join(preview['used_by_profiles'])}", file=sys.stderr)
                print(f"           (will be removed from each profile's references list)",
                      file=sys.stderr)
            else:
                print(f"  used by: (no style profiles)", file=sys.stderr)
            print(f"\nRe-run with --yes to confirm deletion.", file=sys.stderr)
            sys.exit(cli_envelope.emit_error(
                args, "confirmation_required",
                f"Add --yes to delete reference '{ref_id}'",
                field="delete",
                extra={"would_delete": preview,
                       "next": [f"python3 scripts/learn_design.py --delete {ref_id} --yes"]},
                started_at=started_at,
            ))

        remove_reference(prefs, ref_id, output_dir)
        save_prefs(prefs, prefs_path)
        print(f"Deleted reference: {ref_id}")
        sys.exit(cli_envelope.emit_success(args, {
            "mode": "delete",
            "ref_id": ref_id,
            "deleted": preview,
            "prefs_path": prefs_path,
        }, started_at=started_at))

    # -- Process inputs (add mode) --
    if not args.inputs:
        if cli_envelope.use_json(args):
            sys.exit(cli_envelope.emit_error(
                args, "input_invalid",
                "No action specified. Use --list, --show REF_ID, --delete REF_ID, "
                "or pass one or more positional inputs (URLs, videos, images).",
                started_at=started_at,
            ))
        parser.print_help()
        return

    existing_ids = set(prefs.get("design_references", {}).keys())
    # Parse --tags once for the whole add run; every new reference gets the
    # same list. Empty / whitespace-only tokens are filtered out.
    tags_list = [t.strip() for t in (args.tags or "").split(",") if t.strip()]
    profile_name = (args.profile or "").strip() or None
    # Track every ref_id added in this run so we can attach them to the
    # named profile in one go at the end.
    newly_added_ids = []
    images, videos, urls = [], [], []
    skipped = []
    for input_path in args.inputs:
        input_type = detect_input_type(input_path)
        if input_type == "image":
            images.append(input_path)
        elif input_type == "local_video":
            videos.append(input_path)
        elif input_type == "url":
            urls.append(input_path)
        elif input_type == "not_found":
            print(f"Warning: not found — skipping: {input_path}", file=sys.stderr)
            skipped.append({"input": input_path, "reason": "not_found"})
        else:
            print(f"Warning: unsupported file type — skipping: {input_path}", file=sys.stderr)
            skipped.append({"input": input_path, "reason": "unsupported"})

    if not images and not videos and not urls:
        sys.exit(cli_envelope.emit_error(
            args, "input_invalid",
            "No valid inputs provided",
            extra={"skipped": skipped,
                   "input_count": len(args.inputs)},
            started_at=started_at,
        ))

    result = {
        "mode": "add",
        "output_dir": output_dir,
        "name_arg": args.name,
        "profile": profile_name,
        "tags": tags_list,
        "images": [],
        "videos": [],
        "urls": [],
        "skipped": skipped,
    }

    # Multiple images → group into one reference
    if images:
        source = "images" if len(images) > 1 or (not videos and not urls) else images[0]
        ref_id = generate_reference_id(source, name=args.name, existing_ids=existing_ids)
        existing_ids.add(ref_id)
        ref_dir = create_reference_dir(output_dir, ref_id)

        print(f"\nProcessing {len(images)} image(s)")
        print(f"  Reference ID: {ref_id}")
        print(f"  Output: {ref_dir}")

        frames = copy_images(images, ref_dir)

        report = {
            "ref_id": ref_id,
            "source": images,
            "input_type": "images",
            "orientation": "unknown",
            "frame_count": len(frames),
            "frames": [os.path.relpath(f, ref_dir) for f in frames],
            "extracted_at": datetime.now(timezone.utc).isoformat(),
        }
        save_report(report, ref_dir)
        add_reference_index(prefs, ref_id=ref_id, title=args.name or "Image set", source_url=None, tags=tags_list)
        newly_added_ids.append(ref_id)
        print(f"  Extracted {len(frames)} frames")
        result['images'].append({
            "ref_id": ref_id, "source": images, "frame_count": len(frames),
            "ref_dir": ref_dir,
        })

    # Each video → separate reference
    for video_path in videos:
        ref_id = generate_reference_id(video_path, name=args.name, existing_ids=existing_ids)
        existing_ids.add(ref_id)
        ref_dir = create_reference_dir(output_dir, ref_id)

        print(f"\nProcessing video: {video_path}")
        print(f"  Reference ID: {ref_id}")
        print(f"  Output: {ref_dir}")

        w, h = get_video_dimensions(video_path)
        orientation = detect_orientation(w, h) if w and h else "unknown"
        duration = get_video_duration(video_path)
        frames = extract_video_frames(video_path, ref_dir)

        report = {
            "ref_id": ref_id,
            "source": video_path,
            "input_type": "local_video",
            "orientation": orientation,
            "frame_count": len(frames),
            "frames": [os.path.relpath(f, ref_dir) for f in frames],
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "duration_seconds": duration,
            "width": w,
            "height": h,
        }
        save_report(report, ref_dir)
        add_reference_index(prefs, ref_id=ref_id, title=os.path.basename(video_path), source_url=None, tags=tags_list)
        newly_added_ids.append(ref_id)
        print(f"  Extracted {len(frames)} frames")
        result['videos'].append({
            "ref_id": ref_id, "source": video_path, "frame_count": len(frames),
            "duration_seconds": duration, "orientation": orientation,
            "width": w, "height": h, "ref_dir": ref_dir,
        })

    # URLs → placeholder. URL screenshot extraction is NOT implemented (no
    # Playwright integration ships with this skill). The placeholder reserves
    # the ref_id and creates an empty frames/ directory so the user can drop
    # in screenshots manually; the report.json carries `needs_manual_frames`
    # so downstream readers know it's not ready for analysis yet.
    for url in urls:
        ref_id = generate_reference_id(url, name=args.name, existing_ids=existing_ids)
        existing_ids.add(ref_id)
        ref_dir = create_reference_dir(output_dir, ref_id)

        print(f"\nURL: {url}")
        print(f"  Reference ID: {ref_id}")
        print(f"  Output: {ref_dir}")
        print(f"  ⚠ URL capture is not implemented in this skill. Empty placeholder created.")
        print(f"    Drop screenshots into {ref_dir}/frames/ manually, then re-run --show {ref_id}.")

        report = {
            "ref_id": ref_id,
            "source": url,
            "input_type": "url",
            "orientation": "unknown",
            "frame_count": 0,
            "frames": [],
            "needs_manual_frames": True,
            "extracted_at": datetime.now(timezone.utc).isoformat(),
        }
        save_report(report, ref_dir)
        add_reference_index(prefs, ref_id=ref_id, title=url, source_url=url, tags=tags_list)
        newly_added_ids.append(ref_id)
        result['urls'].append({
            "ref_id": ref_id, "source": url, "needs_manual_frames": True, "ref_dir": ref_dir,
        })

    # Attach to style profile if --profile was passed. We use the existing
    # add_style_profile() helper with empty visual fields so the call is
    # idempotent for already-existing profiles (it unions references in).
    if profile_name and newly_added_ids:
        existing_profile = prefs.get("style_profiles", {}).get(profile_name, {})
        merged_refs = list(dict.fromkeys(
            (existing_profile.get("references") or []) + newly_added_ids,
        ))
        add_style_profile(
            prefs,
            name=profile_name,
            description=existing_profile.get("description", f"Profile '{profile_name}' (auto-created from learn_design)"),
            props_override=existing_profile.get("props_override") or {},
            preferred_layouts=existing_profile.get("preferred_layouts") or [],
            preferred_backgrounds=existing_profile.get("preferred_backgrounds"),
            animation_feel=existing_profile.get("animation_feel"),
            density=existing_profile.get("density"),
            references=merged_refs,
        )
        print(f"\nAttached {len(newly_added_ids)} reference(s) to style profile '{profile_name}'")
        result['profile_attached'] = profile_name
        result['profile_references'] = merged_refs

    save_prefs(prefs, prefs_path)
    print("\nDone. Pass the frames/ directory to your coding agent for design analysis.")
    sys.exit(cli_envelope.emit_success(args, result, started_at=started_at))


if __name__ == "__main__":
    main()
