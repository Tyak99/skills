---
name: handoff
description: Write a self-contained handoff prompt so another agent (Claude Code, Codex, or a teammate's) can pick up this session's work with zero prior context. Use only when the user asks for a handoff — "handoff", "hand this off", "write a handoff", "prep this for another agent", "I'm switching to Codex/Claude".
disable-model-invocation: true
---

# Handoff

Generate a prompt for handing off work to another AI agent. The receiving agent has no context from this session, so the prompt must be self-contained and actionable. It supports any follow-up: continuation, investigation, review, or exploration.

If the user added notes or a focus area with the request, weight the handoff toward it.

## 1. Gather git context

Run these from the working directory (skip what fails — not every session is in a repo):

```bash
pwd
git rev-parse --show-toplevel | xargs basename   # repo name
git branch --show-current                         # branch
git status --short
git diff --stat                                   # unstaged
git diff --cached --stat                          # staged
git log --oneline -5 --since="4 hours ago"        # this session's commits
```

## 2. Review the session

From this conversation, work out:

- What task was requested and why
- What approach was taken
- Decisions made or tradeoffs discussed
- Current state: what's done, in progress, or blocked
- Open questions or areas of uncertainty
- Known issues or incomplete items

## 3. Write the handoff

### Prompting guidelines

- **Be explicit and detailed** — include context on *why*, not just *what*
- **Use action-oriented language** — direct instructions like "Continue implementing..." not "Can you look at..."
- **Frame positively** — say what to do rather than what to avoid
- **Use XML tags** for clear section delimitation
- **Stand alone** — no "as discussed" or "the earlier approach"; spell it out

### Role

Pick the framing that makes the strongest, most actionable prompt:

- Work needs **review** → reviewer ("You are a senior engineer reviewing...")
- Work needs **continuation** → implementer ("You are picking up implementation of...")
- An **issue to investigate** → debugger ("You are investigating...")
- **Nothing specific** → teammate ("You are picking up work from a teammate...")

### Structure

```
<role>
[Your chosen framing — be specific about what the agent should do]
</role>

<context>
[2-4 sentences: what was being worked on, why, approach taken, key decisions made]
</context>

<current_state>
[What's done, what's in progress, what's blocked or uncertain]
</current_state>

<key_files>
[Files involved with brief descriptions of changes/relevance]
</key_files>

<next_steps>
[Action-oriented tasks for the receiving agent. Be specific. Examples:
- "Continue implementing the X feature by adding Y to Z file"
- "Review changes in A, B, C focusing on error handling"
- "Investigate why the build fails when running X command"]
</next_steps>
```

## 4. Save and copy

1. Write it to `~/.agents/handoffs/handoff-<repo>-<shortname>.md` (create the directory if needed), where `<repo>` is the repository basename (or the working directory's basename outside a repo) and `<shortname>` comes from the branch name — e.g. `handoff-myapp-sen-69.md`, `handoff-api-fix-auth.md`.
2. Copy it to the clipboard with whichever exists: `pbcopy` (macOS), `wl-copy` or `xclip -selection clipboard` (Linux), `clip.exe` (Windows/WSL). If none does, skip this step and say so.
3. Confirm in one line: "Handoff saved to `<path>` and copied to clipboard."
