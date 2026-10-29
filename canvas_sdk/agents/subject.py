from dataclasses import dataclass


@dataclass(frozen=True)
class RunSubject:
    """Who and what an agent run is about, as validated by the platform.

    Set on the agent as ``self.subject`` before any lifecycle hook fires.
    ``patient_id`` and ``note_id`` come from the :class:`RunAgentEffect`,
    checked by the platform (the patient exists, the note is that patient's).
    ``staff_id`` is the staff member whose action emitted the effect; a run
    started by a patient, a schedule, or a system event has none.

    Attributes:
        patient_id: The patient's ``Patient.id``, or None.
        staff_id: The requesting staff member's ``Staff.id``, or None.
        note_id: The note's ``Note.id``, or None.
    """

    patient_id: str | None = None
    staff_id: str | None = None
    note_id: str | None = None


__exports__ = ("RunSubject",)
