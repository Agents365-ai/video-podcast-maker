#!/usr/bin/env python3
"""Read a nested value from user_prefs.json and print it.

Used by SKILL.md / workflow shell snippets:

    BGM_VOL=$(python3 get_pref.py global bgm volume --default 0.10)

Default --format is 'prose' (bare value to stdout, exit 0) so shell
$(...) captures keep working unchanged. Pass --format json to get the
standard envelope for agent consumption:

    {"ok": true,
     "data": {"keys": [...], "value": ..., "used_default": bool, "default": ...},
     "meta": {...}}

NOTE: --format does not include 'auto' — auto-detect would emit JSON
when stdout is piped (the typical shell case), which would break the
back-compat contract that workflow-production.md and SKILL.md rely on.
Agents and orchestrators must opt in to JSON explicitly.
"""
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cli_envelope  # noqa: E402
from tts.backends import user_prefs_get  # noqa: E402


def build_parser():
    parser = argparse.ArgumentParser(
        description=__doc__.split('\n\n')[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('keys', nargs='+', help='Nested key path, e.g. global tts rate')
    parser.add_argument('--default', default='', help='Value to print if key is missing')
    # Custom --format (no 'auto') so $(...) capture stays a bare value.
    parser.add_argument('--format', choices=('json', 'prose'), default='prose',
                        help="Output format. Default 'prose' prints the bare value "
                             "(preserves shell $(...) capture). 'json' emits the "
                             "standard cli_envelope shape on stdout.")
    return parser


def main():
    args = build_parser().parse_args()
    started_at = time.time()

    val = user_prefs_get(*args.keys)
    used_default = val is None
    if used_default:
        val = args.default

    if args.format == 'json':
        sys.exit(cli_envelope.emit_success(args, {
            "keys": args.keys,
            "value": val,
            "used_default": used_default,
            "default": args.default,
        }, started_at=started_at))
    print(val)
    sys.exit(0)


if __name__ == '__main__':
    main()
