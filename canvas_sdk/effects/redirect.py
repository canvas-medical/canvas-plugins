from enum import StrEnum
from typing import Annotated, Any

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.effects import EffectType, _BaseEffect
from canvas_sdk.v1.data import Application


class RedirectEffect(_BaseEffect):
    """An Effect that navigates the Canvas frontend to a destination.

    Exactly one destination must be provided:

    * ``url`` — a full URL string the plugin composes in Python (it may include
      patient/note ids). Either an external URL (``https://...``) or an internal
      Canvas path (``/panel``, ``/patient/{key}?noteId=...``).
    * ``application_id`` — the identifier of a Canvas application to open.

    Every destination is validated on the server against the plugin's admin-managed
    redirect allowlist before the browser navigates; non-allowlisted destinations are
    blocked.
    """

    class Meta:
        effect_type = EffectType.REDIRECT

    class TargetType(StrEnum):
        SAME_TAB = "same_tab"
        NEW_TAB = "new_tab"

    url: Annotated[str, Field(min_length=1)] | None = None
    application_id: str | None = None
    target: TargetType = TargetType.SAME_TAB

    @property
    def values(self) -> dict[str, Any]:
        """The RedirectEffect values."""
        return {
            "url": self.url,
            "application_id": self.application_id,
            "target": self.target.value,
        }

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        provided = [field for field in (self.url, self.application_id) if field is not None]
        if len(provided) != 1:
            errors.append(
                self._create_error_detail(
                    "value",
                    "Exactly one of 'url' or 'application_id' must be provided",
                    None,
                )
            )

        if (
            self.application_id
            and not Application.objects.filter(identifier=self.application_id).exists()
        ):
            errors.append(
                self._create_error_detail(
                    "application_id",
                    f"Application with identifier {self.application_id} does not exist",
                    self.application_id,
                )
            )

        return errors


__exports__ = ("RedirectEffect",)
