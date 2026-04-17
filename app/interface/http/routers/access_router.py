"""Router for access type detection."""

from fastapi import APIRouter, Request
from app.application.common.use_cases import DetectAccessType
from app.interface.http.schemas.access_schemas import AccessInfoResponse

router = APIRouter(prefix="/api/access", tags=["access"])


@router.get("/type", response_model=AccessInfoResponse)
async def get_access_type(request: Request):
    """Detect whether the application is accessed locally or via SSH port forwarding.
    
    Returns information about how the client is accessing the application based on
    the request's host header.
    """
    host = request.headers.get("host", "unknown")
    use_case = DetectAccessType()
    access_info = use_case.execute(host)
    
    return AccessInfoResponse(
        access_type=access_info.access_type.value,
        host=access_info.host,
        is_local=access_info.is_local,
        is_ssh_forwarded=access_info.is_ssh_forwarded,
        description=access_info.description
    )
