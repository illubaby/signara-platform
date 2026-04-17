"""Domain entities for Jira task management."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class JiraTask:
    """Represents a Jira task to be created."""
    summary: str
    brief: str
    outcome: str
    assignee: str
    stakeholder: str
    labels: str
    due_date: str

    def to_dict(self) -> dict:
        """Convert task to dictionary format for JSON serialization."""
        return {
            "summary": self.summary,
            "brief": self.brief,
            "outcome": self.outcome,
            "assignee": self.assignee,
            "stakeholder": self.stakeholder,
            "labels": self.labels,
            "due_date": self.due_date
        }


@dataclass
class JiraBatchConfig:
    """Configuration for batch Jira task creation."""
    last_env: str
    tasks: list[JiraTask]

    def to_dict(self) -> dict:
        """Convert config to dictionary format for JSON serialization."""
        return {
            "last_env": self.last_env,
            "tasks": [task.to_dict() for task in self.tasks]
        }
