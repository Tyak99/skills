# Working on this repo

A collection of [Agent Skills](https://agentskills.io), published for any agent and also as a Claude Code plugin.

## Layout

- `skills/<group>/<skill>/SKILL.md`: one folder per skill, grouped by theme (`sessions/`, …). Supporting files (scripts, references) live beside the `SKILL.md`.
- `skills/<group>/<skill>/agents/openai.yaml`: optional Codex display metadata and invocation policy.
- `.claude-plugin/plugin.json`: the Claude Code plugin. Its `skills` array lists shipped skills explicitly.
- `.claude-plugin/marketplace.json`: makes this repo its own single-plugin marketplace.

## Rules

- **Every shipped skill is listed in `.claude-plugin/plugin.json` → `skills`** and in the README table. A skill folder that isn't listed doesn't ship to plugin users.
- **Write for any agent.** Say "if your agent supports subagents" rather than naming one agent's tools. When a skill is inherently tied to one agent, say so in its description and the README.
- **Frontmatter:** `name` (matches the folder) and `description` (what it does + when to trigger). Add `disable-model-invocation: true` plus `policy.allow_implicit_invocation: false` in `agents/openai.yaml` for skills that should only run when the user asks.
- **Scripts:** Python 3 standard library only, no install step.
- **Nothing private.** No client names, ticket keys, colleagues' names or internal URLs in examples — use `PROJ-123`, `Alice`, `billing-v2`.
- **Releases:** bump `version` in `.claude-plugin/plugin.json` when shipping changes; plugin users only update when it changes.
- Validate before pushing: `claude plugin validate .` and `claude plugin validate .claude-plugin/plugin.json`. The one expected warning is about `CLAUDE.md` at the root. It points Claude Code at this file for contributors and isn't meant as plugin context.
- Check the any-agent route still discovers every skill: `npx skills@latest add . --list`.
