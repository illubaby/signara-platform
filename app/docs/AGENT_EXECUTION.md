# Definition
a runtime / client-server tool stack that gives you an agent shell, tools, sessions, config, MCP integration, and a programmable server/SDK. It is not, by itself, the full theory of agent architecture.

OpenCode is still mainly a coding-agent-oriented runtime
edit files,
run scripts,
inspect a repo/workspace,
connect tools via MCP,
build an automation assistant around a project directory

Microsoft Agent Framework explicitly focuses on building, orchestrating, and deploying AI agents and multi-agent workflows, with graph-based workflows, checkpointing, human-in-the-loop, and observability.
long-running business workflows,
durable orchestration,
graph-based multi-agent execution,
human checkpoints,
service-style hosting,
complex stateful agent apps
# Advice
Start with OpenCode only if you want:

one main agent,
a project workspace,
a few strong tools/scripts,
AGENTS.md context,
SKILL.md reusable procedures,
maybe MCP integrations,
mostly interactive or semi-automated execution. [opencode.ai], [opencode.ai], [open-code.ai]

Add the OpenCode SDK if you want:

to launch/control OpenCode from your own app,
build a custom UI or dashboard,
trigger prompts programmatically,
manage sessions/events from your own code,
integrate OpenCode into a bigger automation system. [open-code.ai], [mintlify.com]

Move to a broader orchestration framework if you want:

durable workflows,
graph-based routing,
explicit state machines,
many cooperating agents,
checkpoints / time-travel / retry semantics,
enterprise-grade observability. [github.com], [microsoft.github.io]