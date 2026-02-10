import json
from typing import Any

from canvas_sdk.base import Model
from canvas_sdk.effects import Effect, EffectType
from logger import log


class _BaseEffect(Model):
    """
    A Canvas Effect that changes user behavior or autonomously performs activities on behalf of users.
    """

    patient_filter: dict | None = None

    class Meta:
        effect_type = EffectType.UNKNOWN_EFFECT

    @property
    def values(self) -> dict[str, Any]:
        return {}

    @property
    def effect_payload(self) -> dict[str, Any]:
        return {"data": self.values}

    def apply(self) -> Effect:
        log.info(f"[report_type] _BaseEffect.apply() called for {self.__class__.__name__}")
        log.info(f"[report_type] Effect type: {self.Meta.effect_type}")

        # Log source_protocol if it exists
        if hasattr(self, 'source_protocol'):
            log.info(f"[report_type] source_protocol before validation: {self.source_protocol!r}")

        self._validate_before_effect("apply")

        payload = self.effect_payload
        log.info(f"[report_type] effect_payload keys: {list(payload.keys()) if isinstance(payload, dict) else 'not a dict'}")
        log.info(f"[report_type] effect_payload: {payload}")

        # Log source_protocol in payload if it exists
        if isinstance(payload, dict):
            if 'source_protocol' in payload:
                log.info(f"[report_type] source_protocol in payload: {payload['source_protocol']!r}")
            else:
                log.warning("[report_type] source_protocol NOT in payload")

        payload_json = json.dumps(payload)
        log.info(f"[report_type] JSON payload length: {len(payload_json)}")

        effect = Effect(type=self.Meta.effect_type, payload=payload_json)
        log.info(f"[report_type] Created Effect object with type: {effect.type}")

        return effect


__exports__ = (
    "_BaseEffect",
    # Not defined here but used in a current plugin
    "EffectType",
)
