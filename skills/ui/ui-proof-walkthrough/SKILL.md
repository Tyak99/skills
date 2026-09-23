---
name: ui-proof-walkthrough
description: Present completed UI work as an annotated, presentation-style screenshot walkthrough. Use after implementing user-visible interface changes, or whenever the user asks for screenshots, visual proof, a demo, or a before-and-after explanation of UI work. Do not use for non-visual backend-only changes.
---

# UI Proof Walkthrough

Turn completed UI work into evidence a product stakeholder can understand without knowing where to look.

## Evidence source

- Capture fresh screenshots from the actual tested application or deployed preview. Do not substitute a mockup or reconstructed interface for proof.
- Show the state that proves the change: the entry point, the interaction or open state, and the result when each adds useful evidence.
- Use disposable or synthetic data. Do not expose credentials, personal data, internal tokens, or unrelated customer information.
- Do not submit forms, create production records, or perform other external writes solely to improve the presentation unless the user authorized that behavior as part of the underlying task.
- Include desktop and mobile evidence when the changed surface is responsive. Show every viewport the preview covered, and any the change affects that it didn't. Layout problems usually hide in the viewport nobody looked at.
- Capture what a user actually sees at that viewport. Stitched full-page captures misplace fixed and sticky elements (bottom navs, headers) and can make correct work look broken, or broken work look fine.

## Build the walkthrough

Present the screenshots as a short numbered story in the order a user experiences the feature. Each slide should normally contain:

- a concise outcome-focused title;
- the real screenshot, large and legible;
- one to three numbered callouts marking only changed or behaviorally important controls;
- short labels that explain what changed and why it matters;
- a small footer naming the flow, platform, and viewport when useful.

Prefer one clear point per callout. Put annotation text in added margins where possible, and use thin arrows, outlines, or translucent highlights that do not cover the UI. Match the product's visual language without implying the annotations are part of the product.

## Fidelity is mandatory

The screenshot is evidence. Preserve its pixels, text, controls, values, spacing, and state.

- Prefer deterministic overlays: draw callouts as SVG or HTML and composite them onto the untouched screenshot (for example with `sharp`, ImageMagick, or a browser page that places the screenshot under an overlay).
- If an image-generation or image-editing tool is used, instruct it to preserve the embedded screenshot exactly, then visually compare the result with the source.
- Reject and redo any slide that redraws the UI, changes text or sample values, removes controls, invents states, or points an arrow at the wrong target.
- Every callout must terminate at the control or region described by its label. When precise mapping is unreliable, reduce the slide to one unambiguous callout.
- Keep the original unannotated captures available so the proof can be audited.

## Final presentation

Save the annotated slides as real image files and embed them directly in the response, each under a short numbered caption. Screenshots left inside tool output don't count as shown. Lead with what the walkthrough proves, not with tooling details. State the tested environment or build when known, and disclose that sample data is synthetic or that a state was not submitted.

If visual proof cannot be captured, say exactly what is unavailable and provide the strongest non-visual verification instead. Never present an illustration as observed proof.
