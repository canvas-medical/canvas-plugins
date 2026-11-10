from __future__ import annotations

from django.db.models import (
    DO_NOTHING,
    CharField,
    DateTimeField,
    ForeignKey,
    Index,
    JSONField,
    UniqueConstraint,
)

from canvas__agent_runner_poc.models.proxy import StaffProxy
from canvas_sdk.v1.data.base import CustomModel


class ClaimConversation(CustomModel):
    """One staff member's chat with the ClaimsChatAgent, about their claims work or one claim.

    Each staff member has one conversation about their work across the claims queues,
    with ``claim_id`` empty, and one per claim they open the chat from. Like the chart
    chat's :class:`Conversation`, the whole history is one JSON list of Anthropic-shaped
    messages, read by ``load_state`` and written back by ``save_state``.
    """

    staff: ForeignKey[StaffProxy, StaffProxy] = ForeignKey(
        StaffProxy,
        to_field="dbid",
        on_delete=DO_NOTHING,
        related_name="claim_conversations",
    )

    # The claim's id, or empty for the conversation about the claims queues.
    claim_id: CharField[str, str] = CharField(max_length=36, default="", blank=True)

    started_at: DateTimeField[str, str] = DateTimeField(auto_now_add=True)
    last_updated_at: DateTimeField[str, str] = DateTimeField(auto_now=True)
    messages: JSONField[list, list] = JSONField(default=list)

    class Meta:
        indexes = [
            Index(fields=["staff", "claim_id"]),
        ]
        # One conversation per staff member and claim, or about the queues.
        constraints = [
            UniqueConstraint(fields=["staff", "claim_id"], name="claim_conversation_staff_claim"),
        ]
