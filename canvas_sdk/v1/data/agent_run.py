from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, Model


class AgentRunStatus(models.TextChoices):
    """Where an agent run stands."""

    QUEUED = "queued", "Queued"
    RUNNING = "running", "Running"
    SUCCEEDED = "succeeded", "Succeeded"
    FAILED = "failed", "Failed"
    REFUSED = "refused", "Refused"
    ABANDONED = "abandoned", "Abandoned"
    GAVE_UP = "gave_up", "Gave up"


class AgentRun(IdentifiableModel):
    """The platform's record of one agent run, kept for a limited time.

    ``id`` is the ``run_id`` of the :class:`RunAgentEffect` that started the run. The
    record holds no chart content: the run's subject is recorded by reference.
    """

    class Meta:
        db_table = "canvas_sdk_data_plugin_io_agentrun_001"

    plugin_name = models.TextField()
    agent_id = models.TextField()
    handler_name = models.TextField()
    scope = models.TextField()
    scope_key = models.TextField()
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, null=True, related_name="agent_runs"
    )
    staff = models.ForeignKey(
        "v1.Staff", on_delete=models.DO_NOTHING, null=True, related_name="agent_runs"
    )
    note = models.ForeignKey(
        "v1.Note", on_delete=models.DO_NOTHING, null=True, related_name="agent_runs"
    )
    status = models.TextField(choices=AgentRunStatus.choices)
    # Why a run failed or was refused: a structured kind, such as LLM_REFUSED, and a
    # short description.
    error_kind = models.TextField()
    error = models.TextField()
    queued_at = models.DateTimeField()
    started_at = models.DateTimeField(null=True)
    finished_at = models.DateTimeField(null=True)
    # How many times the run waited because another run held its scope or the
    # plugin-runner was busy.
    attempts = models.IntegerField()
    model_calls = models.IntegerField(null=True)
    stop_reason = models.TextField()
    effects_returned = models.IntegerField(null=True)
    effects_dropped = models.IntegerField(null=True)
    effects_applied = models.IntegerField(null=True)


class AgentRunToolCall(Model):
    """One tool call an agent run's tool loop dispatched. No arguments or results."""

    class Meta:
        db_table = "canvas_sdk_data_plugin_io_agentruntoolcall_001"

    run = models.ForeignKey(
        AgentRun,
        on_delete=models.DO_NOTHING,
        to_field="id",
        db_column="run_id",
        related_name="tool_calls",
    )
    seq = models.IntegerField()
    name = models.TextField()
    ok = models.BooleanField()
    error_type = models.TextField()
    duration_ms = models.IntegerField()


__exports__ = (
    "AgentRun",
    "AgentRunStatus",
    "AgentRunToolCall",
)
