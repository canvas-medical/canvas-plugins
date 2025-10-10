import json
from dataclasses import dataclass
from typing import Any

from canvas_generated.messages.effects_pb2 import Effect
from canvas_sdk.base import TrackableFieldsModel


@dataclass
class Metadata:
    """A class representing a metadata."""

    key: str
    value: str

    def to_dict(self) -> dict[str, Any]:
        """Convert the metadata to a dictionary."""
        return {"key": self.key, "value": self.value}


class BaseMetadata(TrackableFieldsModel):
    """Base class for metadata effects."""

    key: str

    def upsert(self, value: str) -> Effect:
        """Upsert the metadata."""
        self._validate_before_effect("upsert")

        return Effect(
            type=f"UPSERT_{self.Meta.effect_type}",  # type: ignore[attr-defined]
            payload=json.dumps(
                {
                    "data": {**self.values, "value": value},
                }
            ),
        )


__exports__ = ("Metadata",)
