---
name: ui-change-preview
description: Preview proposed user-interface changes before implementation by annotating the current real UI. Use when an incoming task may add, remove, move, rename, recolor, or otherwise change visible controls, content, states, or layouts. Do not use for backend-only work or as proof of completed UI.
---

# UI Change Preview

Show the user what a proposed UI change would affect before code changes begin.

## Establish the proposal

- Read the task, product authority, and relevant design guidance first.
- Identify the smallest set of visible changes the task actually requires. Do not silently redesign adjacent areas.
- If the task has no meaningful UI impact, say so and continue without producing a preview.

## Capture the current UI

- Capture fresh screenshots from the actual current application, preferably current `main`, using synthetic or explicitly authorized data.
- Use the real screen, viewport, and state where the change will appear.
- If the change adds, removes, moves, or resizes anything on a responsive surface, preview it at both desktop and mobile widths. A placement that reads well on a phone can look broken on a wide screen, and a one-viewport preview approves both without showing one. Use a single viewport only for changes that can't affect layout (copy, color, icon swaps), and say which one you chose.
- Capture what a user actually sees at that viewport. Stitched full-page captures misplace fixed and sticky elements (bottom navs, headers) and make the UI look different than it does.
- Before proposing placement, check the project's own layout and design rules (design docs, `AGENTS.md`, existing patterns) and follow them.
- Do not create production records, use personal customer data, or modify the product merely to improve the preview.
- If the application cannot be accessed, use a user-provided screenshot. If neither is available, explain what evidence is missing instead of inventing the current UI.

## Annotate the proposed change

- Preserve the captured screenshot pixels and add deterministic overlays. Do not use image generation to redraw the interface.
- Mark additions with a dashed or ghost outline positioned where they are proposed to appear. Mark removals, moves, copy changes, and visual changes with precise numbered callouts.
- Use future-tense labels such as “New button will appear here” or “This status will become red.” Never make a proposal read like an implemented state.
- Make every callout terminate at the exact control or region it describes. Keep annotations in added margins when possible so the existing UI remains legible.
- Do not invent exact visual details when the task has not decided them. Label unresolved choices and show alternatives only when the user needs to choose between them.

## Present the preview

- Save the annotated images as real image files and show them inline in the conversation. A screenshot that only exists inside a tool log isn't a preview the user can approve.
- Lead with the user-visible outcome and label the artifact **Concept preview — not implemented**.
- Present the views as a short numbered story in the order a user would encounter the change.
- For each view, include the current real screenshot, one to three proposed-change callouts, and a small footer naming the screen, viewport, and evidence source.
- Keep the original unannotated screenshots available for audit.
- State any behavior that cannot be shown in a static image in plain language.

## Approval gate

When this skill is used before implementation, stop after presenting the preview and ask the user whether the placement, wording, and visual treatment are right. Do not begin implementation until they approve or revise the proposal. Approval applies only to the depicted scope; follow the normal authorization rules for code, deployments, data, and external systems.
