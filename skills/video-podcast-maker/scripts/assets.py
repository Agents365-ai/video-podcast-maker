#!/usr/bin/env python3
"""Asset manifest manager for the per-video asset layer.

The manifest (videos/<name>/assets/manifest.json) is the single source of
truth for every visual/audio asset a video uses: user-supplied files, stock
assets fetched via assetSeeker, AI-generated stills/clips, and Hyperframes
overlay renders. Remotion components read it through --public-dir via the
useAssets() hook.

Subcommands:
    init     <video_dir>              create assets/ + an empty manifest
    add      <video_dir> --id ... --section ... --type ... --role ...
                                      register one asset (copies --file in)
    list     <video_dir>              list assets with status counts
    validate <video_dir>              schema + file-presence + license checks

Manifest schema (schema_version 1) — per-asset fields:
    id       unique slug within the manifest
    section  [SECTION:xxx] name the asset belongs to
    type     image | video | overlay | audio | icon | font
    role     background | inline | broll | overlay | bgm | sfx
    source   user | seek | imagen | videogen | hyperframes
    status   planned | pending_confirmation | resolved | failed
    path     relative to the video dir (required when resolved)
    license  provenance record (required when resolved; warning if absent)
    prompt / credit / cost_estimate / alpha / duration_s / fps   optional
"""
import argparse
import json
import os
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cli_envelope  # noqa: E402

SCHEMA_VERSION = 1

TYPES = ("image", "video", "overlay", "audio", "icon", "font")
ROLES = ("background", "inline", "broll", "overlay", "bgm", "sfx")
SOURCES = ("user", "seek", "imagen", "videogen", "hyperframes")
STATUSES = ("planned", "pending_confirmation", "resolved", "failed")

# Advisory pairing — a mismatch is a warning, not an error, because e.g. an
# animated GIF registered as image/broll can still be a deliberate choice.
ROLE_TYPE_COMPAT = {
    "background": {"image", "video"},
    "inline": {"image", "icon"},
    "broll": {"video"},
    "overlay": {"overlay"},
    "bgm": {"audio"},
    "sfx": {"audio"},
}


def manifest_path(video_dir):
    return Path(video_dir) / "assets" / "manifest.json"


def load_manifest(video_dir):
    """Return (manifest_dict, error_message). Missing file -> (None, None)."""
    path = manifest_path(video_dir)
    if not path.exists():
        return None, None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f), None
    except (json.JSONDecodeError, OSError) as e:
        return None, f"manifest unreadable: {e}"


def save_manifest(video_dir, manifest):
    path = manifest_path(video_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write("\n")


def validate_manifest(video_dir):
    """Validate the manifest. Returns (errors, warnings, manifest).

    Importable by verify_output.py — keep it side-effect free.
    A missing manifest is valid (text-only videos): ([], [], None).
    """
    video_dir = Path(video_dir)
    manifest, err = load_manifest(video_dir)
    if err:
        return [err], [], None
    if manifest is None:
        return [], [], None

    errors, warnings = [], []
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append(
            f"schema_version {manifest.get('schema_version')!r} != {SCHEMA_VERSION}")
    assets = manifest.get("assets")
    if not isinstance(assets, list):
        return errors + ["'assets' is not a list"], warnings, manifest

    seen_ids = set()
    for i, a in enumerate(assets):
        label = a.get("id") or f"assets[{i}]"
        for field in ("id", "section", "type", "role", "source", "status"):
            if not a.get(field):
                errors.append(f"{label}: missing required field '{field}'")
        if a.get("id"):
            if a["id"] in seen_ids:
                errors.append(f"{label}: duplicate id")
            seen_ids.add(a["id"])
        for field, allowed in (("type", TYPES), ("role", ROLES),
                               ("source", SOURCES), ("status", STATUSES)):
            if a.get(field) and a[field] not in allowed:
                errors.append(f"{label}: {field} '{a[field]}' not in {list(allowed)}")

        role, typ = a.get("role"), a.get("type")
        if role in ROLE_TYPE_COMPAT and typ in TYPES and typ not in ROLE_TYPE_COMPAT[role]:
            warnings.append(f"{label}: type '{typ}' is unusual for role '{role}'")

        if a.get("status") == "resolved":
            rel = a.get("path")
            if not rel:
                errors.append(f"{label}: resolved but has no 'path'")
            else:
                target = (video_dir / rel).resolve()
                if not str(target).startswith(str(video_dir.resolve()) + os.sep):
                    errors.append(f"{label}: path escapes the video directory")
                elif not target.exists():
                    errors.append(f"{label}: file not found: {rel}")
            if not a.get("license"):
                warnings.append(f"{label}: resolved asset has no license record")

    return errors, warnings, manifest


# ---- subcommands ------------------------------------------------------------

def cmd_init(args, started_at):
    video_dir = Path(args.video_dir)
    if not video_dir.is_dir():
        return cli_envelope.emit_error(
            args, "input_not_found", f"Video directory not found: {video_dir}",
            started_at=started_at)
    path = manifest_path(video_dir)
    created = not path.exists()
    if created:
        save_manifest(video_dir, {"schema_version": SCHEMA_VERSION, "assets": []})
    manifest, err = load_manifest(video_dir)
    if err:
        return cli_envelope.emit_error(args, "input_invalid", err, started_at=started_at)
    count = len(manifest["assets"])
    if not cli_envelope.use_json(args):
        state = "created" if created else f"already exists ({count} assets)"
        print(f"Manifest {state}: {path}")
    return cli_envelope.emit_success(args, {
        "manifest_path": str(path), "created": created, "asset_count": count,
    }, started_at=started_at)


def cmd_add(args, started_at):
    video_dir = Path(args.video_dir)
    if not video_dir.is_dir():
        return cli_envelope.emit_error(
            args, "input_not_found", f"Video directory not found: {video_dir}",
            started_at=started_at)
    if args.file and args.path:
        return cli_envelope.emit_error(
            args, "input_invalid", "--file and --path are mutually exclusive",
            started_at=started_at)

    manifest, err = load_manifest(video_dir)
    if err:
        return cli_envelope.emit_error(args, "input_invalid", err, started_at=started_at)
    if manifest is None:
        manifest = {"schema_version": SCHEMA_VERSION, "assets": []}

    existing = next((a for a in manifest["assets"] if a.get("id") == args.id), None)
    if existing and not args.replace:
        return cli_envelope.emit_error(
            args, "validation_failed",
            f"Asset id '{args.id}' already exists (use --replace to overwrite)",
            field="id", started_at=started_at)

    entry = {
        "id": args.id, "section": args.section,
        "type": args.type, "role": args.role, "source": args.source,
    }

    if args.file:
        src = Path(args.file)
        if not src.is_file():
            return cli_envelope.emit_error(
                args, "input_not_found", f"File not found: {src}",
                field="file", started_at=started_at)
        rel = f"assets/{args.id}{src.suffix.lower()}"
        dest = video_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        entry["path"] = rel
        entry["status"] = "resolved"
    elif args.path:
        target = (video_dir / args.path).resolve()
        if not str(target).startswith(str(video_dir.resolve()) + os.sep):
            return cli_envelope.emit_error(
                args, "input_invalid", f"--path escapes the video directory: {args.path}",
                field="path", started_at=started_at)
        if not target.is_file():
            return cli_envelope.emit_error(
                args, "input_not_found", f"File not found under video dir: {args.path}",
                field="path", started_at=started_at)
        entry["path"] = args.path
        entry["status"] = "resolved"
    else:
        # No file yet: a plan entry (generator sources fill it in later).
        entry["status"] = "pending_confirmation" if args.cost_estimate else "planned"

    if args.license:
        entry["license"] = args.license
    elif entry.get("status") == "resolved" and args.source == "user":
        entry["license"] = "user-owned"
    for field in ("prompt", "credit", "cost_estimate"):
        value = getattr(args, field)
        if value:
            entry[field] = value
    if args.alpha:
        entry["alpha"] = True
    if args.duration_s is not None:
        entry["duration_s"] = args.duration_s
    if args.fps is not None:
        entry["fps"] = args.fps

    if existing:
        manifest["assets"][manifest["assets"].index(existing)] = entry
    else:
        manifest["assets"].append(entry)
    save_manifest(video_dir, manifest)

    if not cli_envelope.use_json(args):
        verb = "Replaced" if existing else "Added"
        print(f"{verb} asset '{args.id}' ({entry['status']})"
              + (f" -> {entry.get('path')}" if entry.get("path") else ""))
    return cli_envelope.emit_success(args, {
        "asset": entry, "replaced": bool(existing),
        "asset_count": len(manifest["assets"]),
    }, started_at=started_at)


def cmd_list(args, started_at):
    manifest, err = load_manifest(args.video_dir)
    if err:
        return cli_envelope.emit_error(args, "input_invalid", err, started_at=started_at)
    assets = manifest["assets"] if manifest else []
    by_status = {}
    for a in assets:
        by_status[a.get("status", "?")] = by_status.get(a.get("status", "?"), 0) + 1
    if not cli_envelope.use_json(args):
        if manifest is None:
            print("No manifest (text-only video).")
        for a in assets:
            print(f"  [{a.get('status', '?'):<22}] {a.get('id', '?'):<24} "
                  f"{a.get('section', '?'):<14} {a.get('role', '?'):<10} "
                  f"{a.get('source', '?'):<11} {a.get('path', '')}")
        print(f"{len(assets)} assets " + json.dumps(by_status, ensure_ascii=False))
    return cli_envelope.emit_success(args, {
        "manifest_exists": manifest is not None,
        "assets": assets, "count": len(assets), "by_status": by_status,
    }, started_at=started_at)


def cmd_validate(args, started_at):
    errors, warnings, manifest = validate_manifest(args.video_dir)
    if not cli_envelope.use_json(args):
        if manifest is None and not errors:
            print("No manifest (text-only video) — nothing to validate.")
        for e in errors:
            print(f"  ✗ {e}")
        for w in warnings:
            print(f"  ⚠ {w}")
        if manifest is not None and not errors:
            print(f"Manifest valid ({len(manifest.get('assets', []))} assets, "
                  f"{len(warnings)} warnings).")
    data = {
        "manifest_exists": manifest is not None,
        "valid": not errors, "errors": errors, "warnings": warnings,
        "asset_count": len(manifest.get("assets", [])) if manifest else 0,
    }
    if errors:
        return cli_envelope.emit_error(
            args, "validation_failed",
            f"{len(errors)} manifest error(s)", extra={"details": data},
            started_at=started_at)
    return cli_envelope.emit_success(args, data, started_at=started_at)


# ---- parser ------------------------------------------------------------------

def build_parser():
    p = argparse.ArgumentParser(
        prog="assets.py",
        description="Manage the per-video asset manifest (assets/manifest.json).")
    sub = p.add_subparsers(dest="command", required=True, metavar="<command>")

    sp = sub.add_parser("init", help="Create assets/ + an empty manifest")
    sp.add_argument("video_dir", help="Path to videos/<name>/")
    cli_envelope.add_format_arg(sp)

    sp = sub.add_parser("add", help="Register one asset in the manifest")
    sp.add_argument("video_dir", help="Path to videos/<name>/")
    sp.add_argument("--id", required=True, help="Unique asset slug")
    sp.add_argument("--section", required=True, help="[SECTION:xxx] name it belongs to")
    sp.add_argument("--type", required=True, choices=TYPES)
    sp.add_argument("--role", required=True, choices=ROLES)
    sp.add_argument("--source", default="user", choices=SOURCES)
    sp.add_argument("--file", help="External file to copy into assets/ (user assets)")
    sp.add_argument("--path", help="Path relative to video_dir of an already-placed file")
    sp.add_argument("--license", help="License / provenance record")
    sp.add_argument("--prompt", help="Generation prompt (imagen/videogen/hyperframes)")
    sp.add_argument("--credit", help="Attribution URL or text")
    sp.add_argument("--cost-estimate", dest="cost_estimate",
                    help="Cost quote for paid generation (marks pending_confirmation)")
    sp.add_argument("--alpha", action="store_true", help="Asset has an alpha channel")
    sp.add_argument("--duration-s", dest="duration_s", type=float,
                    help="Duration in seconds (video/overlay/audio)")
    sp.add_argument("--fps", type=int, help="Frame rate (overlay renders must be 30)")
    sp.add_argument("--replace", action="store_true",
                    help="Overwrite an existing entry with the same id")
    cli_envelope.add_format_arg(sp)

    sp = sub.add_parser("list", help="List assets with status counts")
    sp.add_argument("video_dir", help="Path to videos/<name>/")
    cli_envelope.add_format_arg(sp)

    sp = sub.add_parser("validate", help="Schema + file-presence + license checks")
    sp.add_argument("video_dir", help="Path to videos/<name>/")
    cli_envelope.add_format_arg(sp)

    return p


def main():
    started_at = time.time()
    args = build_parser().parse_args()
    handler = {"init": cmd_init, "add": cmd_add,
               "list": cmd_list, "validate": cmd_validate}[args.command]
    try:
        sys.exit(handler(args, started_at))
    except SystemExit:
        raise
    except Exception as e:  # keep the envelope contract even on bugs
        sys.exit(cli_envelope.emit_error(
            args, "internal_error", f"{type(e).__name__}: {e}", started_at=started_at))


if __name__ == "__main__":
    main()
