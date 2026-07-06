import re
from abc import abstractmethod
from enum import StrEnum
from functools import cached_property

from pydantic import ValidationError

from canvas_sdk.effects import Effect
from canvas_sdk.effects.action_button import ReloadNoteActionButtonsEffect
from canvas_sdk.effects.note import Appointment as AppointmentEffect
from canvas_sdk.effects.note import Note as NoteEffect
from canvas_sdk.effects.note.note import transition_matrix_for
from canvas_sdk.effects.show_button import ShowButtonEffect
from canvas_sdk.events import EventType
from canvas_sdk.handlers.base import BaseHandler
from canvas_sdk.v1.data import Appointment as AppointmentModel
from canvas_sdk.v1.data import Note
from canvas_sdk.v1.data.note import NoteStates

SHOW_BUTTON_REGEX = re.compile(r"^SHOW_(.+?)_BUTTON$")


class ActionButton(BaseHandler):
    """Base class for action buttons."""

    RESPONDS_TO = [
        EventType.Name(EventType.SHOW_NOTE_HEADER_BUTTON),
        EventType.Name(EventType.SHOW_NOTE_FOOTER_BUTTON),
        EventType.Name(EventType.SHOW_NOTE_BODY_BUTTON),
        EventType.Name(EventType.SHOW_NOTE_HEADER_DROPDOWN_BUTTON),
        EventType.Name(EventType.SHOW_CHART_PATIENT_HEADER_BUTTON),
        EventType.Name(EventType.SHOW_CHART_SUMMARY_SOCIAL_DETERMINANTS_SECTION_BUTTON),
        EventType.Name(EventType.SHOW_CHART_SUMMARY_GOALS_SECTION_BUTTON),
        EventType.Name(EventType.SHOW_CHART_SUMMARY_CONDITIONS_SECTION_BUTTON),
        EventType.Name(EventType.SHOW_CHART_SUMMARY_MEDICATIONS_SECTION_BUTTON),
        EventType.Name(EventType.SHOW_CHART_SUMMARY_ALLERGIES_SECTION_BUTTON),
        EventType.Name(EventType.SHOW_CHART_SUMMARY_CARE_TEAMS_SECTION_BUTTON),
        EventType.Name(EventType.SHOW_CHART_SUMMARY_VITALS_SECTION_BUTTON),
        EventType.Name(EventType.SHOW_CHART_SUMMARY_IMMUNIZATIONS_SECTION_BUTTON),
        EventType.Name(EventType.SHOW_CHART_SUMMARY_SURGICAL_HISTORY_SECTION_BUTTON),
        EventType.Name(EventType.SHOW_CHART_SUMMARY_FAMILY_HISTORY_SECTION_BUTTON),
        EventType.Name(EventType.SHOW_CHART_SUMMARY_CODING_GAPS_SECTION_BUTTON),
        EventType.Name(EventType.ACTION_BUTTON_CLICKED),
    ]

    class ButtonLocation(StrEnum):
        NOTE_HEADER = "note_header"
        NOTE_FOOTER = "note_footer"
        NOTE_BODY = "note_body"
        NOTE_HEADER_DROPDOWN = "note_header_dropdown"
        CHART_PATIENT_HEADER = "chart_patient_header"
        CHART_SUMMARY_SOCIAL_DETERMINANTS_SECTION = "chart_summary_social_determinants_section"
        CHART_SUMMARY_GOALS_SECTION = "chart_summary_goals_section"
        CHART_SUMMARY_CONDITIONS_SECTION = "chart_summary_conditions_section"
        CHART_SUMMARY_MEDICATIONS_SECTION = "chart_summary_medications_section"
        CHART_SUMMARY_ALLERGIES_SECTION = "chart_summary_allergies_section"
        CHART_SUMMARY_CARE_TEAMS_SECTION = "chart_summary_care_teams_section"
        CHART_SUMMARY_VITALS_SECTION = "chart_summary_vitals_section"
        CHART_SUMMARY_IMMUNIZATIONS_SECTION = "chart_summary_immunizations_section"
        CHART_SUMMARY_SURGICAL_HISTORY_SECTION = "chart_summary_surgical_history_section"
        CHART_SUMMARY_FAMILY_HISTORY_SECTION = "chart_summary_family_history_section"
        CHART_SUMMARY_CODING_GAPS_SECTION = "chart_summary_coding_gaps_section"

    BUTTON_TITLE: str = ""
    BUTTON_KEY: str = ""
    BUTTON_LOCATION: ButtonLocation
    PRIORITY: int = 0
    BUTTON_TEXT_COLOR: str | None = None
    BUTTON_BACKGROUND_COLOR: str | None = None

    @abstractmethod
    def handle(self) -> list[Effect]:
        """Method to handle button click."""
        raise NotImplementedError("Implement to handle button click")

    def visible(self) -> bool:
        """Method to determine button visibility."""
        return True

    def compute(self) -> list[Effect]:
        """Method to compute the effects."""
        if not self.BUTTON_LOCATION:
            return []

        show_button_event_match = SHOW_BUTTON_REGEX.fullmatch(self.event.name)

        if show_button_event_match:
            location = show_button_event_match.group(1)
            if self.ButtonLocation[location] == self.BUTTON_LOCATION and self.visible():
                return [
                    ShowButtonEffect(
                        key=self.BUTTON_KEY,
                        title=self.BUTTON_TITLE,
                        priority=self.PRIORITY,
                        color=self.BUTTON_TEXT_COLOR,
                        background=self.BUTTON_BACKGROUND_COLOR,
                    ).apply()
                ]
        elif self.context["key"] == self.BUTTON_KEY:
            return self.handle()

        return []


class NoteStateActionButton(ActionButton):
    """A note footer button that transitions a note into ``STATE_ACTION``.

    Shown only when that transition is allowed from the note's current state (per
    ``TRANSITION_STATE_MATRIX``).

    ``LOCKED`` and ``SIGNED`` are the same transition shown differently: a note type that
    requires a signature offers Sign, one that does not offers Lock. So a ``LOCKED``-target
    button is hidden for signature-required note types and a ``SIGNED``-target button is
    hidden for those that don't require one.
    """

    RESPONDS_TO = [
        EventType.Name(EventType.SHOW_NOTE_FOOTER_BUTTON),
        EventType.Name(EventType.ACTION_BUTTON_CLICKED),
    ]

    BUTTON_LOCATION = ActionButton.ButtonLocation.NOTE_FOOTER

    # The state this button transitions the note into.
    STATE_ACTION: NoteStates | None = None

    # Imperative labels for the supported target states.
    _DEFAULT_TITLES = {
        NoteStates.LOCKED: "Lock",
        NoteStates.UNLOCKED: "Unlock",
        NoteStates.SIGNED: "Sign",
        NoteStates.PUSHED: "Push charges",
        NoteStates.CONVERTED: "Check in",
        NoteStates.NOSHOW: "No show",
        NoteStates.DELETED: "Delete",
        NoteStates.UNDELETED: "Restore",
        NoteStates.DISCHARGED: "Discharge",
        NoteStates.CANCELLED: "Cancel",
        NoteStates.REVERTED: "Restore",
    }

    def __init_subclass__(cls, **kwargs: object) -> None:
        """Derive the button key and title from STATE_ACTION unless set explicitly."""
        super().__init_subclass__(**kwargs)
        if cls.STATE_ACTION:
            cls.BUTTON_KEY = cls.BUTTON_KEY or f"note_state_action__{cls.STATE_ACTION.value}"
            cls.BUTTON_TITLE = cls.BUTTON_TITLE or cls._DEFAULT_TITLES.get(
                cls.STATE_ACTION, cls.STATE_ACTION.label
            )

    @cached_property
    def _note_context(self) -> tuple[NoteStates, bool, str] | None:
        """The context note's (current state, is_sig_required, note type category), or None.

        Cached per handler instance so ``visible()`` and ``compute()`` share a single note
        query per button render.
        """
        note_id = self.context.get("note_id")
        if not note_id:
            return None
        note = Note.objects.filter(dbid=note_id).first()
        if not note:
            return None
        try:
            return (
                NoteStates(note.current_state.state),
                note.note_type_version.is_sig_required,
                note.note_type_version.category,
            )
        except Exception:  # noqa: BLE001
            return None

    def transition(self, note_id: str) -> list[Effect]:
        """Return the SDK effect(s) that transition ``note`` into ``STATE_ACTION``."""
        if not self.STATE_ACTION:
            raise ValueError("STATE_ACTION is required")
        effect = NoteEffect(instance_id=note_id)
        actions = {
            NoteStates.LOCKED: [effect.lock],
            NoteStates.UNLOCKED: [effect.unlock],
            NoteStates.SIGNED: [effect.lock, effect.sign],
            NoteStates.PUSHED: [effect.push_charges],
            NoteStates.CONVERTED: [effect.check_in],
            NoteStates.NOSHOW: [effect.no_show],
            NoteStates.DELETED: [effect.delete],
            NoteStates.UNDELETED: [effect.undelete],
            NoteStates.DISCHARGED: [effect.discharge],
        }
        action_effects = actions.get(self.STATE_ACTION)
        if action_effects:
            return [action_effect() for action_effect in action_effects]

        appointment_effects = self._appointment_transition(note_id)
        if appointment_effects:
            return appointment_effects
        raise ValueError(f"No transition for state {self.STATE_ACTION}")

    def _appointment_transition(self, note_id: str) -> list[Effect]:
        """Build the Appointment effect for an appointment-only transition (Cancel/Restore).

        Cancel and Restore act on the note's appointment, not the note, so they resolve the
        appointment id from the note id and emit an Appointment effect.
        """
        if self.STATE_ACTION not in (NoteStates.CANCELLED, NoteStates.REVERTED):
            return []
        appointment_id = (
            AppointmentModel.objects.filter(note__id=note_id).values_list("id", flat=True).first()
        )
        if not appointment_id:
            return []
        appointment = AppointmentEffect(instance_id=str(appointment_id))
        if self.STATE_ACTION == NoteStates.CANCELLED:
            return [appointment.cancel()]
        return [appointment.revert()]

    def visible(self) -> bool:
        """Show only when STATE_ACTION is a permitted transition from the current state.

        Lock and Sign are the same transition: Lock is hidden for signature-required note
        types and Sign for those that don't require one (see the class docstring).
        """
        if not self.STATE_ACTION:
            return False
        note_context = self._note_context
        if not note_context:
            return False
        current_state, is_sig_required, category = note_context
        if self.STATE_ACTION not in transition_matrix_for(category).get(current_state, []):
            return False
        if self.STATE_ACTION == NoteStates.LOCKED:
            return not is_sig_required
        if self.STATE_ACTION == NoteStates.SIGNED:
            return is_sig_required
        return True

    def compute(self) -> list[Effect]:
        """Order this button by its position in the current state's allowed transitions."""
        note_context = self._note_context
        if note_context:
            current_state, _is_sig_required, category = note_context
            matrix = transition_matrix_for(category)
            if self.STATE_ACTION in matrix.get(current_state, []):
                self.PRIORITY = matrix[current_state].index(self.STATE_ACTION)
        return super().compute()

    def handle(self) -> list[Effect]:
        """Apply the transition for STATE_ACTION and reload the footer buttons."""
        note_dbid = self.context.get("note_id")
        note_id = (
            Note.objects.filter(dbid=note_dbid).values_list("id", flat=True).first()
            if note_dbid
            else None
        )
        if not note_id:
            return []
        try:
            transition_effects = self.transition(str(note_id))
        except (ValueError, ValidationError):
            return []
        return [*transition_effects, ReloadNoteActionButtonsEffect(id=note_id).apply()]


__exports__ = (
    "SHOW_BUTTON_REGEX",
    "ActionButton",
    "NoteStateActionButton",
)
