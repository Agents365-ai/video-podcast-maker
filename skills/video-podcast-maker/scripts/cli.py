#!/usr/bin/env python3
"""Top-level dispatcher for the video-podcast-maker CLI suite.

Provides a single hierarchical entry point so agents can discover the
suite without reading 10 individual --help screens. Forwards to the
underlying scripts via subprocess; existing direct invocations
(e.g. `python3 scripts/generate_tts.py ...`) keep working unchanged.

Usage:
    cli.py --help                       # list resources
    cli.py <resource> --help            # list actions for a resource
    cli.py <resource> <action> --help   # forwards --help to the underlying script
    cli.py schema <method>              # JSON schema for one action (e.g. tts.run)
    cli.py schema                       # list all known methods

Resources / actions:
    tts       run | validate
    verify
    align
    audit     beats
    shorts    gen
    design    list | show | delete | add
    assets    init | add | list | validate
    prereqs
    prefs     get | migrate | backend | bgm-path
    schema    [<method>]
"""
import argparse
import importlib
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cli_envelope  # noqa: E402


SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))


# Single source of truth for what each method does, where it lives, and
# what args to inject before the user's args. Adding a new action means
# adding one entry here and one parser line in build_parser().
ACTIONS = {
    'tts.run': {
        'script': 'generate_tts.py',
        'prepend': [],
        'parser_attr': 'build_parser',
        'description': 'Synthesize audio + SRT + timing.json from podcast.txt',
    },
    'tts.validate': {
        'script': 'generate_tts.py',
        'prepend': ['--validate'],
        'parser_attr': 'build_parser',
        'description': 'Validate podcast.txt format without calling TTS API',
    },
    'verify': {
        'script': 'verify_output.py',
        'prepend': [],
        'parser_attr': 'build_parser',
        'description': 'End-of-pipeline acceptance gate (file presence, specs, drift)',
    },
    'align': {
        'script': 'align_timing_from_srt.py',
        'prepend': [],
        'parser_attr': 'build_parser',
        'description': 'Anchor timing.json slides to real audio/SRT timestamps',
    },
    'audit.beats': {
        'script': 'audit_beat_sync.py',
        'prepend': [],
        'parser_attr': 'build_parser',
        'description': 'Audit beat-vs-narration alignment in a Remotion video.tsx',
    },
    'shorts.gen': {
        'script': 'generate_shorts.py',
        'prepend': [],
        'parser_attr': 'build_parser',
        'description': 'Generate vertical shorts assets from a video directory',
    },
    'design.list': {
        'script': 'learn_design.py',
        'prepend': ['--list'],
        'parser_attr': '_build_parser',
        'description': 'List all design references',
    },
    'design.show': {
        'script': 'learn_design.py',
        'prepend': ['--show'],
        'parser_attr': '_build_parser',
        'description': 'Show report.json for a reference (positional arg = REF_ID)',
    },
    'design.delete': {
        'script': 'learn_design.py',
        'prepend': ['--delete'],
        'parser_attr': '_build_parser',
        'description': 'Delete a reference (gated by --yes; positional arg = REF_ID)',
    },
    'design.add': {
        'script': 'learn_design.py',
        'prepend': [],
        'parser_attr': '_build_parser',
        'description': 'Add design references (URLs / videos / images as positional args)',
    },
    'assets.init': {
        'script': 'assets.py',
        'prepend': ['init'],
        'parser_attr': 'build_parser',
        'description': 'Create assets/ + an empty asset manifest for a video',
    },
    'assets.add': {
        'script': 'assets.py',
        'prepend': ['add'],
        'parser_attr': 'build_parser',
        'description': 'Register one asset (user file / stock / generated) in the manifest',
    },
    'assets.list': {
        'script': 'assets.py',
        'prepend': ['list'],
        'parser_attr': 'build_parser',
        'description': 'List manifest assets with status counts',
    },
    'assets.validate': {
        'script': 'assets.py',
        'prepend': ['validate'],
        'parser_attr': 'build_parser',
        'description': 'Validate the asset manifest (schema, files, licenses)',
    },
    'prereqs': {
        'script': 'check_prereqs.py',
        'prepend': [],
        'parser_attr': 'build_parser',
        'description': 'Pre-flight check: required CLIs + backend env vars',
    },
    'prefs.get': {
        'script': 'get_pref.py',
        'prepend': [],
        'parser_attr': 'build_parser',
        'description': 'Read a nested value from user_prefs.json (e.g. global tts rate)',
    },
    'prefs.migrate': {
        'script': 'migrate_prefs.py',
        'prepend': [],
        'parser_attr': 'build_parser',
        'description': 'Migrate user_prefs.json to the current schema version',
    },
    'prefs.backend': {
        'script': 'resolve_backend.py',
        'prepend': [],
        'parser_attr': None,
        'description': 'Print the resolved TTS backend name',
    },
    'prefs.bgm-path': {
        'script': 'resolve_bgm_path.py',
        'prepend': [],
        'parser_attr': None,
        'description': 'Print the resolved absolute BGM file path',
    },
}


def build_parser():
    p = argparse.ArgumentParser(
        prog='cli.py',
        description=__doc__.split("\n\n")[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Run 'cli.py <resource> --help' for resource-level help, "
               "or 'cli.py schema' to list all methods.",
    )
    sub = p.add_subparsers(dest='resource', metavar='<resource>')

    # Resources with sub-actions
    _build_resource(sub, 'tts', 'Text-to-speech pipeline',
                     ['run', 'validate'])
    _build_resource(sub, 'audit', 'Pre-render audits',
                     ['beats'])
    _build_resource(sub, 'shorts', 'Vertical shorts generation',
                     ['gen'])
    _build_resource(sub, 'design', 'Design reference library',
                     ['list', 'show', 'delete', 'add'])
    _build_resource(sub, 'assets', 'Per-video asset manifest',
                     ['init', 'add', 'list', 'validate'])
    _build_resource(sub, 'prefs', 'User preferences',
                     ['get', 'migrate', 'backend', 'bgm-path'])

    # Leaf resources (the resource is itself the action)
    _build_leaf(sub, 'verify', ACTIONS['verify']['description'])
    _build_leaf(sub, 'align', ACTIONS['align']['description'])
    _build_leaf(sub, 'prereqs', ACTIONS['prereqs']['description'])

    # schema subcommand — uses cli_envelope envelope on stdout
    schema = sub.add_parser('schema', help='Print parameter schema for an action')
    schema.add_argument('method', nargs='?', default=None,
                         help='Method ID like "tts.run". Omit to list all known methods.')
    cli_envelope.add_format_arg(schema)

    return p


def _build_resource(sub, resource, description, action_names):
    rp = sub.add_parser(resource, help=description,
                         formatter_class=argparse.RawDescriptionHelpFormatter,
                         epilog="Actions: " + ", ".join(action_names))
    rs = rp.add_subparsers(dest='action', metavar='<action>')
    for name in action_names:
        action_id = f"{resource}.{name}"
        info = ACTIONS[action_id]
        # add_help=False so --help is forwarded to the underlying script
        ap = rs.add_parser(name, help=info['description'], add_help=False)
        ap.add_argument('forwarded_args', nargs=argparse.REMAINDER)


def _build_leaf(sub, resource, description):
    lp = sub.add_parser(resource, help=description, add_help=False)
    lp.add_argument('forwarded_args', nargs=argparse.REMAINDER)


def dispatch(action_id, forwarded_args):
    """Run the underlying script. Returns its exit code."""
    info = ACTIONS[action_id]
    script_path = os.path.join(SCRIPTS_DIR, info['script'])
    cmd = [sys.executable, script_path] + info['prepend'] + list(forwarded_args)
    return subprocess.run(cmd).returncode


# ---- schema introspection -------------------------------------------------

def emit_schema(args):
    """Emit JSON schema for one action, or list all actions when method is omitted."""
    if args.method is None:
        # Listing mode
        sys.exit(cli_envelope.emit_success(args, {
            "methods": [
                {"method": k, "script": v['script'], "description": v['description']}
                for k, v in sorted(ACTIONS.items())
            ],
            "count": len(ACTIONS),
        }))

    if args.method not in ACTIONS:
        sys.exit(cli_envelope.emit_error(
            args, "input_invalid",
            f"Unknown method '{args.method}'. "
            f"Run 'cli.py schema' (no arg) to list available methods.",
            field="method",
        ))

    info = ACTIONS[args.method]
    parser_obj = _try_introspect_parser(info)
    schema_data = {
        "method": args.method,
        "script": info['script'],
        "prepend_args": info['prepend'],
        "description": info['description'],
        "params": _params_from_parser(parser_obj) if parser_obj else None,
        "introspection": "argparse" if parser_obj else "unavailable",
    }
    if parser_obj is None:
        schema_data["help_command"] = (
            f"python3 scripts/cli.py {args.method.replace('.', ' ')} --help"
        )
    sys.exit(cli_envelope.emit_success(args, schema_data))


def _try_introspect_parser(info):
    """Try to load the underlying script's parser. Returns parser or None."""
    if info['parser_attr'] is None:
        return None
    script_name = info['script'][:-3]  # strip .py
    try:
        mod = importlib.import_module(script_name)
    except Exception:
        return None
    builder = getattr(mod, info['parser_attr'], None)
    if builder is None:
        return None
    try:
        return builder()
    except Exception:
        return None


def _params_from_parser(parser):
    """Convert argparse parser actions to a JSON-serializable schema dict."""
    params = {}
    for action in parser._actions:
        if action.dest in ('help', 'forwarded_args') or action.dest.startswith('_'):
            continue
        default = action.default
        if default is argparse.SUPPRESS:
            default = None
        params[action.dest] = {
            "type": _type_name(action.type),
            "required": getattr(action, 'required', False),
            "default": default,
            "choices": list(action.choices) if action.choices else None,
            "help": (action.help or "").strip(),
            "flag": action.option_strings[0] if action.option_strings else None,
            "positional": not action.option_strings,
        }
    return params


def _type_name(t):
    if t is int:
        return "integer"
    if t is float:
        return "number"
    if t is bool:
        return "boolean"
    return "string"


# Resources with sub-actions vs leaf resources. The leaves are themselves
# the action — there's no second positional. Both lists are derived from
# ACTIONS keys but kept explicit so the routing is readable.
_RESOURCES_WITH_ACTIONS = {'tts', 'audit', 'shorts', 'design', 'assets', 'prefs'}
_LEAF_RESOURCES = {'verify', 'align', 'prereqs'}


def main():
    """Manual argv slicing — argparse REMAINDER + nested subparsers
    misorders args (top-level parse_known_args intercepts flags as
    'unknown' before the subparser's REMAINDER can consume them).
    Argparse is still used for the help tree (build_parser) and the
    schema subcommand, but routing reads sys.argv directly.
    """
    argv = sys.argv[1:]

    if not argv or argv[0] in ('-h', '--help'):
        build_parser().print_help()
        sys.exit(0)

    cmd = argv[0]
    rest = argv[1:]

    # Schema subcommand — full argparse handles it (no forwarding)
    if cmd == 'schema':
        parser = build_parser()
        args = parser.parse_args(argv)
        emit_schema(args)
        return  # not reached — emit_* always sys.exit

    # Resources with sub-actions
    if cmd in _RESOURCES_WITH_ACTIONS:
        if not rest or rest[0] in ('-h', '--help'):
            # Resource-level help via argparse (calls sys.exit internally)
            build_parser().parse_args([cmd, '--help'])
            return
        action = rest[0]
        action_id = f"{cmd}.{action}"
        forwarded = rest[1:]
    elif cmd in _LEAF_RESOURCES:
        action_id = cmd
        forwarded = rest
    else:
        # Unknown resource — let argparse give the user the canonical error
        build_parser().parse_args(argv)
        return  # not reached

    if action_id not in ACTIONS:
        print(f"cli.py: unknown action '{rest[0]}' under '{cmd}'. "
              f"Run 'cli.py {cmd} --help' to see available actions.",
              file=sys.stderr)
        sys.exit(2)

    sys.exit(dispatch(action_id, forwarded))


if __name__ == '__main__':
    main()
