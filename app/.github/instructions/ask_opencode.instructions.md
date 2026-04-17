---
description: "Use when the user mentions OpenCode, opencode, open-code.ai, opencode.jsonc, OPENCODE.md, OpenCode agents, subagents, config, or asks to consult official OpenCode documentation."
applyTo: "opencode.jsonc,OPENCODE.md,.opencode/**"
---
description: "Use when the user mentions OpenCode, opencode, open-code.ai, opencode.jsonc, OPENCODE.md, OpenCode agents, subagents, config, or asks to consult official OpenCode documentation."
---

# OpenCode Guidance

- When the user asks a question about OpenCode, first consult https://open-code.ai/en/docs.
- If the normal webpage fetch is blocked by a gateway or proxy, fall back to a terminal-based HTTP request to the official docs before using secondary sources.
<!-- - On Windows, prefer PowerShell with a command like: `$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -UseBasicParsing https://opencode.ai/docs/config/ | Select-Object -ExpandProperty Content` -->
- Another reference source, in case you cannot find the answer in the official documentation, is https://deepwiki.com/tencent-source/opencode, https://learn-opencode.vercel.app/. 
- Base the answer on the official documentation.
- If the documentation does not fully answer the question, say that clearly and separate documented facts from inference.
- When useful, include the relevant documentation link in the response.

## Editing OpenCode Agents In This Repo

- When the user describes a TimeCraft page action, button, or workflow that should be added to an agent, first trace the real implementation path in this repo:
	- page or feature name
	- router endpoint
	- application use case
	- timing integration helper if one exists
	- adapter entrypoint under `intergrations/adapters/timing/`
- Prefer existing TimeCraft functions and existing timing adapters over inventing new workflow text.
- When mapping a page capability into an OpenCode timing agent, use the page name or the corresponding TimeCraft function name so the edited agent step points at the concrete source of truth.
- If users asked to update opencode agent .md file after update, please make it short and compact, dont become lengthy, just update the step that need to be updated. 