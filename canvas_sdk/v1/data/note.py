import hashlib
import json
import uuid
from typing import Any, Self, cast

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import FieldError
from django.db import models
from django.db.models.manager import BaseManager
from django.utils import timezone

from canvas_sdk.v1.data.base import (
    BaseQuerySet,
    IdentifiableModel,
    MetadataModel,
    TimestampedModel,
)
from canvas_sdk.v1.data.claim import Claim
from canvas_sdk.v1.data.coding import Coding
from canvas_sdk.v1.data.utils import empty_note_body


class NoteTypeCategories(models.TextChoices):
    """Note type categories."""

    MESSAGE = "message", "Message"
    LETTER = "letter", "Letter"
    INPATIENT = "inpatient", "Inpatient Visit Note"
    REVIEW = "review", "Chart Review Note"
    ENCOUNTER = "encounter", "Encounter Note"
    APPOINTMENT = "appointment", "Appointment Note"
    TASK = "task", "Task"
    DATA = "data", "Data"
    CCDA = "ccda", "C-CDA"
    SCHEDULE_EVENT = "schedule_event", "Schedule Event"


class PracticeLocationPOS(models.TextChoices):
    """Practice Location POS."""

    PHARMACY = "01", "Pharmacy"
    TELEHEALTH = "02", "Telehealth"
    SCHOOL = "03", "Education Facility"
    HOMELESS_SHELTER = "04", "Homeless Shelter"
    PRISON = "09", "Prison"
    TELEHEALTH_IN_PATIENT_HOME = "10", "Telehealth in Patient's Home"
    OFFICE = "11", "Office"
    HOME = "12", "Home"
    ASSISTED_LIVING = "13", "Asssisted Living Facility"
    GROUP_HOME = "14", "Group Home"
    MOBILE = "15", "Mobile Unit"
    WALK_IN_RETAIL = "17", "Walk-In Retail Health Clinic"
    OFF_CAMPUS_OUTPATIENT_HOSPITAL = "19", "Off-Campus Outpatient Hospital"
    URGENT_CARE = "20", "Urgent Care Facility"
    INPATIENT_HOSPITAL = "21", "Inpatient Hospital"
    ON_CAMPUS_OUTPATIENT_HOSPITAL = "22", "On-Campus Outpatient Hospital"
    ER_HOSPITAL = "23", "Emergency Room Hospital"
    AMBULATORY_SURGERY_CENTER = "24", "Ambulatory Surgery Center"
    BIRTHING_CENTER = "25", "Birthing Center"
    MILITARY_FACILITY = "26", "Military Treatment Facility"
    STREET = "27", "Outreach Site / Street"
    SNF = "31", "Skilled Nursing Facility"
    NURSING = "32", "Nursing Facility"
    CUSTODIAL = "33", "Custodial Care Facility"
    HOSPICE = "34", "Hospice"
    AMBULANCE_LAND = "41", "Ambulance Land"
    AMBULANCE_AIR_WATER = "42", "Ambulance Air or Water"
    INDEPENDENT_CLINIC = "49", "Independent Clinic"
    FQHC = "50", "Federally Qualified Health Center"
    PSYCH = "51", "Inpatient Psychiatric Facility"
    PSYCH_PARTIAL = "52", "Inpatient Psychiatric Facility - Partial Hospitalization"
    MENTAL_HEALTH_CENTER = "53", "Community Mental Health Center"
    INTERMEDIATE_MENTAL = "54", "Intermediate Care Facility for Mentally Retarded"
    SUBSTANCE_RESIDENTIAL = "55", "Residential Substance Abuse Treatment Facility"
    PSYCH_RESIDENTIAL = "56", "Psychiatric Residential Treatment Center"
    SUBSTANCE_NON_RESIDENTIAL = "57", "Non-Residential Substance Abuse Treatment Facility"
    MASS_IMMUNIZATION = "60", "Mass Immunization Center"
    INPATIENT_REHAB = "61", "Inpatient Rehabilitation Facility"
    OUTPATIENT_REHAB = "62", "Outpatient Rehabilitation Facility"
    ESRD = "65", "End-Stage Renal Disease Treatment Facility"
    PUBLIC_CLINIC = "71", "State or Local Public Health Clinic"
    RURAL_CLINIC = "72", "Rural Health Clinic"
    INDEPENDENT_LAB = "81", "Independent Laboratory"
    OTHER = "99", "Other Place of Service"


class NoteTypes(models.TextChoices):
    """Note types."""

    MESSAGE = "message", "Message"
    LETTER = "letter", "Letter"
    INPATIENT = "inpatient", "Inpatient Visit Note"
    REVIEW = "review", "Chart Review Note"
    VOICE = "voice", "Phone Call Note"
    VIDEO = "video", "Video Call Note"
    OFFICE = "office", "Office Visit Note"
    LAB = "lab", "Lab Visit Note"
    HOME = "home", "Home Visit Note"
    GROUP = "group", "Group Visit Note"
    APPOINTMENT = "appointment", "Appointment Note"
    OFFSITE = "offsite", "Other Offsite Visit Note"
    SEARCH = "search", "Search"
    TASK = "task", "Task"
    DATA = "data", "Data"
    CCDA = "ccda", "C-CDA Import"


class NoteStates(models.TextChoices):
    """Note states."""

    NEW = "NEW", "Created"
    PUSHED = "PSH", "Pushed the charges for"
    LOCKED = "LKD", "Locked"
    UNLOCKED = "ULK", "Unlocked"
    DELETED = "DLT", "Deleted"
    RELOCKED = "RLK", "Relocked"
    RESTORED = "RST", "Restored"
    RECALLED = "RCL", "Recalled"
    UNDELETED = "UND", "Undeleted"
    DISCHARGED = "DSC", "Discharged"
    SIGNED = "SGN", "Signed"
    # Appointment note
    SCHEDULING = "SCH", "Scheduling"
    BOOKED = "BKD", "Booked"
    CONVERTED = "CVD", "Checked in"
    CANCELLED = "CLD", "Canceled"
    NOSHOW = "NSW", "No show"
    REVERTED = "RVT", "Reverted"
    # C-CDA Import note
    CONFIRM_IMPORT = "CNF", "Confirmed"


class NoteType(TimestampedModel, IdentifiableModel, Coding):
    """NoteType."""

    objects: models.Manager["NoteType"]

    class Meta:
        db_table = "canvas_sdk_data_api_notetype_001"

    name = models.CharField(max_length=250)
    icon = models.CharField(max_length=250)
    category = models.CharField(choices=NoteTypeCategories.choices, max_length=50)
    rank = models.PositiveIntegerField(default=1)
    is_default_appointment_type = models.BooleanField(default=False)
    is_scheduleable = models.BooleanField(default=True)
    is_telehealth = models.BooleanField(default=False)
    is_billable = models.BooleanField(default=True)
    defer_place_of_service_to_practice_location = models.BooleanField(default=False)
    available_places_of_service = ArrayField(
        models.CharField(choices=PracticeLocationPOS.choices, max_length=5)
    )
    default_place_of_service = models.CharField(choices=PracticeLocationPOS.choices, max_length=5)
    is_system_managed = models.BooleanField(default=False, editable=False)
    is_visible = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    unique_identifier = models.UUIDField(default=uuid.uuid4, editable=False)
    deprecated_at = models.DateTimeField(null=True, editable=False)
    is_patient_required = models.BooleanField(default=False)
    allow_custom_title = models.BooleanField(default=False)
    is_scheduleable_via_patient_portal = models.BooleanField(default=False)
    online_duration = models.IntegerField(default=0)
    is_sig_required = models.BooleanField(default=True)


# The fields holding the body content. Version 1 notes store the body in
# `_body`; version 2 notes store it across `_body_content` and `_body_order`.
NOTE_BODY_FIELDS = ("_body", "_body_content", "_body_order")

# Everything the `body` property reads. It consults `_version` first to decide
# which shape to build, so a query loading `body` has to load that too.
NOTE_BODY_READ_FIELDS = (*NOTE_BODY_FIELDS, "_version")


# The column holding the body for a note's version, exposed to filters as
# `body`.
NOTE_BODY_COLUMN = models.Case(
    models.When(_version=2, then=models.F("_body_content")),
    default=models.F("_body"),
)


def _expand_body(fields: tuple[Any, ...], replacement: tuple[str, ...]) -> tuple[Any, ...]:
    """Replace `body` with the given fields, leaving the rest as-is."""
    expanded: list[Any] = []
    for field in fields:
        if field == "body":
            expanded.extend(replacement)
        else:
            expanded.append(field)
    return tuple(expanded)


def _is_body_lookup(name: Any) -> bool:
    """Whether a lookup name targets `body`."""
    return name == "body" or (isinstance(name, str) and name.startswith("body__"))


def _references_body(condition: models.Q) -> bool:
    """Whether a Q object looks up `body` at any depth."""
    for child in condition.children:
        if isinstance(child, models.Q):
            if _references_body(child):
                return True
        elif isinstance(child, tuple) and _is_body_lookup(child[0]):
            return True
    return False


def _reject_body_selection(fields: tuple[Any, ...], method: str) -> None:
    """Refuse to select `body`, which no single column holds.

    Django's own message for an unselectable alias suggests promoting it with
    `annotate`, which here would hand back the stored column instead of the
    body: for a version 2 note that is a mapping keyed by line, not the ordered
    list of lines that `body` returns.
    """
    if "body" in fields:
        raise FieldError(
            f"'body' cannot be selected with {method}(), because it is built from "
            "several columns rather than stored in one. Use only('body') to load "
            "notes whose 'body' is populated."
        )


class NoteQuerySet(BaseQuerySet):
    """A queryset for notes."""

    def _alias_body_if_referenced(self, args: tuple[Any, ...], kwargs: dict[str, Any]) -> Self:
        """Make `body` resolvable, but only for calls that look it up.

        The alias is added per call rather than to every note queryset so that
        queries not mentioning `body` are left exactly as they were written.
        """
        references_body = any(_is_body_lookup(key) for key in kwargs) or any(
            isinstance(arg, models.Q) and _references_body(arg) for arg in args
        )
        return self.alias(body=NOTE_BODY_COLUMN) if references_body else self

    def filter(self, *args: Any, **kwargs: Any) -> Self:
        """Filter the queryset, resolving `body` to the note's body column.

        `body` is a property rather than a field, so it is supplied as a query
        alias here. That covers `filter`, `exclude` and `get`, including lookups
        nested inside `Q` objects, but not `order_by`, `values`, or traversal
        from another model's queryset.
        """
        return super(NoteQuerySet, self._alias_body_if_referenced(args, kwargs)).filter(
            *args, **kwargs
        )

    def exclude(self, *args: Any, **kwargs: Any) -> Self:
        """Exclude matching rows, resolving `body` to the note's body column."""
        return super(NoteQuerySet, self._alias_body_if_referenced(args, kwargs)).exclude(
            *args, **kwargs
        )

    def defer(self, *fields: Any) -> Self:
        """Defer loading of the named fields.

        `body` is a property derived from three columns, so naming it defers all
        of them.
        """
        return super().defer(*_expand_body(fields, NOTE_BODY_FIELDS))

    def only(self, *fields: Any) -> Self:
        """Load only the named fields, deferring the rest.

        `body` expands to every field the property reads, so that building a
        body from the result costs no further queries.
        """
        return super().only(*_expand_body(fields, NOTE_BODY_READ_FIELDS))

    def values(self, *fields: Any, **expressions: Any) -> models.QuerySet[Any, dict[str, Any]]:
        """Return dictionaries of field values, refusing to select `body`."""
        _reject_body_selection(fields, "values")
        return super().values(*fields, **expressions)

    def values_list(
        self, *fields: Any, flat: bool = False, named: bool = False
    ) -> models.QuerySet[Any, Any]:
        """Return tuples of field values, refusing to select `body`."""
        _reject_body_selection(fields, "values_list")
        return super().values_list(*fields, flat=flat, named=named)


NoteManager = BaseManager.from_queryset(NoteQuerySet)


class Note(TimestampedModel, IdentifiableModel):
    """Note."""

    class Meta:
        db_table = "canvas_sdk_data_api_note_001"

    objects = cast(NoteQuerySet, NoteManager())

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="notes", null=True
    )
    provider = models.ForeignKey(
        "v1.Staff", on_delete=models.DO_NOTHING, related_name="notes", null=True
    )
    supervising_provider = models.ForeignKey(
        "v1.Staff", on_delete=models.DO_NOTHING, related_name="supervised_notes", null=True
    )
    note_type = models.CharField(choices=NoteTypes.choices, null=True, max_length=50)
    note_type_version = models.ForeignKey(
        "v1.NoteType", on_delete=models.DO_NOTHING, related_name="notes"
    )
    title = models.TextField(default="", blank=True)
    originator = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, null=True)
    last_modified_by_staff = models.ForeignKey("v1.Staff", on_delete=models.DO_NOTHING, null=True)
    checksum = models.CharField(max_length=32)
    billing_note = models.TextField()
    # TODO -implement InpatientStay model
    # inpatient_stay = models.ForeignKey("v1.InpatientStay", on_delete=models.DO_NOTHING, null=True)
    related_data = models.JSONField(default=dict, blank=True)
    location = models.ForeignKey("v1.PracticeLocation", on_delete=models.DO_NOTHING, null=True)
    datetime_of_service = models.DateTimeField(default=timezone.now)
    place_of_service = models.CharField(max_length=255)

    # properties that shouldn't be directly exposed in the API
    # but are needed for legacy note handling and other internal logic
    _body = models.JSONField(default=empty_note_body, db_column="body")
    _body_content = models.JSONField(default=dict, db_column="body_content")
    _body_order = ArrayField(models.UUIDField(), default=[], blank=True, db_column="body_order")
    _version = models.IntegerField(null=True, db_column="version")

    @property
    def body(self) -> list[dict]:
        """Return the note body content, handling any necessary transformations for v2 notes."""
        if self._version == 2:
            # For version 2 notes, we need to reconstruct the body using the content and order fields
            legacy_body: list[dict] = []
            for line_uuid in self._body_order:
                line_uuid_str = str(line_uuid)
                line = self._body_content.get(line_uuid_str)

                if line is None:
                    legacy_body.append({"type": "text", "value": ""})
                elif line.get("type") == "command":
                    legacy_body.append({"type": "command", "value": line["value"]})
                else:
                    legacy_body.append({"type": "text", "value": line.get("value", "")})
            return legacy_body
        else:
            # for legacy notes we can return the body directly, as it is already in the expected format
            return self._body

    def body_checksum(self) -> str:
        """Compute an MD5 checksum of the note body content only."""
        return hashlib.md5(json.dumps(self.body, sort_keys=True).encode("utf-8")).hexdigest()

    def get_claim(self) -> Claim | None:
        """
        Get the most recent claim for this note.
        Returns the latest claim ordered by created date, or None if no claims exist.
        """
        return self.claims.order_by("-created").first()


class NoteStateChangeEvent(TimestampedModel, IdentifiableModel):
    """NoteStateChangeEvent."""

    class Meta:
        ordering = ("created", "id")
        db_table = "canvas_sdk_data_api_notestatechangeevent_001"

    note = models.ForeignKey("v1.Note", on_delete=models.DO_NOTHING, related_name="state_history")
    originator = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, null=True)
    state = models.CharField(choices=NoteStates.choices, max_length=3)
    note_state_document = models.CharField(max_length=100, null=True)
    note_state_html = models.TextField()


class CurrentNoteStateEvent(IdentifiableModel):
    """
    CurrentNoteStateEvent is a special model backed by a view which only includes the latest
    NoteStateChangeEvent for any given note_id.
    """

    class Meta:
        db_table = "canvas_sdk_data_current_note_state_001"

    state = models.CharField(choices=NoteStates.choices, max_length=3)
    note = models.OneToOneField(
        "v1.Note", on_delete=models.DO_NOTHING, related_name="current_state"
    )

    def editable(self) -> bool:
        """Returns a boolean to indicate if the related note can be edited."""
        return self.state in [
            NoteStates.NEW,
            NoteStates.CONVERTED,
            NoteStates.PUSHED,
            NoteStates.UNLOCKED,
            NoteStates.RESTORED,
            NoteStates.UNDELETED,
        ]


class NoteMetadata(MetadataModel):
    """A class representing Note Metadata."""

    class Meta:
        db_table = "canvas_sdk_data_api_notemetadata_001"

    note = models.ForeignKey(
        "v1.Note", on_delete=models.CASCADE, related_name="metadata", null=True
    )


__exports__ = (
    "NoteTypeCategories",
    "PracticeLocationPOS",
    "NoteTypes",
    "NoteType",
    "Note",
    "NoteMetadata",
    "NoteStates",
    "NoteStateChangeEvent",
    "CurrentNoteStateEvent",
)
