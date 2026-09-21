from enum import StrEnum
from typing import Any

from pydantic import Field

from canvas_sdk.effects.base import EffectType, _BaseEffect


class PhoneDialSection(StrEnum):
    """A chart section whose phone numbers can be made clickable."""

    PATIENT = "patient"
    CONTACT = "contact"
    EXTERNAL_CARE_TEAM = "external_care_team"


class PhoneDialClickHandling(StrEnum):
    """What a click on a clickable phone number does."""

    # A tel: link, handled by whatever the device registers as its phone app.
    DEVICE = "device"
    # Nothing opens locally, leaving the PHONE_NUMBER_CLICKED event as the only outcome so
    # the plugin places the call.
    PLUGIN = "plugin"


class PhoneDialConfiguration(_BaseEffect):
    """An Effect that makes chart phone numbers clickable and says how a click is handled.

    Return this in response to the ``PHONE_DIAL__GET_CONFIGURATION`` event. Canvas ships no
    setting for click-to-dial, so a section no plugin lists keeps its phone numbers as plain
    text. Fax numbers are always plain text.

    One effect carries one ``click_handling`` covering every section it lists. To handle two
    sections differently, return one effect per handling.

    Under ``DEVICE`` handling a click opens a ``tel:`` link and the plugin is not involved.
    Under ``PLUGIN`` handling nothing opens locally; the click emits ``PHONE_NUMBER_CLICKED``
    and the handler decides what happens, whether that is placing the call through a
    softphone with a ``RedirectEffect`` or doing server-side work such as logging it.

    ``dial_label`` names the dial destination and chooses the affordance. A section with a
    label renders the number plus a button offering to dial that destination by name, which
    suits a plugin routing calls somewhere the number alone does not suggest. A section
    without one makes the number itself the link.

    Where several plugins respond, a section is clickable when any of them lists it, and it is
    plugin-driven when any of them asks for ``PLUGIN`` handling, since opening the device
    phone app alongside a plugin that places the call itself would dial twice. Among the
    rest, the first configuration naming a label supplies it. Clicking a clickable number
    emits ``PHONE_NUMBER_CLICKED`` under either handling.
    """

    class Meta:
        effect_type = EffectType.PHONE_DIAL__CONFIGURATION

    clickable_sections: list[PhoneDialSection] = Field(min_length=1)
    click_handling: PhoneDialClickHandling = PhoneDialClickHandling.DEVICE
    dial_label: str | None = None

    @property
    def values(self) -> dict[str, Any]:
        """The PhoneDialConfiguration's values."""
        return {
            "clickable_sections": [section.value for section in self.clickable_sections],
            "click_handling": self.click_handling.value,
            "dial_label": self.dial_label,
        }


__exports__ = (
    "PhoneDialClickHandling",
    "PhoneDialConfiguration",
    "PhoneDialSection",
)
