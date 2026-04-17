"""Timing QA v2 router using shared layout_form_route factory."""
from app.domain.release.entities import FormConfig
from .layout_form_router import create_form_page_router

# Expose router using reusable factory (no duplication)
router = create_form_page_router(
    route_path="/project-release",
    template_name="project_release.html",
    title="Project Release",
    page_id="project-release",
    form_config_cls=FormConfig,
)