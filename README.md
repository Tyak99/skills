# Skills

Agent skills I use every day, straight from my own setup. They follow the open [Agent Skills](https://agentskills.io) standard, so they work in Claude Code, Codex, Cursor and any other agent that reads `SKILL.md`.

Small, readable, and meant to be adapted. Take what's useful.

## Install

**Any agent** (Codex, Cursor, Claude Code, …) — copies editable skill files you own:

```bash
npx skills@latest add Tyak99/skills
```

Pick the skills you want and which agents to install them for. Update later with `npx skills update`.

**Claude Code plugin** — a managed, read-only bundle that updates when I ship:

```
/plugin marketplace add Tyak99/skills
/plugin install tyak99-skills@tyak99
```

Pick one route. Installing both gives you every skill twice.

**By hand** — copy a skill folder into `~/.claude/skills/` (Claude Code) or `~/.agents/skills/` (Codex and others).

## Skills

### Sessions

Keeping context alive across sessions and across agents.

| Skill | What it does |
|---|---|
| [`recall`](skills/sessions/recall/SKILL.md) | Before answering, searches your past Claude Code and Codex sessions for the ticket, person or thing you just mentioned, and returns a short brief: what it is, what was already decided (and rejected), what's still open, and what it couldn't find. Runs locally; nothing leaves your machine. |
| [`handoff`](skills/sessions/handoff/SKILL.md) | Writes a self-contained prompt so another agent — or you, tomorrow, in a different tool — can pick up exactly where this session left off. Saved to `~/.agents/handoffs/` and copied to your clipboard. Run it explicitly: `/handoff`. |
| [`handoff-to-new-session`](skills/sessions/handoff-to-new-session/SKILL.md) | When a session has run too long, starts a fresh one that picks up where it left off, with nothing to copy. Its brief carries what only lived in the chat (decisions and why, things ruled out, unsaved drafts, the next move), is backed up to `~/.claude/handoffs/`, and opens as a new session. Claude Code desktop app only. Run it explicitly: `/handoff-to-new-session`. |

### UI

For UI changes without a design file: approve the change on the real screen before it's built, and get proof on the real screen after.

| Skill | What it does |
|---|---|
| [`ui-change-preview`](skills/ui/ui-change-preview/SKILL.md) | Before writing code, screenshots the current UI and marks exactly what will change ("New button will appear here"), labelled *Concept preview — not implemented*. Stops until you approve or revise. |
| [`ui-proof-walkthrough`](skills/ui/ui-proof-walkthrough/SKILL.md) | After the work is done, turns fresh screenshots of the running app into a short annotated walkthrough of what changed. Screenshots are never redrawn, so it's evidence, not a mockup. |

### Review

Reviewing changes you didn't write line by line, usually AI-written ones.

| Skill | What it does |
|---|---|
| [`pr-decisions`](skills/review/pr-decisions/SKILL.md) | Point it at a PR, MR, branch or diff. It lists the decisions the change makes without saying so: timeouts, budgets, caps, retries, defaults, what it skips, how it fails and what it trusts. Each one shows the value, where it's set, the reason given (or **not recorded**) and what breaks if it's wrong. Also flags values that must change together. It isn't a bug review; it's what you'd need to explain after the change ships. |

### Planning

Turn a feature idea or ticket into work an implementing agent can pick up.

| Skill | What it does |
|---|---|
| [`generate-spec`](skills/planning/generate-spec/SKILL.md) | Reads the source material and relevant code, agrees on UI design when needed, then writes an implementation spec with technical decisions, acceptance criteria, a dependency-ordered task queue, a QA plan, risks, and scope-based complexity. Requires your approval before posting the spec to a ticket. |

## Requirements

- `recall` and `pr-decisions` need Python 3 (standard library only). `pr-decisions` also needs `git`, plus `gh` or `glab` if you want it to read PR descriptions and discussion.
- `handoff` needs `git` for repo context; it works outside a repo too.
- `handoff-to-new-session` needs the Claude Code desktop app, which provides the tool that starts a new session.
- The UI skills need an agent that can drive a browser and take screenshots (a built-in browser, Playwright, or similar) and show images in chat.

## License

[MIT](LICENSE)
