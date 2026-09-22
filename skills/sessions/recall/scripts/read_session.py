#!/usr/bin/env python3
"""Print readable excerpts from a coding-agent session transcript.

Converts the .jsonl (Claude Code or Codex -- detected automatically) into plain
conversation text, keeping only turns that match the search terms plus surrounding turns
for context. Tool call bodies and tool results are summarised, not dumped -- they are the
bulk of a transcript and rarely the context worth recovering.

Usage:
    read_session.py SESSION.jsonl [--terms T [T ...]] [--window N] [--max-chars N] [--full]
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stores import store_for  # noqa: E402

ROLE_LABEL = {"user": "USER", "assistant": "AGENT"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("session")
    ap.add_argument("--terms", nargs="*", default=[])
    ap.add_argument("--window", type=int, default=2, help="Turns of context around each match")
    ap.add_argument("--max-chars", type=int, default=60_000)
    ap.add_argument("--full", action="store_true", help="Every turn, not just matches")
    args = ap.parse_args()

    store = store_for(args.session)
    turns = []
    with open(args.session, "r", errors="replace") as fh:
        for line in fh:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            t = store.turn(d)
            if t and t[1].strip():
                turns.append((t[0], t[1], d.get("timestamp", "")[:19]))

    if not turns:
        print("No conversation turns found.", file=sys.stderr)
        return 1

    if args.full or not args.terms:
        keep = set(range(len(turns)))
    else:
        pat = re.compile("|".join(re.escape(t) for t in args.terms), re.I)
        keep = set()
        for i, (_, text, _) in enumerate(turns):
            if pat.search(text):
                keep.update(range(max(0, i - args.window), min(len(turns), i + args.window + 1)))

    if not keep:
        print(f"No turns matched {args.terms} in this session.", file=sys.stderr)
        return 0

    out, total, last = [f"[{store.label} session]"], 0, -1
    for i in sorted(keep):
        if i != last + 1:
            out.append("\n... (skipped) ...\n")
        role, text, ts = turns[i]
        block = f"\n=== {ROLE_LABEL.get(role, role)} {ts} ===\n{text}"
        if total + len(block) > args.max_chars:
            if total == 0:  # never come back empty-handed
                out.append(block[: args.max_chars])
            out.append(f"\n[truncated at {args.max_chars} chars -- narrow --terms to see more]")
            break
        out.append(block)
        total += len(block)
        last = i
    print("".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
