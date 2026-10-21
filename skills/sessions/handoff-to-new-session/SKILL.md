---
name: handoff-to-new-session
description: Move this session's work into a fresh Claude Code session that starts with a self-contained brief — for when a session has run too long. Claude Code desktop app only (needs its start-session tool); in other agents use `handoff`. Works for any kind of session (code, research, planning, writing, a plain conversation). Use only when the user asks — "handoff to new session", "hand this off to a new session", "continue in a new session", "this session is too long, move it".
disable-model-invocation: true
---

# Handoff to new session

Start a new session (via `mcp__ccd_session__start_session`) that carries on exactly where this one is, without the user copying anything. The new session has none of this conversation, so the brief must stand alone.

If the user added notes or a focus with the request, weight the brief toward it.

## Principles

- **Fresh, not fork.** The point is to shed a long context, so use `context: "fresh"`. Everything the new session needs goes in `prompt` and `background`.
- **Describe the session as it is, not as a code task.** First work out what kind of work this was — code changes, an investigation, research, a document or card being drafted, a decision being reasoned through, a conversation — and write the brief around that. Code sections appear only when there is code.
- **Carry what can't be recovered.** The new session can re-read files, the repo, Jira, Confluence. It cannot recover what lived only in this chat: the user's decisions and their reasons, things ruled out and why, corrections the user gave, preferences stated, drafts not yet saved anywhere, numbers or facts found mid-session, who said what. These matter most.
- **Point, don't paste.** For anything that lives somewhere (file, branch, MR, card, page, artifact), give its path/link/key and what state it's in, not its contents. Unsaved drafts are the exception: save them to a file first and point to it.
- **State the next move plainly.** End with the immediate next action, and anything waiting on the user (a question asked but unanswered, an approval pending).
- **Nothing lost in transit.** Before starting the new session, make sure nothing exists only in memory of this one: write unsaved drafts to the scratchpad or the project; for code, see below.

## If the session has code changes

Check, skipping what doesn't apply:

```bash
pwd; git rev-parse --show-toplevel; git branch --show-current
git status --short; git diff --stat; git diff --cached --stat
git log --oneline -10 @{upstream}.. 2>/dev/null || git log --oneline -5
```

- In the brief: repo path, branch, what's committed / staged / uncommitted, unpushed commits, open MR/PR and its CI state, tests run and their result.
- The new session must see the same files. Plain checkout: `use_worktree: false` (it shares the folder, uncommitted work included). Worktree session: uncommitted edits don't travel to a new worktree, so either `use_worktree: false` (shares this worktree) or commit first — ask the user only if it's unclear which they want.
- Don't commit, push or stash unless the user says to.

## Brief shape

`background` (≥80 chars): the goal and why, the kind of session, key decisions and constraints so far.

`prompt`, in this order (drop any section that's empty):

```
<role>Continue … (one line: what you are picking up and what to do first)</role>
<context>What this work is, why, approach taken.</context>
<decisions>User decisions + reasons; options ruled out + why; corrections and preferences the user gave.</decisions>
<state>Done / in progress / blocked. For code: repo, branch, git state, MR, CI, tests.</state>
<where_things_are>Paths, links, keys, artifacts — each with its current state.</where_things_are>
<open>Unanswered questions, pending approvals, known risks.</open>
<next>Ordered next actions; first one is what to do immediately.</next>
<origin>Continued from session "<this session's title>".</origin>
```

## Start it

1. Save the brief to `~/.claude/handoffs/handoff-<folder-or-repo>-<shortname>.md` as a backup.
2. Call `start_session` with `initiation: "user_asked"`, `context: "fresh"`, a `title` naming the work (not "handoff"), `prompt`, `background`, and `use_worktree` per the code section (default `false` outside a worktree). Keep model and effort inherited.
3. Reply in one or two lines: link to the new session, where the backup is, and offer to archive this one (only archive on a yes).
