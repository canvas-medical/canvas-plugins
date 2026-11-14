from __future__ import annotations

from datetime import datetime

from django.db.models import DateTimeField, Index, IntegerField, TextField

from canvas_sdk.v1.data.base import CustomModel


class ProbeRecord(CustomModel):
    """What one probe run saw, for the driver to check against the platform's run record.

    ``saw`` is the value the run read before it wrote: a ProbeAgent's counter for its
    scope, or a ChatProbeAgent's previous message. Two runs that read the same value on
    one scope overlapped, which the scope's lease should never allow.
    """

    run_id: TextField[str, str] = TextField()
    scenario: TextField[str, str] = TextField()
    kind: TextField[str, str] = TextField()
    scope_key: TextField[str, str] = TextField()
    seq: IntegerField[int, int] = IntegerField()
    saw: IntegerField[int, int] = IntegerField()
    started_at: DateTimeField[datetime, datetime] = DateTimeField()
    finished_at: DateTimeField[datetime, datetime] = DateTimeField()

    class Meta:
        indexes = [Index(fields=["scenario"]), Index(fields=["run_id"])]


class Counter(CustomModel):
    """A value per scope that each run reads and writes: runs completed, or the last
    chat message seen. Updates lost to overlapping runs leave it short.
    """

    key: TextField[str, str] = TextField()
    value: IntegerField[int, int] = IntegerField()

    class Meta:
        indexes = [Index(fields=["key"])]
