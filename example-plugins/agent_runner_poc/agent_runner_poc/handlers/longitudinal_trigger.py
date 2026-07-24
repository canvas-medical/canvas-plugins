from canvas_sdk.effects import Effect
from canvas_sdk.effects.agent import RunAgentEffect
from canvas_sdk.events import EventType
from canvas_sdk.handlers.base import BaseHandler
from canvas_sdk.v1.data.note import CurrentNoteStateEvent, NoteStates
from logger import log


class LongitudinalCareAdvisorTrigger(BaseHandler):
    """Fires the LongitudinalCareAdvisor when a note transitions to LOCKED.

    LOCKED is the right trigger for the longitudinal advisor (and was wrong for
    ChartSummary) because the advisor reviews a *completed* encounter against
    prior visits' open protocol cards and surfaces follow-up via new cards —
    none of which require originating commands onto the locked note itself.
    """

    RESPONDS_TO: list[str] = [EventType.Name(EventType.NOTE_STATE_CHANGE_EVENT_CREATED)]

    def compute(self) -> list[Effect]:
        """Emit a RunAgentEffect when the trigger note has just been locked."""
        log.info("Triggering LongitudinalCareAdvisorTrigger")
        if not self.is_locked_note_event():
            return []

        note_id = self.context.get("note_id")
        patient_id = self.context.get("patient_id")
        if not (note_id and patient_id):
            log.info(
                "LongitudinalCareAdvisorTrigger: missing note_id or patient_id in context; skipping"
            )
            return []

        return [
            RunAgentEffect(
                agent_id="agent_runner_poc.agents.longitudinal_advisor:LongitudinalCareAdvisor",
                # Patient-scoped, not encounter-scoped — the advisor's whole
                # value is continuity across visits.
                scope_key=f"agent_runner_poc:longitudinal_advisor:patient:{patient_id}",
                trigger_payload={"patient_id": patient_id, "note_id": note_id},
            ).apply()
        ]

    def is_locked_note_event(self) -> bool:
        """Return True if the current note-state event corresponds to LOCKED."""
        return (
            CurrentNoteStateEvent.objects.values_list("state", flat=True).get(
                id=self.event.target.id
            )
            == NoteStates.LOCKED
        )
