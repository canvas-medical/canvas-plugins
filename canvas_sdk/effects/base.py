from pydantic import BaseModel, ConfigDict

from canvas_sdk.effects.constants import Effect


class _BaseEffect(BaseModel):
    """
    A Canvas Effect that changes user behavior or autonomously performs activities on behalf of users.
    """

    class Meta:
        effect_type = ""

    model_config = ConfigDict(strict=True, validate_assignment=True)

    patient_key: str

    @property
    def values(self) -> dict:
        return {}

    def manifest(self) -> Effect:
        return {
            "effect_type": self.Meta.effect_type,
            "payload": {"patient": self.patient_key, "data": self.values},
        }
