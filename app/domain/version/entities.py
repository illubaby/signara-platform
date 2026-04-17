"""Version domain entities."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class VersionInfo:
    """Version information entity."""
    local_version: str
    remote_version: Optional[str]
    deadline: Optional[datetime]
    
    @property
    def is_outdated(self) -> bool:
        """Check if local version is outdated compared to remote."""
        if self.remote_version is None:
            return False
        return self.local_version != self.remote_version
    
    @property
    def is_past_deadline(self) -> bool:
        """Check if current time is past the mandatory update deadline."""
        if self.deadline is None:
            return False
        return datetime.now() > self.deadline
    
    @property
    def must_update(self) -> bool:
        """Check if update is mandatory (outdated AND past deadline)."""
        return self.is_outdated and self.is_past_deadline
