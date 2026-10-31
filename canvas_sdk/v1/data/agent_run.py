from django.contrib.postgres.fields import ArrayField
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
    record holds no chart content: the run's patient and requester are recorded by
    reference here, and the rest of its subject as :class:`AgentRunSubject` rows.
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
    # The capabilities the platform granted the run, such as "revenue".
    capabilities = ArrayField(models.TextField())
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


class AgentRunSubject(Model):
    """One part of an agent run's subject other than its patient, such as its note or claim.

    ``kind`` names the part (``"note"``, ``"claim"``) and ``ref_id`` is the ``id`` of
    the record it names, as the :class:`RunAgentEffect` carried it.
    """

    class Meta:
        db_table = "canvas_sdk_data_plugin_io_agentrunsubject_001"

    run = models.ForeignKey(
        AgentRun,
        on_delete=models.DO_NOTHING,
        to_field="id",
        db_column="run_id",
        related_name="subjects",
    )
    kind = models.TextField()
    ref_id = models.TextField()


class AgentRunProposalStatus(models.TextChoices):
    """Where a proposal stands. A pending proposal past its expiry reads as expired."""

    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    DENIED = "denied", "Denied"
    FAILED = "failed", "Failed"
    EXPIRED = "expired", "Expired"


class AgentRunProposal(IdentifiableModel):
    """A change an agent proposed for its requester to approve, held by the platform.

    An agent whose manifest lists a tool under ``tools.approve`` proposes that tool's
    changes. ``id`` is what :class:`canvas_sdk.effects.agent.DecideAgentProposal` takes.
    ``tool`` and ``arguments`` are the tool the model called and what it passed, for a
    plugin's approval card; ``effect_type`` names the change that applies on approval.
    """

    class Meta:
        db_table = "canvas_sdk_data_plugin_io_agentrunproposal_001"

    run = models.ForeignKey(
        AgentRun,
        on_delete=models.DO_NOTHING,
        to_field="id",
        db_column="run_id",
        related_name="proposals",
    )
    plugin_name = models.TextField()
    agent_id = models.TextField()
    tool = models.TextField()
    arguments = models.JSONField()
    effect_type = models.TextField()
    # The staff member the agent acted for, the only one who may decide.
    staff = models.ForeignKey(
        "v1.Staff", on_delete=models.DO_NOTHING, null=True, related_name="agent_run_proposals"
    )
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, null=True, related_name="agent_run_proposals"
    )
    status = models.TextField(choices=AgentRunProposalStatus.choices)
    created_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    decided_at = models.DateTimeField(null=True)
    # The user's reason for a denial, or why an approved change failed to apply.
    reason = models.TextField()


__exports__ = (
    "AgentRun",
    "AgentRunProposal",
    "AgentRunProposalStatus",
    "AgentRunStatus",
    "AgentRunSubject",
    "AgentRunToolCall",
)
