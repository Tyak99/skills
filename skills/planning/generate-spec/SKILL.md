---
name: generate-spec
description: Generate an implementation spec for a feature through focused dialogue and codebase inspection. Use when the user asks to spec a feature or epic, turn a PRD or ticket into an implementation plan, or break work into testable tasks. Accept tickets, documents, screenshots, URLs, plain text, or a mix.
---

# Generate Spec

Generate an implementation spec through Socratic dialogue. Keep asking questions until all ambiguity is resolved, then produce a structured spec document grounded in the *actual* codebase you're working in.

This skill is project-agnostic. It learns the project from what's in front of it — `CLAUDE.md`, `README`, existing code, recent commits — rather than assuming a stack, architecture, or workflow.

## Workflow

### Phase 1: Gather Context

Accept any combination of inputs — tickets, design docs, screenshots, URLs, plain text. Combine them; do not ask the user to re-describe what an attached screenshot, URL, or ticket already shows.

**Ticket (Jira)**: if a Jira connector or API is available, fetch the issue summary, description, acceptance criteria, comments, parent, and links. Follow any referenced Confluence PRD and check linked tickets or the parent epic for broader context.

**Ticket (Linear / GitHub Issues / other)**: use an available connector, API, or CLI; otherwise ask the user to paste the ticket content or share a URL.

**Confluence / Notion / URL**: fetch with an available connector or web tool. Follow obvious links one hop for context.

**Screenshots**: read them as part of the brief. Extract requirements, UI flows, data, and constraints from what's shown.

**Plain text**: work with what the user provided.

Then **learn the project from the codebase**. Do not assume any stack, framework, or convention.

- Read `CLAUDE.md` / `AGENTS.md` / `README.md` at the repo root (and in any sub-package you'll touch). These are the project's own briefing for AI agents — treat them as authoritative.
- Look at `package.json` / `pyproject.toml` / `go.mod` / `Gemfile` / `Cargo.toml` / `*.csproj` / `pom.xml` / equivalent — identify languages, frameworks, test runners, lint/format tools.
- Walk the top-level directory structure. Identify the architectural shape (monolith vs. multi-package, layered vs. feature-sliced, monorepo vs. single repo).
- Look for an `ARCHITECTURE.md`, `docs/`, `adr/`, or similar. Read what's relevant.
- Grep/Glob for precedent — how were similar features built here? Find at least one analogous existing feature and read the files it touches end-to-end.
- Note the project's own conventions: naming, file layout, test location, error handling style, logging, i18n, auth pipeline, dependency-injection pattern, ORM/query style, API shape, frontend rendering model. **Match what exists. Do not propose patterns that aren't already in the repo.**
- Check `git log --oneline -50` and recent PRs (if a remote is configured) for the team's current direction.

Present the brief back to the user before asking anything:

> "Here's what I understand needs to be built: [summary]. Here's the part of the codebase that's relevant: [files, modules, existing patterns I'll match]. Here's what `CLAUDE.md`/`README` says is relevant: [rules/constraints]. Here are the assumptions I'm making about scope: [list]. I'll start asking focused questions to fill the gaps."

### Phase 2: Resolve Ambiguity

Work through requirements systematically. For each requirement, ensure it has:
- **Trigger** — what causes this to happen
- **Action** — what the system does
- **Measurable outcome** — how to verify it worked
- **Error cases** — what happens when it fails

Ask focused questions using the agent's available question or chat interface, max 3–5 per round. Run the ambiguity checklist (`references/ambiguity-checklist.md`) on every requirement before accepting it.

Project-shaped ambiguity probes — adapt these to what you actually saw in Phase 1:

- **Which user / role / actor?** Name them in the project's own vocabulary. If the project has explicit roles, permissions, or feature flags, map every requirement to one.
- **Which scope of data?** Multi-tenant, per-org, per-user, per-environment? Confirm visibility/ownership rules.
- **Which subsystems are touched?** Frontend? API? DB? Background workers? Third-party integrations? Each touch point increases coordination cost — make it explicit.
- **Which lifecycle / state machine?** If the feature interacts with an entity that has explicit states (order, ticket, subscription, etc.), enumerate the transitions involved.
- **Auth / permissions?** Which roles can do this? Is there a permission row to add, a policy to update, a feature flag?
- **Telemetry / audit / logging?** Anything observable that the team relies on?
- **i18n / a11y?** If user-facing strings or controls are added, confirm what languages and accessibility constraints apply.
- **Async / real-time?** Background job, queue, websocket/SSE, polling — pick one.
- **Backwards compatibility?** Existing data, existing API consumers, existing URLs — what must keep working?
- **Performance / scale?** If a list, search, or aggregation is added, confirm volume + acceptable latency.
- **Rollout?** Big-bang, feature flag, percentage rollout, internal-only first.

**UI design agreement:** Identify whether the work changes a visible screen, control, state, or flow. If it does, ask whether the user has a design unless they already supplied one.

- With a supplied design, use it to resolve UI requirements and cite it in the spec. Confirm which parts the user considers agreed; a reference alone is not approval.
- For a small change without a design, invoke the installed `ui-change-preview` skill. If your agent supports subagents, prefer one to prepare the annotated current-screen images and return the files and evidence; present them to the user yourself and obtain the approval required by that skill. Otherwise run it directly. Resume the spec after the preview is agreed.
- For a new screen or substantial flow without a design, ask which design method the user wants. Use a suitable available design skill or tool if they choose one. If the method or design is still undecided, continue only as a draft and keep UI design unresolved; do not mark UI implementation ready.

Record the agreed design or preview, its scope, and any uncovered states in the spec. Design approval settles only the depicted UI, not the full spec or implementation.

**Keep asking until:**
- Every requirement has trigger + action + outcome.
- Every error case is handled explicitly.
- Every "it depends" is resolved to a concrete decision.
- Scope boundaries are clear (what's in, what's out).
- Domain rules surfaced from `CLAUDE.md` / `README` / existing code are explicitly respected or explicitly out-of-scope.
- Any UI design needed for implementation is agreed, or the spec remains a draft with the gap explicit.
- The user confirms there are no open questions.

Tell the user when you believe all ambiguity is resolved. Ask them to confirm before proceeding.

### Phase 3: Draft Technical Decisions

Present key technical decisions to the user for validation. The shape of this section follows the *architecture you discovered in Phase 1* — there is no fixed template.

For every subsystem the feature touches, decide:
- **What's added/changed** — files, modules, components, tables, columns, endpoints, jobs, events.
- **Public contract** — function signatures, API request/response, message shape, DB column types/constraints, event names.
- **Why this shape** — and what you rejected.
- **Where it fits in existing patterns** — name the precedent file/module you're matching.
- **Edge cases** — and how each is handled.
- **What's explicitly out of scope.**
- **Trade-offs** — simpler now vs more flexible later.

Ask the user about decisions requiring their judgement. Never make business decisions — those are the user's.

### Phase 4: Generate the Spec

Read the template at `references/spec-template.md` and produce the spec following its structure. The template's section headings are fixed; the table contents and any layered subsections adapt to the project.

**Where to write the spec:**
- Default to `docs/specs/[feature-name].md` at the repo root.
- If `docs/specs/` doesn't exist and there's a more conventional location for design docs in this repo (e.g. `docs/design/`, `architecture/`, an `adr/` folder, a Notion page the team prefers), confirm with the user before creating a new directory.
- For multi-repo workspaces where the spec is cross-cutting, write at the workspace root, not inside any sub-repo.

Six sections (mirroring the template):

**Section 1: Technical Decisions** — Confirmed requirements (trigger/action/outcome, source link), context mapping (entities/modules/subsystems), architecture choices with rationale (per subsystem touched), data model changes (only if applicable), permissions/roles (only if applicable), edge cases, out of scope, open questions (MUST be empty by approval).

For UI work, fill the template's UI design reference and status with the approved design or concept preview. Keep unresolved design choices in Open Questions while the spec is a draft.

**Section 2: Acceptance Criteria** — Grouped by role/persona that actually applies (do not invent personas). Each criterion testable, all `[ ]` unchecked.

**Section 3: Task Queue — grouped by subsystem.** Overview table with dependencies. Group tasks by the natural boundaries in this repo (e.g. DB → API → Web, or domain → adapter → UI, or backend → frontend, or per-package). Inside each group, tasks are dependency-ordered. Cross-group dependencies are explicit. Each task has: purpose, what to build (plain language, no code), per-task acceptance criteria, notes. Each sized for one AI coding session.

**Section 4: QA Validation Plan** — How to verify the feature end-to-end. Tailor:
- **UI changes** → manual browser/app verification steps (navigate to X, click Y, expect Z).
- **API-only changes** → automated tests in the project's test runner + a reproducible manual call (curl / Postman / HTTPie / equivalent).
- **DB-only changes** → migration up/down validation + query checks.
- **Background jobs / events** → how to trigger, how to confirm completion, how to inspect the dead-letter path.
- **Mixed** → all that apply.
Each QA item should be a concrete, reproducible step — not a restatement of acceptance criteria.

**Section 5: Risks & Deployment Notes** — Project-specific risks: migration safety, backfill, feature-flag wiring, rollout order, rollback path, observability (metrics/log lines/alerts to watch), security review needs, performance concerns at scale. Only include rows that actually apply.

**Section 6: Complexity** — Always the last section. See Phase 5.

### Phase 5: Score Spec Complexity

Complexity is expressed on a scope-based scale: **Trivial / S / M / L / XL**. This scores the spec's intrinsic complexity — scope, surface area, dependencies, integration count, data complexity — **not** the time it will take to implement. With AI in the loop, effort and delivery time are decoupled; effort-based sizing (story points, sprints, days) is no longer used.

| Score   | Scope anchor                                                                                                  |
|---------|---------------------------------------------------------------------------------------------------------------|
| Trivial | Zero new surface. Config flag, copy tweak, single-line fix.                                                   |
| S       | Single small change in one subsystem / one file / one column. No new domain object.                          |
| M       | Moderate scope. Multiple files in one subsystem, or one new domain object, or one new endpoint over an existing module. |
| L       | Multiple subsystems touched, one new domain object, real integration work.                                   |
| XL      | Cross-cutting: many new objects, many integration points, or changes to core domain rules / state machines. Usually must be split before intake. |

**How to derive:**
- Inspect the task queue: how many subsystems, how many new domain objects, how many integration surfaces, how much novelty (new patterns vs. reusing existing).
- Factor in unresolved ambiguity surfaced during Phase 2 — a spec with deferred questions trends one bucket higher.
- Pick the bucket that matches the spec's **scope**, not how long it'll take to build.

**Confirm with the user:**
1. State the score and the reasoning in one or two sentences, focused on **scope**.
2. Ask them to confirm or change it. Accept any value they pick.
3. Update the spec's Complexity section with the final agreed value.

**If the agreed score is XL:** tell the user the ticket likely needs to be split before intake. Suggest candidate split points from the task queue (by subsystem boundary, by persona, by acceptance-criteria cluster). Do not proceed to Phase 7 (ticket sync) with an XL spec.

### Phase 6: Review with User

Present the completed spec and ask:
1. "Any requirements missing or incorrect?"
2. "Is the context mapping accurate? Any project rule I've missed?"
3. "Are task sizes right — any too big or too small?"
4. "Are cross-group dependencies correct — can tasks be parallelised more?"
5. "Any technical decisions you disagree with?"

Revise based on feedback. Spec is not done until the user approves.

At end of review, if any new durable project knowledge was created during the dialogue (new business rule, clarified edge case, architectural decision worth remembering), draft a **"Suggested `CLAUDE.md` / docs update"** block for the user — do not modify those files yourself; wait for confirmation.

### Phase 7: Sync Back to the Ticket (Optional)

**Only applies when the input included a ticket.** After the spec file is written and the user has approved it:

1. Ask: "The spec is ready. Would you like me to post the full spec to [TICKET-ID] as a comment?"
2. **Do not post without explicit user approval.** Wait for a clear yes.
3. If approved, use an available connector, API, or CLI to comment the **full spec content** — all six sections — on the ticket.
4. Do not sync an XL spec — Phase 5 requires the ticket be split first.

If the input wasn't a ticket, ask whether the user wants to attach the spec to one and, if so, request the ID.

## Rules

- **Never assume business logic.** If the source is ambiguous, ask. Don't invent policies.
- **Never skip the question phase.** Ambiguity resolved here, not during implementation.
- **Stay at "what" not "how".** Describe fields, types, constraints, procedures, endpoints, behaviours in plain language. **No code snippets in the spec** — code biases the implementing agent toward a shape that may not fit once it reads the codebase. The implementing agent figures out the code.
- **Ground decisions in *this* codebase.** Match existing conventions, name the precedent files you're matching. Don't propose patterns that don't exist here. Don't import opinions from other projects.
- **Respect documented project rules.** If `CLAUDE.md` / `README` / `ARCHITECTURE.md` set a rule, the spec respects it or explicitly justifies the exception.
- **Group the task queue by the project's natural subsystem boundaries** and make cross-group dependencies explicit.
- **Respect the user's time.** Ask smart, focused questions. 5 well-chosen > 20 scattered.
- **Accept all input types.** Screenshots, ticket links, design-doc pages, plain text — combine them. Don't ask the user to re-describe what a screenshot or ticket already shows.
