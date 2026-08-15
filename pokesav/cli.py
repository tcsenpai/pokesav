#!/usr/bin/env python3
"""
pokesav — Pokémon save file parser.

Usage:
    pokesav <savefile.sav> [--json] [--gen N]

Auto-detects generation and prints game state + story guidance.
"""

import argparse
import json
import sys
from pathlib import Path

from . import GENERATIONS
from .detect import detect_generation, get_game_name


def main():
    parser = argparse.ArgumentParser(
        prog="pokesav",
        description="Parse Pokémon save files and get story guidance.",
    )
    parser.add_argument("savefile", help="Path to .sav file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--gen", type=int, help="Override generation detection (3-8)")
    args = parser.parse_args()

    filepath = args.savefile
    if not Path(filepath).exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    # Detect generation
    gen = args.gen or detect_generation(filepath)
    if gen is None:
        print("Error: Could not detect generation. Use --gen to specify.", file=sys.stderr)
        sys.exit(1)

    if gen not in GENERATIONS:
        print(f"Error: Generation {gen} is not yet supported.", file=sys.stderr)
        print(f"Supported: {', '.join(f'Gen {g}' for g in sorted(GENERATIONS))}", file=sys.stderr)
        sys.exit(1)

    # Parse
    module_name = GENERATIONS[gen]
    if module_name == "gen5":
        from .gen5 import parse, format_text
    else:
        print(f"Error: Parser for {module_name} not implemented.", file=sys.stderr)
        sys.exit(1)

    result = parse(filepath)

    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    # Output
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
