---
name: simulation
description: >-
  Use when working on extract timing model (ETM) simulation tasks such as simulation setup,
  run directory creation, run-file setup, netlist mapping, job submission, bbSim-style testbench
  execution, raw timing library generation, or collecting pre-postedit simulation outputs.
---

# Simulation

This skill supports the simulation stage of the ETM flow.

When this skill is active:
- Focus only on the pre-postedit stage that produces raw timing-model outputs.
- Use the repo's ETM terminology: working directory, run file, netlist mapping, submitted job, raw libs, timing library.
- Prefer concrete execution plans over general advice.
- Identify the minimum required inputs before execution: project, subproject, cell list, working directory, run inputs, and expected output location.
- If the user already provided enough inputs, proceed directly instead of asking exploratory questions.
- Keep outputs oriented around artifacts that unblock the next stage.

Simulation-stage responsibilities:
- Prepare or validate the working directory for the ETM run.
- Set up the run file or simulation inputs needed for timing-model extraction.
- Confirm the cell scope and requested corners or modes when those affect the run.
- Map the required netlist or source data into the run setup.
- Submit or guide submission of the simulation job.
- Track the location of generated raw libraries and logs needed by the next step.

Boundaries:
- Do not perform postedit-specific cleanup, plan-option adjustments, lib reformatting, or final library packaging.
- Do not perform TMQA analysis in this stage.
- Once raw library outputs exist, hand off to the postedit skill.

Response style:
- Be direct and execution-focused.
- Prefer short step lists, exact paths, exact commands, and explicit missing inputs.
- If blocked, report only the missing inputs or failing step that prevents simulation from producing raw timing-model outputs.