# Copilot Instructions for TimeCraft Platform (app)

## Architecture Overview
- **4-layer Clean Architecture**: Domain → Application → Interface → Presentation
- **Dependency direction**: All imports point inward; no outward dependencies (e.g., Domain never imports FastAPI)
- **Presentation** is split from Infrastructure for UI clarity and future multi-front-end support

## Layer Responsibilities
- **Domain**: Pure business entities, value objects, protocols. No framework imports.
- **Application**: Stateless use cases orchestrating domain + ports. No direct infra/HTTP.
- **Interface**: FastAPI routers, Pydantic schemas, dependency providers. Thin adapters only.
- **Infrastructure**: Implements ports (FS, Perforce, caching, logging, etc). No direct router code.
- **Presentation**: Jinja2 templates, static assets (JS/CSS/images). No business logic.

## Key Patterns & Conventions
- **Ports & Adapters**: Define ports in `domain/<feature>/repositories.py`, implement in `infrastructure/**`. Use cases receive ports via constructor; routers resolve use cases via dependency functions.
- **Use Case Pattern**: Use cases expose `execute()` methods, return domain entities/primitives, validate inputs, never handle HTTP objects.
- **Naming**: Entity: Noun (`ReleaseJob`), Port: `<Concept>Repository`, Impl: `<Port><Tech>`, Use case: Verb phrase (`ListProjects`), Router: `<feature>_router.py`
- **Testing Pyramid**: Unit (domain/use cases), Integration (infra), Interface (routers), E2E (optional UI flows)

## Developer Workflows
- **Run app**: `pip install -r requirements.txt` then `python -m uvicorn app.main:app --reload`
- **App directory**: Always run with parent folder on PYTHONPATH. See README for PowerShell/uvicorn invocation options.
- **Desktop mode**: `python app_mode.py` (requires pywebview/PyQt)
- **Disable auto-open browser**: `$env:TIMING_AUTO_OPEN_BROWSER='false'`
- **Tests**: See `tests/` for unit/integration coverage. Organize by feature and layer.

## Migration & Maintenance
- Legacy code outside these rules should be incrementally refactored, not broken.
- Update this file when adding new feature modules, changing import rules, or completing migrations.

## Example: Projects Feature
```python
# domain/projects/repositories.py
class ProjectRepository(Protocol):
    def list_projects(self) -> list[str]: ...
# application/projects/use_cases.py
class ListProjects:
    def __init__(self, repo: ProjectRepository):
        self.repo = repo
    def execute(self) -> list[str]:
        return self.repo.list_projects()
# interface/http/routers/projects_router.py
@router.get('/api/projects')
def list_projects(list_uc = Depends(get_list_projects_uc)):
    return {'projects': list_uc.execute()}
```

## Integration Points
- **External systems**: Perforce, filesystem, job queue, caching, logging
- **Presentation**: Templates/JS only call HTTP endpoints, never embed business logic
- **Caching**: Use `infrastructure/caching/ttl_cache.py` via explicit injection

## Error Handling
- Domain/app exceptions raised; global FastAPI handlers planned

---
For full details, see `docs/ARCHITECTURE.md` and `README.md`. Please ask for clarification or suggest updates if any section is unclear or incomplete.

# Signara Agent Instructions
- Signara is an AI co-worker agent that assists engineers with analog mixed-signal design tasks.
## Architecture
- AGENT.md defines the overall architecture and task list for Signara.
- .opencode/agents/* : define agents
- tools/ : reusable tools for agents
- knowledge/ : structured knowledge files for agents to reference