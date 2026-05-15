from canvas_sdk.effects.metadata import BaseMetadata


class _CommandMetadata(BaseMetadata):
    """Effect to upsert a Command Metadata record."""

    class Meta:
        effect_type = "COMMAND_METADATA"

    command_id: str
    schema_key: str


__exports__ = ()
