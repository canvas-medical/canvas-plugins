from enum import StrEnum
from typing import Annotated, Any

from pydantic import Field

from canvas_sdk.effects import EffectType, _BaseEffect


class RedirectEffect(_BaseEffect):
    """An Effect that navigates the Canvas frontend to a URL.

    The plugin composes the full target string in Python (it may include patient/note
    ids). The target can be an external URL (``https://...``) or an internal Canvas
    path (``/panel``, ``/patient/{key}?...``). Targets are validated against the
    plugin's manifest ``url_permissions`` allowlist on the server before the browser
    navigates; non-allowlisted targets are blocked.
    """

    class Meta:
        effect_type = EffectType.REDIRECT

    class TargetType(StrEnum):
        SAME_TAB = "same_tab"
        NEW_TAB = "new_tab"

    url: Annotated[str, Field(min_length=1)]
    target: TargetType = TargetType.SAME_TAB

    @property
    def values(self) -> dict[str, Any]:
        """The RedirectEffect values."""
        return {
            "url": self.url,
            "target": self.target.value,
        }


__exports__ = ("RedirectEffect",)
