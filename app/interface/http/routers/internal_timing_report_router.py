"""Post-Edit v2 router using shared layout_form_route factory."""
from app.domain.internal_timing.report_entities import FormConfig
from .layout_form_router import create_form_page_router

# Expose router using reusable factory (no duplication)
router = create_form_page_router(
    route_path="/internal-timing-report",
    template_name="internal_timing_report.html",
    title="Internal Timing Report",
    page_id="internal-timing-report",
    form_config_cls=FormConfig,
)
