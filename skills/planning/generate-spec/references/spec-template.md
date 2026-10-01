# [Feature Name] — Implementation Spec

> **Source:** [link to PRD / design doc]
> **Ticket:** [PROJECT-xxxx]
> **Status:** Draft | In Review | Approved | In Progress | Complete
> **Last Updated:** YYYY-MM-DD
> **Subsystems Touched:** [list the parts of the codebase touched, e.g. backend, frontend, db, workers]
> **UI Design:** [No UI change | Agreed design/preview link and scope | Unresolved — draft only]

---

## 1. Technical Decisions

Everything the implementing agent needs to know that isn't obvious from the codebase. Each decision is settled — zero open questions remain by the time this spec is approved.

### 1.1 Context Mapping

Map the feature to the project's domain. Use *this project's* vocabulary — entities, modules, services as they're already named in the code.

| Entity / Module / Service | Role in this feature | Project rule / doc that applies |
|---|---|---|
| e.g. `Order` | Read + status transition (`PAID` → `SHIPPED`) | `docs/order-lifecycle.md` — transitions must go through `OrderService.transition()` |

### 1.2 Confirmed Requirements

Disambiguated requirements from the source material. Each one follows the pattern: **trigger → action → outcome**, with no vague language.

> Write each requirement so that a test can be written directly from it.
> Bad: "The system should handle order shipment gracefully"
> Good: "When an authenticated `fulfilment_operator` clicks 'Mark shipped' on an order in status `PAID`, the system shall transition `Order.status` to `SHIPPED` via `OrderService.transition()`, write an audit row, and emit an `order.shipped` event; if the order's `shipping_address` is null, return HTTP 422 with code `MISSING_ADDRESS` and no state change."

| ID | Requirement | Source |
|----|-------------|--------|
| R1 | When [trigger], the system shall [action] with [measurable outcome] | doc / ticket ref |
| R2 | While [state], the system shall [action] | doc / ticket ref |
| R3 | If [error condition], then the system shall [recovery action] | doc / ticket ref |

### 1.3 Architecture Choices (per subsystem)

Decisions about *how* to build it, grouped by the subsystems this feature touches. Replicate this block for each subsystem (backend / frontend / db / workers / mobile / etc.). Each row: what was decided, why, what was rejected.

#### [Subsystem 1 — e.g. Backend / `services/api/`]

| Decision | Choice | Rationale | Rejected Alternative |
|----------|--------|-----------|---------------------|
| Module placement | New module under `src/orders/shipment/` | Matches existing per-feature module layout | Reusing `src/orders/` (would mix concerns with payment) |
| Public contract | New service method `OrderService.markShipped(orderId, actor)` | Follows existing service-method shape | Direct repository update (skips lifecycle guard) |

#### [Subsystem 2 — e.g. Frontend / `apps/web/`]

| Decision | Choice | Rationale | Rejected Alternative |
|----------|--------|-----------|---------------------|
| Component placement | `apps/web/src/features/orders/ShipmentAction.tsx` | Matches feature-sliced structure | Page-level component (not reusable) |
| State | Local mutation via existing `useOrderMutation` hook | Reuses existing query-cache invalidation | New global store slice (unnecessary) |

#### [Subsystem 3 — e.g. Database / migrations]

| Decision | Choice | Rationale | Rejected Alternative |
|----------|--------|-----------|---------------------|
| Migration | New columns on `orders`, no new table | Feature sits on existing entity | New sidecar table (extra join, no benefit) |

### 1.4 Data Model Changes

Only fill if persistent storage is touched.

| Object | Change | Fields / Details | Notes |
|---|---|---|---|
| `orders` | ALTER TABLE ADD COLUMN | `shipped_at TIMESTAMP NULL`, `shipped_by_user_id INT NULL FK -> users(id)` | Backfill not required; null = not shipped |
| (sequence/index/etc.) | … | … | … |

### 1.5 Permissions & Roles

Only fill if access control changes.

| Role / Persona | Permission / Feature flag | Access decision | New permission row / config? |
|---|---|---|---|
| Fulfilment operator | `orders.mark_shipped` | Full | Yes — add to seed + admin UI |
| Customer | — | No access | — |

### 1.6 Edge Cases & Error Handling

Every edge case the implementing agent might encounter. If it's not listed here, it's not in scope.

| Case | Expected Behavior |
|------|-------------------|
| Order already in target status | Return HTTP 409, toast "Already shipped", no state change |
| Missing shipping address | Return HTTP 422 with code `MISSING_ADDRESS`, no state change |
| Actor lacks `orders.mark_shipped` | Return HTTP 403, audit denied attempt |
| Concurrent mark-shipped requests | First wins; second sees 409 |

### 1.7 Out of Scope

Explicitly state what is NOT being built. Prevents the implementing agent from over-building.

- [ ] e.g. Bulk-ship (multi-select) — deferred to next ticket
- [ ] e.g. Email notification on ship — needs product decision
- [ ] e.g. Carrier integration — separate epic

### 1.8 Open Questions (Must be zero before execution)

| Question | Status | Resolution |
|----------|--------|------------|
| e.g. Does marking shipped close child line items? | Resolved | No — line-item state is independent |

---

## 2. Acceptance Criteria

What "done" looks like, grouped by role/persona that actually applies. Each criterion is a testable statement. Updated with `[x]`/`[ ]`/`[~]` during implementation.

### Persona: [e.g. Fulfilment Operator]

- [ ] Can see the new action on orders in status `PAID`
- [ ] Cannot see the action on orders in other statuses
- [ ] On click, sees a success toast and the row updates in place

### Persona: [e.g. Customer]

- [ ] Receives an in-app notification within 2 s of the action

### Persona: [e.g. Administrator]

- [ ] Can grant / revoke the new permission via the role admin UI

### Persona: System

- [ ] Audit row written for every status change
- [ ] `order.shipped` event emitted exactly once per successful action

---

## 3. Task Queue — Grouped by Subsystem

Dependency-ordered list, grouped by the natural subsystem boundaries in this project. Inside each group, tasks are dependency-ordered. Cross-group dependencies are explicit. Each task is sized so one AI coding session can complete it.

### Task Overview

| ID | Group | Task | Blocked By | Priority | Status |
|----|-------|------|------------|----------|--------|
| D1 | DB    | Add columns to `orders` + migration | — | CRITICAL | TODO |
| B1 | Backend | Implement `OrderService.markShipped` + lifecycle guard | D1 | CRITICAL | TODO |
| B2 | Backend | Expose endpoint `POST /orders/:id/ship` | B1 | HIGH | TODO |
| B3 | Backend | Emit `order.shipped` event | B1 | HIGH | TODO |
| B4 | Backend | Tests (unit + integration) | B1, B2 | HIGH | TODO |
| F1 | Frontend | `ShipmentAction` component + mutation wiring | B2 | HIGH | TODO |
| F2 | Frontend | Surface action on the order detail page | F1 | MEDIUM | TODO |
| F3 | Frontend | Tests (component + e2e happy path) | F1 | MEDIUM | TODO |
| P1 | Permissions | Add `orders.mark_shipped` to seed + role admin UI | B2 | MEDIUM | TODO |

### D1: [Task Name]

**Purpose:** One line on why this task exists and what it enables.

**What to build:** Describe in plain language what needs to exist after this task — new/changed tables, columns (types, nullability, defaults, FKs), indexes, migrations. Precise field names, types, constraints — but do NOT include SQL snippets. The implementing agent writes the migration.

**Acceptance Criteria:**
- [ ] Migration applies cleanly forward
- [ ] Migration applies cleanly in rollback (or has an explicit no-down-migration note)
- [ ] New columns have the stated types/nullability/defaults

**Notes:** Migration must follow the project's existing migration naming convention.

---

### B1: [Task Name]

**Purpose:** …

**What to build:** New service method(s), including signature (params + return shape) and the lifecycle/business rules enforced. Cite the existing service it sits next to.

**Acceptance Criteria:**
- [ ] Method exists with the stated signature
- [ ] Business rules from §1.6 enforced
- [ ] Existing patterns matched (transactionality, error types, logging)

**Notes:** Reuses the project's existing `…` pattern — do not invent a new one.

---

### B2: [Task Name]

**Purpose:** Expose the service to clients.

**What to build:** New endpoint — HTTP method, route, request body shape, response shape, status codes (200 / 400 / 401 / 403 / 404 / 409 / 422 / 500), required headers/auth. Cite the analogous existing endpoint.

**Acceptance Criteria:**
- [ ] Endpoint reachable and returns contracted shape on happy path
- [ ] Error paths from §1.6 return the correct HTTP codes
- [ ] OpenAPI / route doc updated if the project maintains one

---

### B3: [Task Name]

**Purpose:** …

**What to build:** Event name, payload shape, where it's emitted from, which queue/topic/bus it lands on.

**Acceptance Criteria:**
- [ ] Event emitted exactly once per successful state transition
- [ ] Payload matches stated shape
- [ ] Consumer contract documented (if applicable)

---

### B4: [Task Name]

**Purpose:** Prove the backend works.

**What to build:** Unit tests for the service method, integration tests for the endpoint covering happy path + each error case from §1.6.

**Acceptance Criteria:**
- [ ] All new tests pass via the project's standard test command
- [ ] No existing tests broken
- [ ] Coverage of every row in §1.6

---

### F1: [Task Name]

**Purpose:** Wire the feature into the UI.

**What to build:** Component(s) — props, state, mutation/query hook(s) used, loading/error states. Cite the analogous existing component to match.

**Acceptance Criteria:**
- [ ] Component renders the documented states (idle / loading / success / error)
- [ ] On success, cached order data is updated locally
- [ ] On error, the user sees a message tied to the error code from §1.6

---

### F2: [Task Name]

**Purpose:** Place the new action where users will find it.

**What to build:** Where the new component is mounted, visibility rules tied to status + permission, accessibility expectations.

**Acceptance Criteria:**
- [ ] Action appears only when status + permission allow it
- [ ] Keyboard-accessible
- [ ] All new strings are localised (if the project ships multiple languages)

---

### F3: [Task Name]

**Purpose:** Prove the UI works.

**What to build:** Component tests + at least one end-to-end happy-path test against a seeded order.

**Acceptance Criteria:**
- [ ] All new tests pass
- [ ] No existing tests broken

---

### P1: [Task Name]

**Purpose:** Grant access.

**What to build:** New permission seeded; admin UI updated so the permission can be assigned to roles.

**Acceptance Criteria:**
- [ ] Permission exists after seed run
- [ ] Admin UI lists it under the correct group
- [ ] Role with the permission can perform the action; role without it gets 403

---

<!--
Repeat ### [ID]: [Task Name] for each task in the queue.
Keep the same structure. Consistency matters more than perfection.
Group IDs (D/B/F/P/…) are illustrative — use whatever prefixes match the subsystems this project actually has.
-->

---

## 4. QA Validation Plan

How to verify the feature works end-to-end after all tasks are implemented. Tailor to what was built. Only include sub-sections that actually apply.

### Browser / App Verification (for UI changes)

| # | Step | Expected Result |
|---|------|-----------------|
| 1 | Log in as [persona] | [landing page] |
| 2 | Navigate to [feature] | [expected state] |
| 3 | Perform [action] on a valid record | [success state] |
| 4 | Repeat on an invalid record | Error message from §1.6 |

### API Verification

| Scope | What to test | Type |
|-------|--------------|------|
| Happy path | Endpoint returns contracted shape | Integration |
| Auth missing | Endpoint returns 401 | Unit |
| Forbidden actor | Endpoint returns 403, no side effects | Integration |
| Each error code from §1.6 | Matches stated HTTP code + body | Integration |

### Database Verification

| Scope | How to verify |
|-------|---------------|
| Migration applies on a fresh DB | Run the project's migration command end-to-end |
| Migration rolls back cleanly | Run the project's rollback command (or note no-down) |
| New audit rows written | Trigger the action, inspect the audit table |

### Background / Event Verification

| Scope | How to verify |
|-------|---------------|
| Event emitted on success | Tail the queue/topic; confirm one message per action |
| Event payload shape | Compare against §1.3 contract |
| Consumer behaviour (if owned by this feature) | Run the consumer locally; confirm side effects |

### Edge Case Verification (from §1.6)

| Edge Case | How to verify |
|-----------|---------------|
| [Case 1] | [Repro steps + expected result] |
| [Case 2] | [Repro steps + expected result] |

---

## 5. Risks & Deployment Notes

Project-specific risks the implementing agent must handle before calling the task done. Only include rows that actually apply.

- **Migration safety:** is the migration safe under concurrent writes / on the production data volume?
- **Backfill:** any existing rows that need to be updated retroactively?
- **Feature flag:** is the change behind a flag? Default on/off? Who flips it?
- **Rollout order:** does the backend need to ship before the frontend (or vice versa)?
- **Backwards compatibility:** existing API consumers / URLs / data shapes that must keep working.
- **Observability:** new metrics / log lines / alerts to watch during rollout.
- **Security:** anything that warrants a security review (auth changes, new external surface, sensitive data).
- **Performance:** expected load on the new path; any indexes/caches required.
- **Rollback:** concrete steps to undo the change in production.

### Suggested project-docs update

If new durable project knowledge was surfaced during Phase 2 / 3 (a business rule, an architectural decision, a clarified edge case), propose it here for the developer to review — do **not** modify `CLAUDE.md` / `README` / `ARCHITECTURE.md` unprompted.

```
File: <path/to/doc>
Section: <heading>
Content:
- <new rule / insight>
- <additional notes if needed>
```

---

## 6. Complexity

**[Trivial | S | M | L | XL]**

[One or two sentences explaining why this score, focused on **scope**: subsystems touched, new domain objects, integration surfaces, novelty, deferred ambiguity. Do not describe how long the work will take.]

**Scale:**

| Score   | Scope anchor                                                                                                  |
|---------|---------------------------------------------------------------------------------------------------------------|
| Trivial | Zero new surface. Config flag, copy tweak, single-line fix.                                                   |
| S       | Single small change in one subsystem / one file / one column. No new domain object.                          |
| M       | Moderate scope. Multiple files in one subsystem, or one new domain object, or one new endpoint over an existing module. |
| L       | Multiple subsystems touched, one new domain object, real integration work.                                   |
| XL      | Cross-cutting: many new objects, many integration points, or changes to core domain rules / state machines. Usually must be split before intake. |

> **If XL:** this ticket is likely too large to implement as a single unit and should be split before intake. Candidate split points:
>
> - [Suggested split 1 — e.g. by subsystem boundary]
> - [Suggested split 2 — e.g. by persona]
> - [Suggested split 3 — e.g. by acceptance-criteria cluster]
