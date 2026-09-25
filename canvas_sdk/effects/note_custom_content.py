from enum import StrEnum
from typing import Any, Self

from pydantic import model_validator

from canvas_sdk.effects.base import EffectType, _BaseEffect


class NoteCustomContent(_BaseEffect):
    """Custom content rendered inside a note.

    Return this in response to the ``NOTE__GET_CUSTOM_CONTENT`` event. A handler may return
    several, and everything returned for one section stacks in the order the handlers ran.

    ``section`` names a section the note renders. It is deliberately not a command's clinical
    note section: which commands a rendered section gathers is Canvas's to change, and a
    plugin should keep working when it does. Leaving it unset places the content at the top
    of the combined note view.
    """

    class Meta:
        effect_type = EffectType.NOTE__CUSTOM_CONTENT

    class Section(StrEnum):
        HISTORY = "history"
        EXAM = "exam"
        ASSESSMENT_PLAN = "assessment-plan"
        INTERNAL = "internal"

    section: Section | None = None
    url: str | None = None
    content: str | None = None

    @model_validator(mode="after")
    def check_mutually_exclusive_fields(self) -> Self:
        """Check that exactly one of url/content is provided."""
        if self.url is not None and self.content is not None:
            raise ValueError("'url' and 'content' are mutually exclusive")

        if self.url is None and self.content is None:
            raise ValueError("One of 'url' or 'content' must be provided")

        return self

    @property
    def values(self) -> dict[str, Any]:
        """The NoteCustomContent's values."""
        return {
            "section": self.section,
            "url": self.url,
            "content": self.content,
        }


__exports__ = ("NoteCustomContent",)
