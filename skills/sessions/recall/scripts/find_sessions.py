#!/usr/bin/env python3
"""Rank past coding-agent sessions by relevance to a set of search terms.

Scans every session store found on this machine (Claude Code, Codex -- see stores.py),
scores each session on term hits, and prints a ranked table with each session's topic
(its first real user prompt).

Never prints transcript bodies -- only metadata. Safe to run into context.

Usage:
    find_sessions.py TERM [TERM ...] [--agent claude|codex] [--cwd PATH] [--days N]
                     [--limit N] [--this-project-only]
"""
import argparse
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stores import STORES, encode_cwd  # noqa: E402


def term_hits(terms, roots):
    """Map file path -> total match count across all terms, case-insensitive.

    One pass over each file for all terms. Plain Python on purpose: no ripgrep
    dependency, and it beats BSD `grep -i` by ~20x on a multi-GB store.
    """
    needles = [(t, t.lower().encode()) for t in terms]
    hits = defaultdict(int)
    per_term = defaultdict(set)
    for root in roots:
        for dirpath, _, files in os.walk(root):
            for f in files:
                if not f.endswith(".jsonl"):
                    continue
                path = os.path.join(dirpath, f)
                try:
                    with open(path, "rb") as fh:
                        data = fh.read().lower()
                except OSError:
                    continue
                for term, needle in needles:
                    n = data.count(needle)
                    if n:
                        hits[path] += n
                        per_term[path].add(term)
    return hits, per_term


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("terms", nargs="+")
    ap.add_argument("--agent", choices=sorted(STORES), action="append",
                    help="Only search this agent's sessions (repeatable). Default: every store found")
    ap.add_argument("--cwd", default=os.getcwd(), help="Working dir whose sessions rank first")
    ap.add_argument("--days", type=int, default=0, help="Only sessions modified in the last N days")
    ap.add_argument("--limit", type=int, default=12)
    ap.add_argument("--this-project-only", action="store_true")
    args = ap.parse_args()

    stores = [STORES[n] for n in (args.agent or STORES)]
    stores = [s for s in stores if s.available()]
    if not stores:
        looked = ", ".join(str(r) for s in STORES.values() for r in s.roots())
        print(f"No session stores found (looked in {looked})", file=sys.stderr)
        return 1

    roots, owner = [], {}
    for s in stores:
        for r in s.roots():
            if r.is_dir():
                roots.append(r)
                owner[str(r)] = s

    hits, per_term = term_hits(args.terms, roots)
    if not hits:
        print(f"No sessions matched: {', '.join(args.terms)}")
        return 0

    current = encode_cwd(str(Path(args.cwd).resolve()))
    cutoff = time.time() - args.days * 86400 if args.days else 0
    rows = []
    for path, count in hits.items():
        store = next((owner[r] for r in owner if path.startswith(r + os.sep)), None)
        if store is None or store.skip(path):
            continue
        p = Path(path)
        try:
            mtime = p.stat().st_mtime
        except OSError:
            continue
        if mtime < cutoff:
            continue
        project = store.project_key(p)
        if args.this_project_only and project != current:
            continue
        # Rank: distinct terms matched dominates, then depth of engagement (hit count).
        # The current-project bonus is deliberately small -- a tiebreaker only. Making it
        # large buries a heavily-relevant session in a sibling project under a passing
        # one-line mention in the current one.
        distinct = len(per_term[path])
        score = distinct * 1000 + min(count, 500) + (60 if project == current else 0)
        rows.append((score, mtime, count, distinct, project, store, p))

    rows.sort(key=lambda r: (-r[0], -r[1]))
    rows = rows[: args.limit]

    searched = ", ".join(s.label for s in stores)
    print(f"{len(rows)} candidate session(s) for: {', '.join(args.terms)}  [searched: {searched}]\n")
    for score, mtime, count, distinct, project, store, p in rows:
        when = time.strftime("%Y-%m-%d %H:%M", time.localtime(mtime))
        here = " *THIS PROJECT*" if project == current else ""
        size = p.stat().st_size / 1_000_000
        print(f"{when}  {count:>4} hits  {distinct}/{len(args.terms)} terms  {size:.1f}MB  "
              f"[{store.name}]{here}")
        print(f"  {project}")
        print(f"  {p}")
        topic = store.topic(p)
        if topic:
            print(f"  topic: {topic}")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
