from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import TypeVar

from canvas_sdk.commands.base import _BaseCommand as BaseCommand


class AssigneeType(Enum):
    """The type of assigner for a Task command."""

    ROLE = "role"
    TEAM = "team"
    UNASSIGNED = "unassigned"
    STAFF = "staff"


@dataclass
class TaskAssigner:
    """A class for managing an assign for a Task command."""

    to: AssigneeType
    id: int | None = None

    def as_dict(self) -> dict:
        """Return the TaskAssigner as a dictionary."""
        return {"type": self.to.value, "id": self.id}


TaskAssignerType = TypeVar("TaskAssignerType", bound=TaskAssigner)


class TaskCommand(BaseCommand):
    """A class for managing a Task command within a specific note."""

    class Meta:
        key = "task"
        commit_required_fields = (
            "title",
            "assign_to",
        )

    title: str = ""
    assign_to: TaskAssignerType | None = None
    due_date: date | None = None
    comment: str | None = None
    labels: list[str] | None = None
    linked_items_urns: list[str] | None = None

    @property
    def values(self) -> dict:
        """The Task command's field values."""
        return {
            "title": self.title,
            "assign_to": self.assign_to.as_dict() if self.assign_to else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "comment": self.comment,
            "labels": self.labels,
            "linked_items_urns": self.linked_items_urns,
        }
