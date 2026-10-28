from __future__ import annotations

from django.db.models import DO_NOTHING, DateTimeField, ForeignKey, Index, JSONField

from agent_runner_poc.models.proxy import PatientProxy, StaffProxy
from canvas_sdk.v1.data.base import CustomModel


class Conversation(CustomModel):
    """A single ongoing chat conversation between a clinician and the ChartChatAgent.

    One row per patient and clinician — the conversation is scoped to the
    chart, not to a specific visit, and each clinician has their own, so one
    clinician's questions and drafts never become another's context.

    Storage shape: the entire conversation history lives in a single
    JSONField as a list of Anthropic-shaped message dicts (``{"role":
    "user|assistant", "content": "..."}`` — see the snapshot
    serialization in :class:`ConversationState`). This is the "snapshot
    state" pattern from doc §6.12: ``load_state`` reads the row,
    ``run()`` mutates the in-memory list, ``save_state`` writes it back.

    Like other CustomModels, ``flagged_at`` / ``last_updated_at`` are
    declared explicitly (CustomModel does not inherit TimestampedModel).
    """

    patient: ForeignKey[PatientProxy, PatientProxy] = ForeignKey(
        PatientProxy,
        to_field="dbid",
        on_delete=DO_NOTHING,
        related_name="chart_chat_conversations",
    )

    # The clinician whose conversation this is. Nullable so the column can be
    # added to an existing table; every row the agent writes sets it.
    staff: ForeignKey[StaffProxy, StaffProxy] = ForeignKey(
        StaffProxy,
        to_field="dbid",
        on_delete=DO_NOTHING,
        related_name="chart_chat_conversations",
        null=True,
    )

    # When the conversation was first created. Useful for "this thread was
    # started on..." UI affordances.
    started_at: DateTimeField[str, str] = DateTimeField(auto_now_add=True)

    # When the last turn was appended. Drives "recently active" sort orders.
    last_updated_at: DateTimeField[str, str] = DateTimeField(auto_now=True)

    # Serialized Anthropic-shaped message list. Each entry is at minimum
    # ``{"role": "user" | "assistant", "content": "..."}``. The agent's
    # ``run()`` appends turns and the snapshot is persisted back via
    # ``save_state``.
    messages: JSONField[list, list] = JSONField(default=list)

    class Meta:
        indexes = [
            Index(fields=["patient", "staff", "-last_updated_at"]),
        ]
