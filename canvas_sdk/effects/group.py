from typing import Any

from canvas_sdk.base import Model


class Group(Model):
    """
    Class representing a group of items.
    """

    items: list[Any]
    priority: int
    name: str

    def to_dict(self) -> dict[str, Any]:
        """Convert the Group object to a dictionary."""
        return {"items": self.items, "priority": self.priority, "name": self.name}


__exports__ = ("Group",)
