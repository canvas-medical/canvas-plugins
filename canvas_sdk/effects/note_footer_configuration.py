from typing import Any

from canvas_sdk.effects.base import EffectType, _BaseEffect


class NoteFooterConfiguration(_BaseEffect):
    """An Effect that configures the note footer for the current note.

    Return this in response to the ``NOTE_FOOTER__GET_CONFIGURATION`` event to control the
    footer at the note level (rather than per button) — e.g. hide Canvas's default
    state-transition buttons when a plugin provides its own.
    """

    class Meta:
        effect_type = EffectType.NOTE_FOOTER__CONFIGURATION

    hide_default_state_buttons: bool = False

    @property
    def values(self) -> dict[str, Any]:
        """The NoteFooterConfiguration's values."""
        return {"hide_default_state_buttons": self.hide_default_state_buttons}


__exports__ = ("NoteFooterConfiguration",)
