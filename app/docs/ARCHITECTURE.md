# Application Architecture (TimeCraft Platform)

This document defines the 5-layer Clean Architecture variant used in this FastAPI + Jinja2 application. It exists so both humans and AI assistants can quickly understand boundaries, allowed dependencies, naming conventions, and the migration path from older code.

## Layer Overview

We adopt a pragmatic 5-layer view. Conceptually layers 4 and 5 both live in the canonical Clean Architecture outer ring ("Frameworks & Drivers"), but are split for clarity.

1. Domain (Enterprise / Core Business Rules)
2. Application (Use Cases / Orchestration)
3. Interface (Adapters: HTTP, presenters, DTO mappers, dependency wiring)
4. Infrastructure (External implementations: filesystem, subprocess, Perforce, caching, settings, logging)
5. Presentation (UI: templates, static assets - JS, CSS, images)

### High-Level Responsibilities

| Layer          | Responsibility                                                                 | Allowed Dependencies | Forbidden Dependencies |
|----------------|----------------------------------------------------------------------------------|----------------------|------------------------|
| Domain         | Pure business entities, value objects, domain exceptions, invariants            | None (only stdlib)   | Application, Interface, Infrastructure, Presentation |
| Application    | Use case classes/functions invoking domain rules and repository/service ports    | Domain               | Interface, Presentation (direct), concrete infrastructure classes |
| Interface      | Translates external input (HTTP) to application use-case calls and maps outputs | Domain, Application  | Presentation internals, direct low-level infra (prefer ports) |
| Infrastructure | Implements ports: persistence, FS, external APIs, subprocess, caching, logging  | Domain (for models)  | Presentation (direct), circular deps back into Application |
| Presentation   | HTML/Jinja templates, JS, CSS, UI composition                                    | Interface (API schema contract), Asset build tools | Domain (direct business logic), Application logic, infrastructure internals |

## Dependency Rule

The source code dependency graph must point inward:

```
Presentation -> Interface -> Application -> Domain
Infrastructure -> (ports consumed by Application)
Interface may depend on Infrastructure only for wiring (factory functions) but not for core logic.
```

No outward dependency (e.g., Domain importing FastAPI) is permitted.

## Folder Layout (Target)

```
app/
  domain/
    projects/
      entities.py          # Project, Subproject dataclasses
      repositories.py      # Protocols / ABCs for project access
    release/
      entities.py          # ReleaseJob, status enums
      repositories.py      # Release job & changelist query ports
    qa/
      entities.py          # QA summary row, cell selection rules
    common/
      errors.py            # Domain-specific exception types
      value_objects.py     # Reusable validated types (e.g., PathSegment)
  application/
    projects/use_cases.py  # ListProjects, ListSubprojects
    release/use_cases.py   # StartRelease, GetReleaseStatus, ListChangeLists
    qa/use_cases.py        # LoadDefaults, RunQa, GetQaSummary
  interface/
    http/
      routers/
        projects_router.py
        release_router.py
        qa_router.py
        explorer_router.py  # Thin wrappers
      schemas/
        projects.py         # Pydantic request/response models
        release.py
        qa.py
      dependencies.py       # FastAPI Depends factories (binding use-cases)
    presenters/
      release_presenter.py  # Convert domain ReleaseJob -> API DTO
  Version: 2025-11-04

  Goal: concise reference (layers, imports, migration status, next steps).

  ## Layers
  1. Domain – Pure business types + ports (protocols). No framework imports.
  2. Application – Use cases orchestrating domain + ports. Stateless.
  3. Interface – FastAPI routers, schemas, dependency providers. Thin.
  4. Infrastructure – External concerns (fs, Perforce, processes, caching, settings, logging, Excel, terminal).
  5. Presentation – Templates + static assets (JS/CSS/images). No business rules.

  Dependency direction: Presentation -> Interface -> Application -> Domain. Infrastructure implements ports. No outward imports from Domain.

  ## Feature Modules
  dashboard, explorer (partial), impostor, lsf, post_edit, projects, qa, qc, release, saf, task_queue, terminal, common.

  ## Ports & Adapters
  Ports in `domain/<feature>/repositories.py`; infra implementations in `infrastructure/**`. Use cases receive ports via constructor; routers resolve use cases via dependency functions.

  ## Import Rules
  Domain: stdlib + domain only.
  Application: domain + typing/util libs.
  Interface: application + domain + FastAPI + Pydantic.
  Infrastructure: domain + stdlib + external libs (never routers).
  Presentation: templates/JS only.

  ## Use Case Pattern
  `execute()` returns domain entities or primitives; validation first; no HTTP objects.

  ## Migration Status
  Dashboard done. Explorer v2 active (legacy v1 pending removal). Post-Edit / QA / QC / Projects / Task Queue / Terminal / LSF / SAF migrated. Project Release legacy router pending refactor. Presentation unified.

  ## Pending Actions
  1. Finish Explorer cutover.
  2. Refactor Project Release.
  3. Add centralized exception handlers.
  4. Optional DI container (reduce wiring in `main.py`).
  5. Reorganize tests by pyramid.
  6. Add import enforcement script.
  7. Move remaining validation helpers in `utils/` into domain value objects.

  ## Caching
  `infrastructure/caching/ttl_cache.py` injected explicitly; avoid hidden globals.

  ## Error Handling
  Domain/app exceptions raised; global FastAPI handlers TODO.

  ## Testing (Target)
  Unit: domain + use cases. Interface: routers. Integration: infra. E2E: optional UI flows.

  ## Naming
  Entity: Noun (`ReleaseJob`). Port: `<Concept>Repository`. Impl: `<Port><Tech>` (`ProjectRepositoryFS`). Use case: Verb phrase (`ListProjects`). Router: `<feature>_router.py`.

  ## Mini Example
  ```python
  class ProjectRepository(Protocol):
      def list_projects(self) -> list[str]: ...
  class ListProjects:
      def __init__(self, repo: ProjectRepository):
          self.repo = repo
      def execute(self) -> list[str]:
          return self.repo.list_projects()
  ```

  ## Maintenance
  Update when: new feature module, migration completion, import rule change. Keep it short.

  ---
  End.
Infrastructure: imports domain + stdlib + external libs (no FastAPI router code).
Presentation: no Python imports beyond templating; JS calls HTTP endpoints.
```

Automated checks (future): a simple script can scan imports to enforce these rules.

## Why 5 Layers Instead of 4

Presentation was split out of the canonical outer ring to isolate UI-specific tooling, faster change cadence, and potential multi-front-end evolution (CLI, desktop shell). Conceptually layers 4 & 5 are siblings, not hierarchical; both depend inward only.

### Presentation Transition (Templates & Static Assets)

Current state (post-migration, fallback removed):

Next improvements:
1. Add a lint / CI script to assert no future additions under other folders (guard rails).
2. Optionally introduce asset pipeline (hashing, bundling) under `presentation/static/`.
3. Consider splitting large JS features into modules with feature-focused directories and adding unit tests (e.g., via Playwright for E2E).

Guidelines during migration:

Future enforcement: Add an import/path check script under `scripts/` to assert no new templates are added outside `presentation/` once migration is complete.

## Dashboard Feature Migration (Example)

Status: **Complete** (November 3, 2025). Legacy `app/routers/dashboard.py` removed.

### Layer Mapping

Domain:
```
app/domain/dashboard/entities.py           # Page, NavigationMenu domain entities
```

Application:
```
app/application/dashboard/use_cases.py     # GetNavigationMenu use case
```

Interface:
```
app/interface/http/dependencies/dashboard.py      # get_navigation_menu_uc factory
app/interface/http/schemas/dashboard.py           # PageSchema, NavigationMenuSchema
app/interface/http/routers/dashboard_router.py    # HTTP endpoints for dashboard
```

Presentation:
```
app/presentation/templates/choose_project.html    # Landing page template
app/presentation/templates/generic_page.html      # Fallback template
app/presentation/templates/*.html                 # All feature-specific templates
```

### Key Design Decisions

1. **Domain Entities**: `Page` and `NavigationMenu` are immutable frozen dataclasses with built-in validation (page IDs must be non-empty, template names must end with `.html`, etc.)

2. **Use Case Pattern**: `GetNavigationMenu` encapsulates the hard-coded page list. Future enhancements could read from config/DB without changing the interface layer.

3. **Template Compatibility**: The router converts domain entities to the legacy `List[Tuple[str, str]]` format expected by existing templates, minimizing template changes.

4. **New API Endpoint**: Added `/api/navigation/pages` for programmatic access to the menu structure (useful for dynamic frontends).

5. **State Migration**: `app.state.pages` is still populated from domain entities for backwards compatibility with any legacy code.

### Request Flow Example

`GET /choose-project`:
1. FastAPI router `choose_project` receives request
2. Dependency injection provides `GetNavigationMenu` use case instance
3. Use case returns `NavigationMenu` domain entity with all pages
4. Router converts to legacy tuple format for template
5. Template rendered with page list

### Benefits of Architecture Alignment


### Migration Checklist (Completed)


### Next Steps (Optional Enhancements)

1. Extract inline JS from templates (e.g., `choose_project.html`) to `presentation/static/js/dashboard/`
2. Add unit tests for domain entities (validation edge cases)
3. Add unit tests for use case
4. Add integration tests for router endpoints
5. Consider making page list configurable via YAML/JSON if dynamic menus are needed

## AI Assistant Guidelines

When adding a feature:
1. Start at Domain: define/extend entities if new business concepts appear.
2. Add/modify a use-case in Application (never put orchestration in routers).
3. If a new external integration is needed, define a port in Domain and implement it in Infrastructure.
4. Expose functionality through a thin Interface router + Pydantic schema.
5. Update Presentation templates/JS as needed (no business rules).
6. Add appropriate tests across the pyramid.

When refactoring legacy code found outside these rules, plan an incremental move (do not break working endpoints).

## Example Code Snippet (Projects)

```python
# domain/projects/repositories.py
from typing import Protocol, List
class ProjectRepository(Protocol):
    def list_projects(self) -> List[str]: ...
    def list_subprojects(self, project: str) -> List[str]: ...

# application/projects/use_cases.py
class ListProjects: ...  # orchestrates repo + cache

# interface/http/routers/projects_router.py
@router.get('/api/projects')
def list_projects(list_uc = Depends(get_list_projects_uc)):
    return {'projects': list_uc.execute()}
```

## Future Extensions



