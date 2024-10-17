from datetime import date
from enum import Enum, StrEnum

from typing_extensions import NotRequired, TypedDict

from canvas_sdk.commands.base import _BaseCommand as BaseCommand


class AssigneeType(StrEnum):
    """The type of assigner for a Task command."""

    ROLE = "role"
    TEAM = "team"
    UNASSIGNED = "unassigned"
    STAFF = "staff"


class TaskAssigner(TypedDict):
    """A class for managing an assign for a Task command."""

    to: AssigneeType
    id: NotRequired[int]


class TaskCommand(BaseCommand):
    """A class for managing a Task command within a specific note."""

    class Meta:
        key = "task"
        commit_required_fields = (
            "title",
            "assign_to",
        )

    title: str = ""
    assign_to: TaskAssigner | None = None
    due_date: date | None = None
    comment: str | None = None
    labels: list[str] | None = None
    linked_items_urns: list[str] | None = None

    @property
    def values(self) -> dict:
        """The Task command's field values."""
        return {
            "title": self.title,
            "assign_to": self.assign_to,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "comment": self.comment,
            "labels": self.labels,
            "linked_items_urns": self.linked_items_urns,
        }
