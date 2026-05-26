from typing import Any

from canvas_sdk.effects.base import EffectType, _BaseEffect


class _CommandCustomHtml(_BaseEffect):
    """Effect to set the custom_html field on a staged command."""

    class Meta:
        effect_type = EffectType.SET_COMMAND_CUSTOM_HTML

    command_id: str
    custom_html: str | None

    @property
    def values(self) -> dict[str, Any]:
        return {
            "command_id": self.command_id,
            "custom_html": self.custom_html,
        }


__exports__ = ()
