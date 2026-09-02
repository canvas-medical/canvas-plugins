from enum import Enum
from typing import Any

from canvas_sdk.base import Model
from canvas_sdk.effects.base import EffectType, _BaseEffect


class AssigneeType(Enum):
    """The kind of assignee shown in the note header dropdown."""

    STAFF = "staff"
    TEAM = "team"


class AssigneeOption(Model):
    """A single staff member or team in the note header assignee dropdown."""

    id: str
    type: AssigneeType


class NoteHeaderAssigneeOptions(_BaseEffect):
    """
    An Effect that decides which staff and teams appear, and in what order, in the note
    header assignee dropdown. Options are shown in the given order; any staff or team
    omitted from the list is hidden. The "Unassigned" options remain available.
    """

    class Meta:
        effect_type = EffectType.PATIENT_NOTE_HEADER_ASSIGNEE__POST_SEARCH_RESULTS

    options: list[AssigneeOption]

    @property
    def values(self) -> dict[str, Any]:
        """The NoteHeaderAssigneeOptions's values."""
        return {
            "options": [{"id": option.id, "type": option.type.value} for option in self.options]
        }


__exports__ = ("AssigneeOption", "AssigneeType", "NoteHeaderAssigneeOptions")
