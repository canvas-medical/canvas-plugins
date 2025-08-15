from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel
from canvas_sdk.v1.data.protocol_result import ProtocolResult


class ProtocolCurrent(ProtocolResult, IdentifiableModel):
    """ProtocolCurrent."""

    class Meta:
        db_table = "canvas_sdk_data_api_protocolcurrent_001"

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="protocol_currents"
    )
    result_hash = models.CharField(max_length=32, default="")
    snooze_date = models.DateField(null=True)


__exports__ = (
    "ProtocolCurrent",
    "ProtocolCurrentStatus",
)
