from canvas_sdk.effects import Effect
from canvas_sdk.effects.agent import RunAgentEffect
from canvas_sdk.events import EventType
from canvas_sdk.handlers.base import BaseHandler
from canvas_sdk.v1.data.note import CurrentNoteStateEvent, NoteStates
from logger import log


class ChartSummaryTrigger(BaseHandler):
    """Fires the ChartSummary agent when a note transitions to LOCKED."""

    RESPONDS_TO: list[str] = [EventType.Name(EventType.NOTE_STATE_CHANGE_EVENT_CREATED)]

    def compute(self) -> list[Effect]:
        """Emit a RunAgentEffect when a note enters the NEW state."""
        log.info("Triggering ChartSummaryTrigger")
        if not self.is_new_note_event():
            return []

        note_id = self.context.get("note_id")
        patient_id = self.context.get("patient_id")
        if not (note_id and patient_id):
            log.info("ChartSummaryTrigger: missing note_id or patient_id in context; skipping")
            return []

        return [
            RunAgentEffect(
                agent_id="agent_runner_poc.agents.chart_summary:ChartSummary",
                scope_key=f"agent_runner_poc:chart_summary:patient:{patient_id}",
                trigger_payload={"patient_id": patient_id, "note_id": note_id},
            ).apply()
        ]

    def is_new_note_event(self) -> bool:
        """Return True if the current note-state event corresponds to NEW.

        The PoC originates a draft Plan command into the target note, which
        requires the note to be mutable. Locked/signed notes are immutable
        by clinical-integrity validation in canvas_core.commands.utils, so
        we fire on initial note creation instead.
        """
        return (
            CurrentNoteStateEvent.objects.values_list("state", flat=True).get(
                id=self.event.target.id
            )
            == NoteStates.NEW
        )
