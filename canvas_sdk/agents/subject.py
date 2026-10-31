from dataclasses import dataclass


@dataclass(frozen=True)
class RunSubject:
    """What an agent run is about, as validated by the platform.

    Set on the agent as ``self.subject`` before any lifecycle hook fires. Each field
    comes from the :class:`RunAgentEffect`, checked by the platform: the patient
    exists, the note is that patient's, and the claim exists.

    Attributes:
        patient_id: The patient's ``Patient.id``, or None.
        note_id: The note's ``Note.id``, or None.
        claim_id: The claim's ``Claim.id``, or None.
    """

    patient_id: str | None = None
    note_id: str | None = None
    claim_id: str | None = None


@dataclass(frozen=True)
class RunRequester:
    """Who started an agent run, as the platform took it from the event.

    Set on the agent as ``self.requester``. It is never a field of the
    :class:`RunAgentEffect`, so a plugin cannot choose it.

    Attributes:
        staff_id: The ``Staff.id`` of the staff member whose action emitted the effect;
            None for a run a patient, a schedule, or a system event started.
        permissions: The staff member's platform permissions, such as
            ``"api.change_task"``; empty for a run a patient started. None when
            permissions do not limit the run: Canvas Bot is behind it, acting with the
            plugin's authority, or a superuser is. The platform hides tools that need a
            permission the requester lacks, and checks the requester's permissions
            again on every effect the run returns.
    """

    staff_id: str | None = None
    permissions: frozenset[str] | None = None


__exports__ = ("RunRequester", "RunSubject")
