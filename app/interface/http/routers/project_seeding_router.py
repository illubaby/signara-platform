"""Timing QA v2 router using shared layout_form_route factory."""
from app.domain.project_seeding.entities import FormConfig
from .layout_form_router import create_form_page_router

# Expose router using reusable factory (no duplication)
router = create_form_page_router(
    route_path="/project-seeding",
    template_name="project_seeding.html",
    title="Project Seeding",
    page_id="project-seeding",
    form_config_cls=FormConfig,
)