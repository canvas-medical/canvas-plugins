from typing import Any

from pydantic import Field

from canvas_sdk.effects.base import _BaseEffect


class _SurfaceEntryEffect(_BaseEffect):
    """An Effect that puts one plugin entry in a Canvas surface's list.

    Every surface needs the same three things to show an entry and to tell Canvas
    which one the user picked. A surface adds whatever else it renders.
    """

    key: str = Field(min_length=1)
    title: str = Field(min_length=1)
    priority: int = Field(default=0)

    @property
    def values(self) -> dict[str, Any]:
        """The values every surface entry carries."""
        return {"key": self.key, "title": self.title, "priority": self.priority}


__exports__ = ("_SurfaceEntryEffect",)
