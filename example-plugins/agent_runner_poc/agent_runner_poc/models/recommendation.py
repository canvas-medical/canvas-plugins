from __future__ import annotations

from django.db.models import (
    DO_NOTHING,
    DateTimeField,
    ForeignKey,
    Index,
    JSONField,
    TextField,
)

from agent_runner_poc.models.proxy import PatientProxy
from canvas_sdk.v1.data.base import CustomModel


class Recommendation(CustomModel):
    """A single longitudinal-advisor recommendation tracked across encounters.

    The LongitudinalCareAdvisor agent emits one record per recommendation it
    surfaces (paired with a Task effect that the clinician sees). On each
    subsequent run, the agent checks whether the recommendation's proxy fired —
    the Task being marked complete, a matching lab being ordered, etc. — and
    flips ``status`` to ``"addressed"`` if so. Open recommendations resurface
    in the agent's reasoning until they're addressed or marked ``"stale"``.

    Note: CustomModel does NOT inherit from TimestampedModel, so the
    timestamp fields are declared explicitly. ``auto_now_add`` /
    ``auto_now`` are Python-side defaults (Django populates them at
    ``.save()`` time); they don't translate into SQL DEFAULT clauses (the
    DDL pipeline strips defaults) but every write goes through the ORM so
    this is fine.

    Status lifecycle: ``"open"`` → ``"addressed"`` (proxy fired) | ``"stale"``
    (timed out without action).

    Category values (kept loose / unconstrained on purpose; the proxy verifier
    matches on the string):

    - ``"task"`` — proxy is the emitted Task's completion state, identified by
      a client-generated UUID stored in ``proxy_data["task_id"]``.
    - ``"follow_up_lab"`` — proxy is a matching LabValue with
      ``codings.code == proxy_data["loinc"]`` from a report dated after
      ``flagged_at``.
    - ``"none"`` — no machine-verifiable proxy (e.g. "keep taking tylenol").
      Resurfaces until the clinician explicitly addresses it via the Task.
    """

    patient: ForeignKey[PatientProxy, PatientProxy] = ForeignKey(
        PatientProxy,
        to_field="dbid",
        on_delete=DO_NOTHING,
        related_name="recommendations",
    )

    # When the agent emitted this recommendation. Used as the lower bound for
    # proxy verifiers (e.g. "any matching lab order *after* flagged_at").
    flagged_at: DateTimeField[str, str] = DateTimeField(auto_now_add=True)

    # When the status was last changed. Useful for "recently addressed" tail
    # in the agent's context preamble.
    status_updated_at: DateTimeField[str, str] = DateTimeField(auto_now=True)

    # The narrative the agent surfaced to the clinician (also the body of the
    # paired Task). Plain text.
    narrative: TextField[str, str] = TextField()

    # Recommendation category — drives which proxy verifier runs on subsequent
    # invocations. See class docstring for the supported values.
    category: TextField[str, str] = TextField()

    # Category-specific identifying fields. For ``"task"``:
    # ``{"task_id": "<uuid>"}``. For ``"follow_up_lab"``: ``{"loinc": "..."}``.
    proxy_data: JSONField[dict, dict] = JSONField(default=dict)

    # Lifecycle. Updated in place by the verifier.
    status: TextField[str, str] = TextField(default="open")
    status_reason: TextField[str, str] = TextField(blank=True, default="")

    class Meta:
        indexes = [
            # Resurface open recs for a patient in flagged-at order.
            Index(fields=["patient", "status", "-flagged_at"]),
        ]
