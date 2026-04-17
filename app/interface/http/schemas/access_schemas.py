"""Pydantic schemas for access information API."""

from pydantic import BaseModel, Field


class AccessInfoResponse(BaseModel):
    """Response schema for access type detection."""
    access_type: str = Field(..., description="Type of access: local, ssh_forwarded, or remote")
    host: str = Field(..., description="The host header from the request")
    is_local: bool = Field(..., description="Whether access is from localhost")
    is_ssh_forwarded: bool = Field(..., description="Whether access appears to be via SSH port forwarding")
    description: str = Field(..., description="Human-readable description of the access type")
