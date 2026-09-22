---
name: recall
description: Recover context from past coding-agent sessions (Claude Code, Codex) before answering. Use when a request leans on history the current conversation doesn't contain — the user pastes a message, error, code, or link and says "help me with this"; names a ticket key, person, repo, skill, or product with no explanation; or refers to "the thing we built", "what we decided", "the skill I made", "why did we do it this way". Also triggered by explicit asks like "find context on this", "search my old sessions", "what did we do about X", "gather context first". Searches the local session history of every supported agent (ranked, current project first) and returns a context brief rather than raw transcripts.
---

# Recall

Reconstruct what the user already knows — and already decided — from past agent sessions, so they don't have to re-explain it.

Coding agents keep every session on disk as `.jsonl` transcripts. The store is large (hundreds of MB to GBs) and mostly noise. The job is to extract the handful of facts that make the current request make sense, then answer the request.

| Agent | Sessions | Memory |
|---|---|---|
| Claude Code | `~/.claude/projects/<encoded-cwd>/*.jsonl` | `~/.claude/projects/<encoded-cwd>/memory/MEMORY.md` |
| Codex | `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`, `~/.codex/archived_sessions/` | `~/.codex/memories/MEMORY.md` |

The scripts search every store that exists on the machine, whichever agent is running them — work on one project often spans several agents. Everything stays local; nothing is uploaded anywhere.

## The one hard rule

**Never read a raw `.jsonl` transcript directly** (no `cat`, `head`, `tail`, or whole-file reads). Single sessions reach several MB and will blow the context window. Use `scripts/read_session.py`, which converts a transcript to readable excerpts (a 948KB session becomes ~1.7KB when filtered). Grepping a `.jsonl` for matches is fine — matches only, never with a large surrounding window.

## Workflow

`<skill>` below is this skill's directory. The scripts need only Python 3.

### Phase 1 — Derive search terms

Pull concrete, greppable identifiers from the request and any attached code or pasted text:

- Ticket keys (`PROJ-123`), PR/issue numbers, repo names, branch names
- People (first names as written — `Alice`, `Sam`)
- Skill/plugin/product names, file paths, function or symbol names, error strings
- Distinctive domain nouns (`billing-v2`, `onboarding-funnel`, `rate-limiter`)

Prefer 2–5 **specific** terms. Generic words (`test`, `api`, `fix`) match everything and rank nothing. If the request has no greppable nouns at all, say so and ask for one rather than guessing.

### Phase 2 — Read memory first

Before searching transcripts, read whatever memory the agents keep (see the table above), plus the project's `AGENTS.md` / `CLAUDE.md`. Memory is the already-distilled version of exactly this history — read the index, then only the entries whose description matches.

Claude Code's encoded cwd = the working directory with `/`, `.`, and `_` replaced by `-` (`/Users/x/Code/app` → `-Users-x-Code-app`).

Memory often answers the question outright. When it does, skip to Phase 5 and note that transcripts weren't needed. Memory reflects when it was written — treat it as a lead, not a guarantee.

### Phase 3 — Rank candidate sessions

```bash
python3 <skill>/scripts/find_sessions.py TERM [TERM ...] [--days N] [--limit N]
```

Prints a ranked table — timestamp, hit count, how many distinct terms matched, size, which agent, project, path, and each session's topic (its first real user prompt). Sessions matching **all** terms rank above sessions matching one many times; the current project ranks above others. A multi-GB store scans in a few seconds.

Useful flags: `--agent claude|codex` to search one agent's store, `--this-project-only` to suppress cross-project noise, `--days N` to bound recency, `--cwd PATH` when reasoning about a different project than the shell's.

Judge candidates by their **topic line**, not their hit count. A session whose topic is the thing being asked about beats one that mentions the term in passing 200 times. The session you are in right now will often rank first — it contains the terms you just typed. Skip it.

### Phase 4 — Read the top candidates

Pick the 2–5 best. For each:

```bash
python3 <skill>/scripts/read_session.py SESSION.jsonl --terms TERM [TERM ...] [--window 2]
```

The format (Claude Code or Codex) is detected automatically. `--window N` includes N turns either side of each match. Widen to 4–5 when excerpts read as fragments; add `--full` only for a small session whose whole arc matters.

**If your agent can delegate to subagents, do so when there is more than one session to read, or when a session is over ~1MB.** Transcript excerpts are bulky and mostly irrelevant to the final answer — the main thread should receive findings, not raw material. Give the subagent the terms, the paths, the questions to answer, and instruct it to use `read_session.py`. Ask for findings with short quotes, not summaries of everything. Without subagents, keep `--window` small and read one session at a time.

Good questions to answer from each session: What is this thing? What was decided, and why? What was explicitly rejected? What was left unfinished or blocked? Who else is involved?

### Phase 5 — Brief, then answer

Produce a short context brief before acting on the request:

- **What this is** — one or two lines, enough that the request now parses
- **Decisions already made** — including ones deliberately rejected, so they aren't re-proposed
- **Open threads** — what was unfinished, blocked, or waiting on someone
- **What I couldn't find** — gaps, stated plainly

Then answer the actual request. The brief is scaffolding for a good answer, not the deliverable.

Two accuracy rules:

- **Transcripts record what was true then.** Before acting on a load-bearing detail — a file path, a branch, a decision that may have been reversed — check the live source (`git`, the ticket, the file). Say which claims are verified and which are just what the transcript said.
- **Never invent continuity.** If the history doesn't cover something, say so. A confident wrong reconstruction is worse than asking.

### Phase 6 — Offer to save what was expensive to find

If the search surfaced a durable fact not already in memory — an offline decision, a constraint, a "we chose X over Y because Z" — offer to save it wherever the current agent keeps memory, so the next session doesn't repeat this search. Offer; don't write unprompted. Skip facts the repo or git history already records.

## Notes

- Sibling projects matter: work on one product is often split across several directories (`app`, `app-api`, `app-web`) and several agents. The default everything-search is deliberate.
- Claude Code keeps subagent transcripts in `<session-id>/subagents/*.jsonl` and spooled tool output in `tool-results/`. `find_sessions.py` skips both; reach for them only when a finding clearly came from delegated work.
- Sessions are append-only, so a long-running session's modified time reflects its last turn, not its topic's age.
- Another agent's store? Add a `Store` subclass in `scripts/stores.py` — where its files live, which project a session belongs to, and how to flatten one line into a turn.
