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

### UI

For UI changes without a design file: approve the change on the real screen before it's built, and get proof on the real screen after.

| Skill | What it does |
|---|---|
| [`ui-change-preview`](skills/ui/ui-change-preview/SKILL.md) | Before writing code, screenshots the current UI and marks exactly what will change ("New button will appear here"), labelled *Concept preview — not implemented*. Stops until you approve or revise. |
| [`ui-proof-walkthrough`](skills/ui/ui-proof-walkthrough/SKILL.md) | After the work is done, turns fresh screenshots of the running app into a short annotated walkthrough of what changed. Screenshots are never redrawn, so it's evidence, not a mockup. |

## Requirements

- `recall` needs Python 3 (standard library only).
- `handoff` needs `git` for repo context; it works outside a repo too.
- The UI skills need an agent that can drive a browser and take screenshots (a built-in browser, Playwright, or similar) and show images in chat.

## License

[MIT](LICENSE)
