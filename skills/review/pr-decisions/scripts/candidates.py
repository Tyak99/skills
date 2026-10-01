#!/usr/bin/env python3
"""List lines in a diff that look like they set a value someone will later ask "why?" about.

Reads a unified diff (git diff, gh pr diff, glab mr diff) on stdin, prints one candidate per
line as `path:line  [kind]  code`, plus `was: ...` when the same hunk removed a line setting the
same key. This is a sweep for recall, not a verdict: expect noise, and expect to judge each hit.

    git diff origin/main...HEAD | python3 candidates.py
    gh pr diff 123 | python3 candidates.py --include-tests
"""

import argparse
import re
import sys

UNIT = re.compile(
    r"(?<![\w.])\d+(?:\.\d+)?\s*(?:ms|msec|s|sec|secs|seconds?|m|mins?|minutes?|h|hrs?|hours?|"
    r"d|days?|w|weeks?|[kmgt]i?b|bytes?|%|usd|dollars?)\b",
    re.I,
)
KEYWORD = re.compile(
    r"(timeout|limit|max|min|cap|budget|cost|retr(?:y|ies)|attempts?|threshold|ttl|interval|delay|"
    r"backoff|wait|sleep|batch|chunk|page_?size|per_?page|concurren|parallel|workers?|rate|quota|"
    r"window|expir|lifetime|size|length|count|port|severity|score|percent|ratio|top_?k|tokens?|"
    r"slice|head|tail|take|truncat|poll|tries|cutoff|floor|ceil)",
    re.I,
)
DIGIT = re.compile(r"(?<![\w.])\d[\d_]*(?:\.\d+)?(?![\w.])")  # 5_000_000 counts as one number
ENV_DEFAULT = re.compile(
    r"(process\.env\.\w+\s*(\|\||\?\?)|os\.environ\.get\(|os\.getenv\(|getenv\(|ENV\.fetch\(|"
    r"\$\{\w+:-|env\.\w+\s*(\|\||\?\?)|\bnum\(\s*env)",
)
FLAG = re.compile(
    r"(enabled?|disabled?|allow\w*|deny\w*|skip\w*|ignore\w*|exclude\w*|strict|force|dry_?run|"
    r"read_?only|public|private|verify|insecure|fail_?(?:open|closed|fast|soft)|required|optional|"
    r"interruptible|protected|masked|manual|debug|verbose|cache)"
    r"\w*\s*[:=]\s*(true|false|yes|no|on|off|none|null|\[)",
    re.I,
)
CLI_FLAG = re.compile(r"['\"]--(?:no-)?[a-z][\w-]*['\"]|\s--(?:no-)?[a-z][\w-]*[ =]\S")
SILENT = re.compile(
    r"(except\s*(\w+\s*)?:\s*(pass|continue)|catch\s*(\(\w*\))?\s*\{\s*(/\*.*?\*/)?\s*\}|"
    r"\|\|\s*true\b|allow_failure|continue-on-error|2>\s*/dev/null|\.catch\(\s*\(\)\s*=>\s*\{?\s*\}?\)|"
    r"exit\s+0\b|process\.exit\(0\))",
    re.I,
)
BOUND = re.compile(r"[<>]=?\s*(\d[\d_]*)\b")  # loop and guard bounds: i < 6, n >= 50
KEY = re.compile(r"^\s*[-+]?\s*[\"']?([A-Za-z_][\w.-]*)[\"']?\s*[:=]")

COMMENT = re.compile(r"^\s*(#|//|/\*|\*|<!--|--\s|;)")
LOCKFILES = re.compile(
    r"(package-lock\.json|yarn\.lock|pnpm-lock\.yaml|poetry\.lock|Pipfile\.lock|Gemfile\.lock|"
    r"Cargo\.lock|go\.sum|composer\.lock|\.terraform\.lock\.hcl)$"
)
TESTS = re.compile(r"(^|/)(tests?|__tests__|spec|fixtures?|__snapshots__)/|[._-](test|spec)\.\w+$")
DOCS = re.compile(r"\.(md|mdx|rst|txt|adoc)$", re.I)
BINARY_ISH = re.compile(r"\.(svg|png|jpe?g|gif|ico|pdf|min\.js|map|snap)$", re.I)
HUNK = re.compile(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def kinds(code):
    found = []
    if SILENT.search(code):
        found.append("fails-soft")
    if ENV_DEFAULT.search(code):
        found.append("default")
    if FLAG.search(code):
        found.append("switch")
    if UNIT.search(code):
        found.append("unit")
    elif KEYWORD.search(code) and any(float(d.replace("_", "")) not in (0, 1) for d in DIGIT.findall(code)):
        found.append("number")  # 0 and 1 are almost always indexes and emptiness checks
    if not found and any(float(d.replace("_", "")) not in (0, 1) for d in BOUND.findall(code)):
        found.append("bound")
    if not found and CLI_FLAG.search(code):
        found.append("cli-flag")
    return found


def key_of(code):
    m = KEY.match(code)
    return m.group(1).lower() if m else None


def skip_path(path, args):
    if not path or path == "/dev/null":
        return True
    if LOCKFILES.search(path) or BINARY_ISH.search(path):
        return True
    if not args.include_tests and TESTS.search(path):
        return True
    if not args.include_docs and DOCS.search(path):
        return True
    return False


def parse(lines, args):
    path, new_line, hunk_removed, hunk_added = None, 0, [], []
    out = []

    def flush():
        removed_by_key = {}
        for text in hunk_removed:
            k = key_of(text)
            if k:
                removed_by_key.setdefault(k, text.strip())
        for p, n, ks, text in hunk_added:
            k = key_of(text)
            was = removed_by_key.get(k) if k else None
            out.append((p, n, ks, text.strip(), was))
        hunk_removed.clear()
        hunk_added.clear()

    for raw in lines:
        line = raw.rstrip("\n")
        if line.startswith("diff --git") or line.startswith("+++ ") or line.startswith("--- "):
            flush()
            if line.startswith("+++ "):
                target = line[4:].strip()
                path = target[2:] if target.startswith("b/") else target
            continue
        m = HUNK.match(line)
        if m:
            flush()
            new_line = int(m.group(2))
            continue
        if skip_path(path, args):
            continue
        if line.startswith("+"):
            code = line[1:]
            if code.strip() and not COMMENT.match(code) and len(code) < 400:
                ks = kinds(code)
                if ks:
                    hunk_added.append((path, new_line, ks, code))
            new_line += 1
        elif line.startswith("-"):
            hunk_removed.append(line[1:])
        elif line.startswith(" "):
            new_line += 1
    flush()
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--include-tests", action="store_true", help="also scan test and fixture files")
    ap.add_argument("--include-docs", action="store_true", help="also scan Markdown and other docs")
    ap.add_argument("--limit", type=int, default=400, help="max candidates to print (default 400)")
    args = ap.parse_args()

    found = parse(sys.stdin, args)
    if not found:
        print("No candidates. The change may still make decisions a pattern can't see — read the diff.")
        return

    for path, n, ks, code, was in found[: args.limit]:
        print(f"{path}:{n}  [{','.join(ks)}]  {code}")
        if was:
            print(f"    was: {was}")

    per_file = {}
    for path, *_ in found:
        per_file[path] = per_file.get(path, 0) + 1
    print(f"\n{len(found)} candidate(s) in {len(per_file)} file(s)"
          + (f"; showing first {args.limit}" if len(found) > args.limit else ""))


if __name__ == "__main__":
    main()
