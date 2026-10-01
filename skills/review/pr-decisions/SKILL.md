---
name: pr-decisions
description: Surface the decisions a pull request or merge request makes quietly — limits, timeouts, budgets, retries, defaults, what it skips, how it fails, what it trusts — each with where it's set, the reason given (or "not recorded"), and what happens if the value is wrong. Not a bug review. Use when the user points at a PR/MR, branch or diff and asks "what does this decide", "what's hidden in this PR", "surface the important details", "what would I need to explain later", "decisions in this PR", or is about to approve a large or AI-written change.
---

# PR decisions

Large changes, especially AI-written ones, carry decisions nobody said out loud: a 6-minute
timeout, a $1 budget, a cap of 10, a job that passes when it fails. They're a few lines in a
thousand-line diff, so reviewers miss them. Months later someone asks "why is it 6 minutes?"
and nobody knows.

This skill finds those decisions and puts each one in a single line: what the value is, where
it's set, why it was chosen and what breaks if it's wrong. It doesn't judge whether the code is
correct. That's a code review's job. It shows what the change commits to.

`<skill>` below is this skill's directory. The helper script needs only Python 3.

## 1. Get the diff and the stated intent

Work from a local checkout of the repo when there is one. Pure `git` works for both GitHub and
GitLab, because both expose the change as a ref:

```bash
git fetch origin pull/123/head:pr-123            # GitHub
git fetch origin merge-requests/123/head:mr-123  # GitLab
git diff origin/main...pr-123                    # three dots: only what the change adds
```

Or use the host CLI if it's installed: `gh pr diff 123` / `gh pr view 123 --comments`, or
`glab mr diff 123` / `glab mr view 123 --comments`. For a branch or local work, use
`git diff <base>...HEAD`. Use the real target branch, not always `main`.

Also collect what the author said: the PR/MR title and description, its discussion if you can
read it, and the commit messages (`git log --format='%h %s%n%b' <base>..<head>`). These are
where reasons come from in step 3.

## 2. Sweep for candidates, then read

Run the sweep so that nothing is missed just because it was one line among hundreds:

```bash
git diff origin/main...pr-123 | python3 <skill>/scripts/candidates.py
```

It lists every added line that sets a number with a unit, a limit-like number, an environment
default, an on/off switch, a CLI flag, or a fail-soft pattern (`|| true`, `allow_failure`, an
empty `catch`, `exit 0`). When the same hunk removed the old value, it prints `was:` too, so
changed values show as old → new. Tests, fixtures, docs and lockfiles are skipped. Pass
`--include-tests` or `--include-docs` when those matter.

The sweep is for recall. Expect noise, and expect it to miss decisions that aren't literals.
**Then read the diff yourself** for the kinds a pattern can't see:

- **Failure behaviour:** on error, does it retry, skip, fall back, swallow the error, or pass anyway? Does the user find out?
- **Exclusions:** files, users, branches, event types or sizes it deliberately doesn't handle.
- **Trust and access:** token scopes, tools or permissions granted or withheld, what counts as untrusted, what's sent to a third party.
- **Where things come from:** which branch, file, service or model a value is read from; hard-coded URLs, regions and endpoints.
- **Silent loss:** truncation, caps, dropped items, `slice`/`limit`/`head` on user-visible data.
- **Scope cuts:** things the change says it won't do yet (a TODO, a "for now", a stub).

Keep a candidate only if a reasonable person could ask "why this and not something else?" and
the answer affects behaviour, cost, security or operations. Drop array indexes, formatting
widths, and values dictated by an external spec (HTTP status codes, a schema's own bounds).
Record the old value for anything the change modifies rather than introduces. When the file is
new, check whether the value changed *within* the branch (`git log -p -S'<literal>' <base>..<head>`).
A timeout that went from 8 to 6 minutes in a later commit was deliberately tuned, and that commit
usually says why.

## 3. Find the reason for each one

Start by reading every commit message in full once
(`git log --format='%h %s%n%b' <base>..<head>`). It's cheaper than searching per value, and it
answers many of them at once. Then, for each decision still without a reason, look in this order
and record where you found it:

1. **A comment** at or near the line, in the diff or the surrounding file.
2. **The commit** that introduced it: `git log -S'<literal>' --format='%h %s%n%b' <base>..<head> -- <file>`.
3. **The PR/MR description or discussion.**
4. **A linked ticket, spec or design doc**, if your agent can read it.
5. **Past agent sessions.** For AI-written changes the reasoning often exists only in the chat
   that produced it. If a session-history skill such as `recall` is available, search for the
   branch name plus the most distinctive term, such as a constant or setting name
   (`MAX_RETRIES`, `REVIEW_TIMEOUT`). Bare numbers match too much. Skip the session you're
   running in, since it contains the terms you just typed. Label anything found there
   **session-only**: it's real, but a reviewer can't see it. Keep this search to a few queries.

Then label each decision:

- **Stated:** a reason is written somewhere a teammate can find it. Quote it briefly.
- **Partly stated:** the mechanism is explained but not the number ("waits for the diff to catch
  up", but not why 30 s). Common, and worth asking about.
- **Session-only:** the reason exists only in an agent transcript.
- **Contradictory:** two sources disagree (a comment says one thing, the README another). Name both
  locations. These rank high: someone is already wrong.
- **Not recorded:** no reason anywhere. Say what you'd guess, marked as a guess, or say plainly that you can't tell.

Never invent a reason and present it as stated. "Not recorded" is the most useful thing this skill reports.

## 4. Look for coupled values

Some decisions only make sense together, and a later edit to one breaks the other quietly. For
example: the script's timeout has to stay below the job's timeout, the page size times the page
cap is the real maximum, and a retry count times the backoff has to fit inside the timeout. List
each pair and the rule linking them, with both locations.

## 5. Report

Rank by how badly a wrong value hurts: silent data loss or skipped work, then security and
access, then money, then limits users hit, then operational timing, then internal tuning. These
overlap, so when a decision fits several, rank it by the worst one. If a source you'd normally
use wasn't available (no access to the PR description, say), say so in one line under the heading. Put
the top 10–15 in the table. List the rest in one line each, so nothing is hidden, just ranked
lower.

```markdown
## Decisions in <title> — <N> found, <U> not recorded

| # | Decision | Value | Where | Why | If wrong |
|---|---|---|---|---|---|
| 1 | Worker call timeout | 6 min (was: none) | `worker.py:91` | Not recorded — likely sized to fit the 10 min job | Large inputs time out and are never processed |

**Coupled:** `worker.py:91` timeout (6 min) must stay below `ci.yml:43` job timeout (10 min), or the job is killed before it can report.

**Questions for the author:** one line per *not recorded*, *partly stated*, *contradictory* or *session-only* decision whose
answer you'd want in the code. Phrase them so they can be pasted into a review comment.

**Also set:** the lower-ranked decisions, one line each.
```

Keep the "Why" cell short. For a stated reason, name its source (`comment`, `commit abc123`,
`PR description`, `session 2026-03-02`). For "If wrong", give the specific observable effect,
not "could cause issues".

## 6. Offer next steps; don't post

Offer to save the report next to the repo, or to turn the questions into review comments. Post
to the PR/MR only when the user explicitly says yes. For session-only reasons, suggest the
author move them into a code comment or the PR description, since that fixes the problem at the
source.
