from typing import Any

from pydantic import ConfigDict
from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType, _BaseEffect


class LoginEmailContent(_BaseEffect):
    """The portal login email, the answer to PATIENT_PORTAL__GET_LOGIN_EMAIL.

    A handler responds to that event and returns this effect. The event context
    carries ``link_type`` (``invite`` or ``reset``), the ``login_url`` to send,
    ``practice_location_id``, and the ``default_subject`` and ``default_body``.

    Canvas sends ``html_body`` as written, with no templating, so the handler must
    escape any patient data it puts in. When the body does not contain
    ``login_url``, raw or HTML-escaped, Canvas adds the link at the end.
    """

    class Meta:
        effect_type = EffectType.PATIENT_PORTAL__LOGIN_EMAIL_CONTENT

    # An unknown field is an error, so a misspelled field does not silently do nothing.
    model_config = ConfigDict(extra="forbid")

    subject: str
    html_body: str

    @property
    def values(self) -> dict[str, Any]:
        """The subject and the HTML body."""
        return {"subject": self.subject, "html_body": self.html_body}

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if not self.subject.strip():
            errors.append(
                self._create_error_detail("value", "subject must not be empty", self.subject)
            )
        # A line break ends the email header, so it would break or rewrite the message.
        if "\r" in self.subject or "\n" in self.subject:
            errors.append(
                self._create_error_detail(
                    "value", "subject must not contain a line break", self.subject
                )
            )
        if not self.html_body.strip():
            errors.append(
                self._create_error_detail("value", "html_body must not be empty", self.html_body)
            )

        return errors


__exports__ = ("LoginEmailContent",)
