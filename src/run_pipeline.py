#!/usr/bin/env python3
"""Minimal vertical slice of Dark Matter pipeline.

Usage:
    python run_pipeline.py [--input <path>] [--store <path>]
"""

import sys
import json
from pathlib import Path

# Add parent to path so we can import dm
sys.path.insert(0, str(Path(__file__).parent))
from dm.pipeline import Pipeline


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Dark Matter Intelligence Pipeline")
    parser.add_argument("--input", default="input", help="Path to repository to analyze")
    parser.add_argument("--store", default=None, help="Path for .darkmatter store (default: input/.darkmatter)")
    args = parser.parse_args()

    input_path = Path(__file__).parent.parent / args.input if not Path(args.input).is_absolute() else Path(args.input)
    if not input_path.exists():
        print(f"Error: input path '{input_path}' does not exist")
        sys.exit(1)

    pipeline = Pipeline(str(input_path), args.store)
    result = pipeline.run()

    print(f"\n{'='*50}")
    print(f"  AETHER v0.1 — Vertical Slice Complete")
    print(f"{'='*50}")
    print(f"  Evidence collected:    {result['evidence_count']}")
    print(f"  Nodes created:         {result['nodes_created']}")
    print(f"  Edges created:         {result['edges_created']}")
    print(f"  Facts derived:         {result['facts_derived']}")
    print(f"  Verifications:         {result['verifications_recorded']}")
    print(f"{'='*50}")
    print(f"  Outputs:")
    print(f"    Markdown:  {result['outputs']['markdown']}")
    print(f"    .ai Pkg:   {result['outputs']['ai_package']}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
