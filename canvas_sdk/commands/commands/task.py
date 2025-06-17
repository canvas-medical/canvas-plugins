from datetime import date
from enum import StrEnum
from typing import NotRequired

from typing_extensions import TypedDict

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

    title: str = ""
    assign_to: TaskAssigner | None = None
    due_date: date | None = None
    comment: str | None = None
    labels: list[str] | None = None
    linked_items_urns: list[str] | None = None


__exports__ = (
    "AssigneeType",
    "TaskAssigner",
    "TaskCommand",
)
