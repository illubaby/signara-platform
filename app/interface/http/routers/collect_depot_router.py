"""Timing QA v2 router using shared layout_form_route factory."""
from app.domain.collect_depot.entities import FormConfig
from .layout_form_router import create_form_page_router

# Expose router using reusable factory (no duplication)
router = create_form_page_router(
    route_path="/collect-depot",
    template_name="collect_depot.html",
    title="Collect Depot",
    page_id="collect-depot",
    form_config_cls=FormConfig,
)