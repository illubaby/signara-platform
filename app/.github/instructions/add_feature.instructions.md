---
applyTo: '**'
---
## TimeCraft Platform – Add / Change / Debug Rules

Use the Clean Architecture :
Domain -> Application -> Interface -> (Presentation outward). All imports point inward. No FastAPI, OS, subprocess, Perforce, or filesystem calls outside Infrastructure.

### 1. When Adding a Feature (Checklist)
1. Domain: Define/extend entities, value objects, enums, and repository Protocols in `domain/<feature>/`. Keep pure Python (stdlib typing only). No business logic in routers/templates.
2. Ports: New external data access? Add a Protocol (`XRepository`) in domain; DO NOT call infra directly from use cases or routers.
3. Infrastructure: Implement the port under `infrastructure/<area>/` (e.g., FS, p4, processes). Inject via constructor; never import router modules.
4. Application: Add a use case class (`VerbNoun`, e.g., `ListProjects`, `GenerateQcTable`) with `execute(...)` returning domain entities or primitives. Validate inputs early.
5. Interface: Expose with a thin router endpoint + Pydantic schema (if JSON) under `interface/http/routers/` and `interface/http/schemas/`. Use dependency providers to assemble use case with infra impls.
6. Presentation: If UI required, add/modify Jinja templates or static JS/CSS in `presentation/`. Absolutely no domain decisions or data shaping beyond display formatting.
7. Tests: Unit (use case, domain invariants), Integration (infra impl), Interface (router happy path). Reuse existing patterns in `tests/`.

### 2. Function Additions (Inside Existing Feature)
Place logic according to responsibility:
- Data shaping / orchestration -> Application use case.
- Validation rules / invariants -> Domain entity or value object factory.
- External I/O (read files, Perforce changelists, subprocess) -> Infrastructure adapter implementing a port.
- HTTP / request parsing -> Interface router/schema only.
- Pure formatting for UI -> Presentation template/JS.

### 3. Naming Conventions
- Entity: Noun (`ReleaseJob`, `NavigationMenu`).
- Port: `<Concept>Repository` or `<Capability>Service` (Protocol in domain).
- Infra Implementation: `<Port><Tech>` (`ProjectRepositoryFS`, `ReleaseJobRepositoryP4`).
- Use case: VerbPhrase (`PrepareRun`, `ListCells`, `DiagnoseNetlist`).
- Router file: `<feature>_router.py`.

### 4. Use Case Pattern
```python
class ListProjects:
	def __init__(self, repo: ProjectRepository):
		self.repo = repo
	def execute(self) -> list[str]:
		return self.repo.list_projects()
```
Rules: single public `execute()`, no FastAPI types, raise domain/application exceptions, never mutate global state.

### 5. Debugging Flow (Trace Request)
Request -> Router -> Dependency provider -> Use case -> Port (Protocol) -> Infra implementation -> Back up stack.
Locate bug by moving inward; do NOT patch around in router with file/process calls. Add focused unit tests rather than print statements. If data mismatch, inspect infra adapter then port contract.

### 6. Forbidden Patterns
- Business logic in templates, JS, routers, or infrastructure adapters.
- Direct infra (filesystem, Perforce, subprocess) calls in routers/use cases.
- Cross-feature deep imports bypassing ports.
- Fat use cases with mixed concerns (split them instead).

### 7. Testing Guidance
- Domain/entity invariants: create minimal tests (invalid names, empty lists).
- Use case: mock port(s), assert output + edge handling.
- Infra: integration test hitting real FS/perforce stub; keep deterministic.
- Router: fast API test client call for success + one validation failure.

### 8. Caching
Use `infrastructure/caching/ttl_cache.py` via explicit injection; never hide caching inside domain or templates.

### 9. Small Refactors
When touching legacy code outside layers: introduce a port + use case first, migrate logic gradually, keep endpoint behavior stable.

### 10. Quick Sanity Before Commit
- Imports respect inward rule.
- New external access behind a Protocol.
- Use case returns domain/primitive only.
- Router endpoint thin (< ~15 LOC).
- No TODO left in critical path; add future tasks to comments minimally.

Adhere to these constraints every time you add, modify, or debug. If unsure, start from Domain and move outward.
Don't create js script inside html, always create a separate .js file in the static folder.
Please use daisyui to reduce effort on styling when needed. For more information visit: **https://daisyui.com/components/**
