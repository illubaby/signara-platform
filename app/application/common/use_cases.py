"""Use cases for detecting access type."""

from app.domain.common.access_info import AccessInfo, AccessType


class DetectAccessType:
    """Determine if the application is accessed locally or via SSH port forwarding.
    
    Detection logic:
    - localhost/127.0.0.1 = Local access
    - Other IPs or hostnames = SSH forwarded or remote access
    """

    def execute(self, host: str) -> AccessInfo:
        """Detect access type based on the request host.
        
        Args:
            host: The host header from the HTTP request (e.g., "localhost:8003", "127.0.0.1:8003")
        
        Returns:
            AccessInfo with details about the access type
        """
        # Extract hostname without port
        hostname = host.split(':')[0] if ':' in host else host
        hostname = hostname.lower().strip()
        
        # Check if it's local access
        is_local = hostname in ('127.0.0.1', '::1', '0.0.0.0')
        
        if is_local:
            access_type = AccessType.LOCAL
            is_ssh_forwarded = False
            description = "Direct local access - application running on your machine"
        else:
            # If not local, assume SSH port forwarding (most common scenario)
            # Could be refined further if needed to distinguish true remote access
            access_type = AccessType.SSH_FORWARDED
            is_ssh_forwarded = True
            description = f"SSH port forwarding detected - accessing via {hostname}"
        
        return AccessInfo(
            access_type=access_type,
            host=host,
            is_local=is_local,
            is_ssh_forwarded=is_ssh_forwarded,
            description=description
        )
