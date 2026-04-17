"""Timing QA v2 router using shared layout_form_route factory."""
from app.domain.timing_qa.entities import FormConfig
from .layout_form_router import create_form_page_router

# Expose router using reusable factory (no duplication)
router = create_form_page_router(
    route_path="/timing-qa-v2",
    template_name="timing_qa_v2.html",
    title="Timing QA v2",
    page_id="timing-qa-v2",
    form_config_cls=FormConfig,
)