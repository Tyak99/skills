"""Where coding agents keep their session transcripts, and how to read each format.

Each store knows three things: where its .jsonl files live, which project a session
belongs to, and how to turn one line of its format into a (role, text) turn.

Supported today:
  claude  Claude Code  ~/.claude/projects/<encoded-cwd>/<session>.jsonl   ($CLAUDE_CONFIG_DIR)
  codex   Codex        ~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl        ($CODEX_HOME)
                       ~/.codex/archived_sessions/rollout-*.jsonl

Adding an agent means adding one Store subclass and registering it in STORES.
"""
import json
import os
import re
from pathlib import Path

# Prompts that carry no topic signal -- injected context, not something the user typed.
NOISE = re.compile(
    r"^\s*(<local-command|<system-reminder|<environment_context|<user_instructions|"
    r"<permissions|<recommended_plugins|# AGENTS\.md|caveat:|\[request interrupted)",
    re.I,
)
CMD_NAME = re.compile(r"<command-name>([^<]*)</command-name>")
CMD_ARGS = re.compile(r"<command-args>([^<]*)</command-args>")


def encode_cwd(path: str) -> str:
    """Normalise a working directory into a comparable project key (Claude's dir naming)."""
    return path.replace("/", "-").replace(".", "-").replace("_", "-")


def clean_prompt(text):
    """Return a topic string, or '' if this prompt carries no signal.

    A slash command with arguments is a real topic ('/review-pr <url> ...'); a bare
    '/model' or '/clear' is not, so keep scanning for the next prompt.
    """
    text = " ".join(text.split())
    if not text or NOISE.match(text):
        return ""
    if "<command-name>" in text:
        name = (CMD_NAME.search(text) or [None, ""])[1].strip()
        args = (CMD_ARGS.search(text) or [None, ""])[1].strip()
        return f"{name} {args}".strip() if args else ""
    return text


def _blocks_text(content, kinds=("text", "input_text", "output_text")):
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    return " ".join(
        b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") in kinds
    )


def _read_lines(path, max_bytes):
    try:
        with open(path, "r", errors="replace") as fh:
            return fh.read(max_bytes).splitlines()
    except OSError:
        return []


class Store:
    name = ""
    label = ""

    def roots(self):
        """Directories holding this agent's session files."""
        return []

    def available(self):
        return any(r.is_dir() for r in self.roots())

    def skip(self, path: str) -> bool:
        return False

    def project_key(self, path: Path) -> str:
        """Encoded cwd of the session, comparable with encode_cwd(os.getcwd())."""
        raise NotImplementedError

    def topic(self, path: Path) -> str:
        """The session's first substantive user prompt."""
        raise NotImplementedError

    def turn(self, d: dict):
        """Flatten one parsed .jsonl line into (role, text), or None if it isn't conversation."""
        raise NotImplementedError


class ClaudeStore(Store):
    name = "claude"
    label = "Claude Code"

    def roots(self):
        base = Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude"))
        return [base / "projects"]

    def skip(self, path):
        # Subagent transcripts and spooled tool output, not sessions of their own.
        return "/subagents/" in path or "/tool-results/" in path

    def project_key(self, path):
        return path.parent.name if path.parent.parent.name == "projects" else path.parent.parent.name

    def topic(self, path):
        for line in _read_lines(path, 400_000):
            if '"type":"user"' not in line.replace(" ", ""):
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if d.get("type") != "user":
                continue
            text = clean_prompt(_blocks_text(d.get("message", {}).get("content")))
            if text:
                return text[:180]
        return ""

    def turn(self, d):
        if d.get("type") not in ("user", "assistant"):
            return None
        content = d.get("message", {}).get("content")
        if isinstance(content, str):
            return d["type"], content
        if not isinstance(content, list):
            return None
        parts = []
        for b in content:
            if not isinstance(b, dict):
                continue
            kind = b.get("type")
            if kind == "text":
                parts.append(b.get("text", ""))
            elif kind == "thinking":
                parts.append("[thinking] " + b.get("thinking", "")[:400])
            elif kind == "tool_use":
                parts.append(f"[tool: {b.get('name')} {json.dumps(b.get('input', {}))[:200]}]")
            elif kind == "tool_result":
                parts.append(f"[result: {_blocks_text(b.get('content'))[:300]}]")
        return d["type"], "\n".join(p for p in parts if p)


class CodexStore(Store):
    name = "codex"
    label = "Codex"

    def roots(self):
        base = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
        return [base / "sessions", base / "archived_sessions"]

    def _meta(self, path):
        # The first line is session_meta, which carries the cwd.
        for line in _read_lines(path, 2_000_000)[:5]:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if d.get("type") == "session_meta":
                return d.get("payload", {})
        return {}

    def project_key(self, path):
        cwd = self._meta(path).get("cwd")
        return encode_cwd(cwd) if cwd else "(unknown cwd)"

    def topic(self, path):
        for line in _read_lines(path, 1_000_000):
            if '"role":"user"' not in line.replace(" ", ""):
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            p = d.get("payload", {})
            if d.get("type") != "response_item" or p.get("role") != "user":
                continue
            text = clean_prompt(_blocks_text(p.get("content")))
            if text:
                return text[:180]
        return ""

    def turn(self, d):
        # response_item lines are the conversation; event_msg lines duplicate them.
        if d.get("type") != "response_item":
            return None
        p = d.get("payload", {})
        kind = p.get("type")
        if kind == "message" and p.get("role") in ("user", "assistant"):
            return p["role"], _blocks_text(p.get("content"))
        if kind == "reasoning":
            summary = _blocks_text(p.get("summary"), kinds=("summary_text",))
            return ("assistant", "[thinking] " + summary[:400]) if summary else None
        if kind in ("function_call", "custom_tool_call"):
            args = p.get("arguments") or p.get("input") or ""
            return "assistant", f"[tool: {p.get('name')} {str(args)[:200]}]"
        if kind in ("function_call_output", "custom_tool_call_output"):
            return "user", f"[result: {str(p.get('output', ''))[:300]}]"
        return None


STORES = {s.name: s for s in (ClaudeStore(), CodexStore())}


def store_for(path) -> Store:
    """Pick the store a session file belongs to, by location, then by content."""
    resolved = str(Path(path).resolve())
    for store in STORES.values():
        for root in store.roots():
            if resolved.startswith(str(root.resolve()) + os.sep):
                return store
    head = "".join(_read_lines(path, 20_000)[:3])
    return STORES["codex"] if '"session_meta"' in head else STORES["claude"]
