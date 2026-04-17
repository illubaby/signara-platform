---
name: postedit
description: >-
  Use when extract timing model (ETM) work reaches postedit tasks such as Postedit_libs,
  post_edit config files, lib cleanup, -plan option decisions, reformat or reorder options,
  leakage handling, reference lib usage, or finalizing libraries after raw simulation output.
---

# Postedit

This skill supports the postedit stage of the ETM flow.

When this skill is active:
- Treat raw simulation output libraries as input and produce cleaned postedit libraries as output.
- Reuse repo terminology and conventions around post_edit, Postedit_libs, config files, and final lib preparation.
- Prefer the existing local workflow over inventing alternate cleanup logic.
- Keep the work centered on converting raw ETM output into a publishable or QA-ready timing library.

Postedit-stage responsibilities:
- Determine the correct input lib path, config file, reference path, plan option, and output path.
- Guide or perform postedit runs with the parameters already used in this codebase: configfile, lib, reference, copyReference, plan, reformat, reorder, leakage, pt, output.
- Call out when a missing config or invalid path blocks postedit.
- Keep track of the final postedit library location that should be used by downstream QA.

Boundaries:
- Do not redo the simulation-stage setup that should already have produced raw libraries.
- Do not analyze QA failures in depth; once postedit output is ready, hand off to the timing QA flow or timing-qa-analyst agent if requested.

Response style:
- Be explicit about the exact inputs, selected options, and resulting output path.
- Keep recommendations tied to postedit behavior in this repo.
- If blocked, state which postedit input is missing or which postedit step failed.