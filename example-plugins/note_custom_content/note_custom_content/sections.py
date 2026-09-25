"""What each rendered section of the note holds, and what a button adds to it.

Canvas decides which commands a section gathers, and a plugin has no way to ask, so the
mapping is declared here. It mirrors the `noteSection` each command type carries.
"""

from canvas_sdk.commands import MedicalHistoryCommand, PlanCommand, VitalsCommand
from canvas_sdk.effects.note_custom_content import NoteCustomContent
from canvas_sdk.v1.data.command import Command

SCHEMA_KEYS = {
    NoteCustomContent.Section.HISTORY: frozenset(
        {
            "allergy",
            "approveChange",
            "chartSectionReview",
            "denyChange",
            "familyHistory",
            "hpi",
            "immunizationStatement",
            "medicalHistory",
            "medicationStatement",
            "questionnaire",
            "reasonForVisit",
            "removeAllergy",
            "ros",
            "surgicalHistory",
        }
    ),
    NoteCustomContent.Section.EXAM: frozenset({"exam", "visualExamFinding", "vitals"}),
    NoteCustomContent.Section.ASSESSMENT_PLAN: frozenset(
        {
            "adjustPrescription",
            "adjustProtocol",
            "approveRefill",
            "assess",
            "closeGoal",
            "denyRefill",
            "diagnose",
            "educationalMaterial",
            "followUp",
            "goal",
            "imagingOrder",
            "imagingReview",
            "immunize",
            "instruct",
            "labOrder",
            "labReview",
            "perform",
            "plan",
            "pocLabTest",
            "prescribe",
            "refer",
            "reference",
            "referralReview",
            "refill",
            "resolveCondition",
            "snoozeProtocol",
            "stopMedication",
            "structuredAssessment",
            "task",
            "uncategorizedDocumentReview",
            "updateDiagnosis",
            "updateGoal",
        }
    ),
    NoteCustomContent.Section.INTERNAL: frozenset(
        {
            "assessCodingGap",
            "cancelPrescription",
            "changeMedication",
            "clipboard",
            "createCodingGap",
            "deferCodingGap",
            "privateNotes",
            "validateCodingGap",
        }
    ),
}

LABELS = {
    NoteCustomContent.Section.HISTORY: "History",
    NoteCustomContent.Section.EXAM: "Exam",
    NoteCustomContent.Section.ASSESSMENT_PLAN: "Assessment & Plan",
    NoteCustomContent.Section.INTERNAL: "Internal",
}

ADDS = {
    NoteCustomContent.Section.HISTORY: MedicalHistoryCommand,
    NoteCustomContent.Section.EXAM: VitalsCommand,
    NoteCustomContent.Section.ASSESSMENT_PLAN: PlanCommand,
}

ADD_LABELS = {
    NoteCustomContent.Section.HISTORY: "Medical History",
    NoteCustomContent.Section.EXAM: "Vitals",
    NoteCustomContent.Section.ASSESSMENT_PLAN: "Plan",
}


def section_for(value: str) -> NoteCustomContent.Section | None:
    """The section a request named, or nothing where it named none Canvas renders."""
    for section in NoteCustomContent.Section:
        if section.value == value:
            return section

    return None


COUNTED_STATES = ("staged", "committed")


def channel_for(note_id: str) -> str:
    """The socket every copy of one note listens on."""
    return f"note-{note_id}"


def counts_for(note_id: str) -> dict[str, int]:
    """How many of a note's commands each section holds, plus the note's total.

    Keyed by the section's wire value so the number lands in the browser ready to use.
    """
    schema_keys = list(
        Command.objects.filter(note__id=note_id, state__in=COUNTED_STATES).values_list(
            "schema_key", flat=True
        )
    )

    counts = {
        section.value: sum(1 for key in schema_keys if key in keys)
        for section, keys in SCHEMA_KEYS.items()
    }
    counts["total"] = len(schema_keys)

    return counts
