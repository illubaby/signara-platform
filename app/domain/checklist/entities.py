"""Checklist domain entities."""
from dataclasses import dataclass
from typing import List


@dataclass
class ChecklistItem:
    """An individual checklist item."""
    item: str
    done: bool
    note: str
    date: str


@dataclass
class TaskGroup:
    """A group of related checklist tasks."""
    title: str
    duration: str
    tasks: List[ChecklistItem]


@dataclass
class ChecklistSection:
    """A section of the checklist (e.g., Preliminary Release, Prefinal Release)."""
    title: str
    milestone: str
    task_groups: List[TaskGroup]


@dataclass
class Checklist:
    """Complete checklist for a project."""
    sections: List[ChecklistSection]
    
    @classmethod
    def from_dict(cls, data: list) -> "Checklist":
        """Create Checklist from JSON dict structure."""
        sections = []
        for section_data in data:
            task_groups = []
            for tg_data in section_data.get("task_groups", []):
                tasks = []
                for task_data in tg_data.get("tasks", []):
                    tasks.append(ChecklistItem(
                        item=task_data.get("item", ""),
                        done=task_data.get("done", False),
                        note=task_data.get("note", ""),
                        date=task_data.get("date", "")
                    ))
                task_groups.append(TaskGroup(
                    title=tg_data.get("title", ""),
                    duration=tg_data.get("duration", "1"),
                    tasks=tasks
                ))
            sections.append(ChecklistSection(
                title=section_data.get("title", ""),
                milestone=section_data.get("milestone", ""),
                task_groups=task_groups
            ))
        return cls(sections=sections)
    
    def to_dict(self) -> list:
        """Convert Checklist to JSON dict structure."""
        result = []
        for section in self.sections:
            task_groups_data = []
            for tg in section.task_groups:
                tasks_data = []
                for task in tg.tasks:
                    tasks_data.append({
                        "item": task.item,
                        "done": task.done,
                        "note": task.note,
                        "date": task.date
                    })
                task_groups_data.append({
                    "title": tg.title,
                    "duration": tg.duration,
                    "tasks": tasks_data
                })
            section_data = {
                "title": section.title,
                "task_groups": task_groups_data
            }
            if section.milestone:
                section_data["milestone"] = section.milestone
            result.append(section_data)
        return result
