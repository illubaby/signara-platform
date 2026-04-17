"""Post-Edit v2 router using shared layout_form_route factory."""
from app.domain.post_edit.entities_v2 import FormConfig
from .layout_form_router import create_form_page_router

# Expose router using reusable factory (no duplication)
router = create_form_page_router(
    route_path="/post-edit-v2",
    template_name="post-edit-v2.html",
    title="Post Edit V2",
    page_id="post-edit-v2",
    form_config_cls=FormConfig,
)
