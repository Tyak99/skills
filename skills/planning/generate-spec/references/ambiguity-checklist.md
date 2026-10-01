# Ambiguity Checklist

Run this on every requirement before accepting it. Nine types of natural-language ambiguity that cause implementation bugs.

## The 9 Types

| # | Type | Signal | Example Problem | Fix |
|---|------|--------|-----------------|-----|
| 1 | **Vagueness** | "fast", "efficient", "large", "appropriate" | "respond quickly" | Quantify: "within 500 ms at p95 under expected load" |
| 2 | **Missing actor** | "the user", "it", "this" | "the user can edit" — which user? | Name explicitly: "the authenticated admin of organisation X" |
| 3 | **Missing trigger** | No "when" or "if" | "validate input" — when? | Add trigger: "when the save action is invoked" |
| 4 | **Missing error path** | Happy path only | "process the order" — what if payment fails? | Enumerate: "if the payment provider returns a non-2xx, reject with HTTP 402 and show error toast '…'" |
| 5 | **Implied behavior** | "handle", "support", "manage" | "handle errors" — how? | Specify: "log via the existing logging pipeline, return a structured error response, show user-visible notification with retry CTA" |
| 6 | **Assumed state** | Presupposes something exists | "when the order is shipped" — is `shipped` a real status? | State prerequisite explicitly, cite the source-of-truth (enum, table, doc) |
| 7 | **Obligation level** | "should", "may", "could", "might" | "should notify admin" — required or nice-to-have? | Decide: "shall" = must, "should" = recommended, "may" = optional |
| 8 | **Context-dependent** | Role/term means different things to different readers | "administrator" — system admin? tenant admin? feature admin? | Define in context — map to an existing role/permission if possible |
| 9 | **Underspecification** | Missing who/what/when/where/how | "send notification" — to whom? via which channel (email, push, in-app)? | Fill all blanks |

## Red-Flag Words

These almost always signal ambiguity:

| Word | Problem | Ask |
|------|---------|-----|
| etc. | Undefined scope | "What specifically is included?" |
| appropriate | Subjective | "What are the criteria?" |
| handle | Ambiguous action | "Log, retry, reject, or alert?" |
| support | Unclear scope | "What exactly can the user do?" |
| various / some / any | Undefined set | "Which ones specifically?" |
| efficient / fast | No threshold | "What's the target number?" |
| user-friendly | Unmeasurable | "What's the specific UX requirement?" |
| automatically | Hides the trigger | "What event causes it? Batch job? Trigger? Webhook?" |
| seamless | Hides the seam | "What's the actual transition / state change?" |
| robust | Hides the failure modes | "Which failure modes specifically must it survive?" |

## Quick Scan

For each requirement, verify:

- [ ] No vague adjectives without thresholds
- [ ] No pronouns without clear antecedents
- [ ] No passive voice hiding the actor
- [ ] No compound "and/or" (split into separate requirements)
- [ ] All quantities specified (time, size, count)
- [ ] All error/edge cases covered
- [ ] Obligation level clear (must vs should vs nice-to-have)
- [ ] Domain entities named using *this project's* vocabulary — not generic ones
- [ ] Role/persona mapped to an existing permission / feature flag (or new one flagged)
