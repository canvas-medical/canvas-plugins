from pydantic import BaseModel, ConfigDict

from plugin_runner.generated.messages.effects_pb2 import Effect


class _BaseEffect(BaseModel):
    """
    A Canvas Effect that changes user behavior or autonomously performs activities on behalf of users.
    """

    class Meta:
        effect_type = ""

    model_config = ConfigDict(strict=True, validate_assignment=True)

    @property
    def values(self) -> dict:
        return {}

    @property
    def effect_payload(self) -> dict:
        return {"data": self.values}

    def apply(self) -> Effect:
        return {
            "type": self.Meta.effect_type,
            "payload": self.effect_payload,
        }
