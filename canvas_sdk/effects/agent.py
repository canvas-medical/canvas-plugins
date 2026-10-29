from enum import StrEnum
from typing import Annotated, Any, Self

from pydantic import Field, model_validator

from canvas_sdk.effects.base import EffectType, _BaseEffect

# The run subject's fields. They reach the agent as ``self.subject`` after the
# platform validates them, so they never travel in ``trigger_payload``.
SUBJECT_FIELDS = frozenset({"patient_id", "staff_id", "note_id"})


class RunAgentEffect(_BaseEffect):
    """Request that the platform invoke an :class:`AgentPlugin` in a worker.

    Plugin authors return this from a trigger handler's ``compute()`` to
    hand control off to the agent runtime. The platform validates the run's
    subject, derives its scope key, and runs the agent's
    ``load_state`` → ``run`` → ``save_state`` one run at a time per scope.

    Fields:
        agent_id: Class path of the :class:`AgentPlugin` subclass to instantiate,
            in ``module.path:ClassName`` form.
        scope: Which runs of this agent wait on each other; see :class:`Scope`.
            The platform derives the scope key from it and the run's subject.
        patient_id: The patient the run acts on. The platform checks that the
            patient exists, and a patient requesting a run may only name themselves.
        note_id: The note the run acts on. Requires ``patient_id``; the platform
            checks the note belongs to that patient.
        trigger_payload: Small dict of trigger-shaped data the agent needs in
            ``run``, such as a chat message. The subject's fields
            (``patient_id``, ``staff_id``, ``note_id``) are not allowed here.

    The staff member whose action started the run is never a field: the
    platform takes it from the event and sets it on ``self.subject.staff_id``.

    Example::

        return [RunAgentEffect(
            agent_id="my_plugin.agents.chart_summary:ChartSummary",
            scope=RunAgentEffect.Scope.PATIENT,
            patient_id=patient_id,
            note_id=note_id,
        ).apply()]
    """

    class Meta:
        effect_type = EffectType.RUN_AGENT

    class Scope(StrEnum):
        """Which runs of one agent wait on each other.

        Runs of different agents never wait on each other, whatever their scope.
        """

        # Runs on the same patient, one at a time.
        PATIENT = "patient"
        # Runs on the same patient started by the same staff member, one at a
        # time; a chat with one clinician about one patient.
        PATIENT_AND_STAFF = "patient_and_staff"
        # Runs on the same note, one at a time.
        NOTE = "note"
        # One run of this agent at a time on the instance.
        AGENT = "agent"

    agent_id: Annotated[str, Field(min_length=1)]
    scope: Scope
    patient_id: Annotated[str, Field(min_length=1)] | None = None
    note_id: Annotated[str, Field(min_length=1)] | None = None
    trigger_payload: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def check_subject(self) -> Self:
        """Require the subject fields the scope needs and keep them out of the payload."""
        if self.scope != self.Scope.AGENT and self.patient_id is None:
            raise ValueError(f"scope {self.scope.value!r} requires 'patient_id'")
        if self.scope == self.Scope.NOTE and self.note_id is None:
            raise ValueError("scope 'note' requires 'note_id'")
        if self.note_id is not None and self.patient_id is None:
            raise ValueError("'note_id' requires 'patient_id'")
        if subject_keys := sorted(SUBJECT_FIELDS & self.trigger_payload.keys()):
            raise ValueError(
                f"trigger_payload cannot carry {subject_keys}; the agent reads the run's "
                "subject from self.subject"
            )
        return self

    @property
    def values(self) -> dict[str, Any]:
        """Serialize the run-agent request into the effect payload."""
        return {
            "agent_id": self.agent_id,
            "scope": self.scope.value,
            "patient_id": self.patient_id,
            "note_id": self.note_id,
            "trigger_payload": self.trigger_payload,
        }


__exports__ = ("RunAgentEffect",)
