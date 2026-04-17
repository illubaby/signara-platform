"""Internal Timing router using shared layout_form_route factory."""
from app.domain.internal_timing.entities import FormConfig
from .layout_form_router import create_form_page_router

# Expose router using reusable factory (no duplication)
router = create_form_page_router(
    route_path="/internal-timing",
    template_name="internal_timing.html",
    title="Internal Timing",
    page_id="internal-timing",
    form_config_cls=FormConfig,
)
