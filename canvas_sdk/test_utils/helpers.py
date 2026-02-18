"""Test helpers for CQM protocol tests."""

import json
import uuid
from datetime import date, datetime
from typing import Any, TypeVar
from unittest.mock import Mock

import arrow
from django.utils import timezone

from canvas_sdk.effects import EffectType
from canvas_sdk.protocols.clinical_quality_measure import ClinicalQualityMeasure
from canvas_sdk.protocols.timeframe import Timeframe
from canvas_sdk.test_utils.factories import (
    ConditionCodingFactory,
    ConditionFactory,
    LabReportFactory,
    LabValueCodingFactory,
    LabValueFactory,
    MedicationCodingFactory,
    MedicationFactory,
    NoteFactory,
    ObservationFactory,
    ObservationValueCodingFactory,
)
from canvas_sdk.v1.data import NoteType
from canvas_sdk.v1.data.condition import Condition
from canvas_sdk.v1.data.lab import LabReport
from canvas_sdk.v1.data.medication import Medication
from canvas_sdk.v1.data.note import NoteTypeCategories, PracticeLocationPOS
from canvas_sdk.v1.data.observation import Observation
from canvas_sdk.v1.data.patient import Patient

_CQM = TypeVar("_CQM", bound=ClinicalQualityMeasure)

SNOMED_CT_SYSTEM = "http://snomed.info/sct"
ICD10_CM_SYSTEM = "http://hl7.org/fhir/sid/icd-10-cm"
RXNORM_SYSTEM = "http://www.nlm.nih.gov/research/umls/rxnorm"
LOINC_SYSTEM = "http://loinc.org"

CODE_SYSTEM_MAP = {
    "SNOMEDCT": SNOMED_CT_SYSTEM,
    "ICD10CM": ICD10_CM_SYSTEM,
    "RXNORM": RXNORM_SYSTEM,
    "LOINC": LOINC_SYSTEM,
}


def get_value_set_code(value_set: Any) -> tuple[str, str] | None:
    """Extract the first available code and system from a value set."""
    for attr_name, system_uri in CODE_SYSTEM_MAP.items():
        if hasattr(value_set, attr_name):
            codes_set = getattr(value_set, attr_name)
            if codes_set:
                codes = list(codes_set)
                if codes:
                    return codes[0], system_uri
    return None


def extract_card(effects: list[Any]) -> dict[str, Any]:
    """Extract protocol card data from a single effect."""
    assert len(effects) == 1, f"Expected 1 effect, got {len(effects)}"
    eff = effects[0]
    assert eff.type == EffectType.ADD_OR_UPDATE_PROTOCOL_CARD
    return json.loads(eff.payload)["data"]


def create_protocol_instance(
    protocol_class: type[_CQM],
    timeframe_start: arrow.Arrow | None = None,
    timeframe_end: arrow.Arrow | None = None,
) -> _CQM:
    """Create a protocol instance with a custom timeframe for testing."""
    if timeframe_end is None:
        timeframe_end = arrow.now()
    if timeframe_start is None:
        timeframe_start = timeframe_end.shift(years=-1)

    custom_timeframe = Timeframe(start=timeframe_start, end=timeframe_end)

    class CustomTimeframeProtocol(protocol_class):  # type: ignore[valid-type, misc]
        @property
        def timeframe(self) -> Timeframe:
            return custom_timeframe

    mock_event = Mock()
    mock_event.type = 1

    protocol = CustomTimeframeProtocol(event=mock_event)
    protocol.now = timeframe_end

    return protocol


def set_protocol_patient_context(protocol: Any, patient_id: str) -> None:
    """Set patient context and target ID in a protocol's event."""
    protocol.event.context = {"patient": {"id": str(patient_id)}}
    protocol.event.target.id = str(patient_id)


def create_note_type(
    now: arrow.Arrow,
    code: str,
    name: str,
    pos: PracticeLocationPOS,
) -> NoteType:
    """Create a NoteType for encounter testing."""
    return NoteType.objects.create(
        code=code,
        system=SNOMED_CT_SYSTEM,
        display=name,
        name=name,
        icon="office",
        category=NoteTypeCategories.ENCOUNTER,
        rank=1,
        is_default_appointment_type=False,
        is_scheduleable=True,
        is_telehealth=False,
        is_billable=True,
        defer_place_of_service_to_practice_location=False,
        available_places_of_service=[],
        default_place_of_service=pos,
        is_system_managed=False,
        is_visible=True,
        is_active=True,
        unique_identifier=uuid.uuid4(),
        deprecated_at=now.shift(years=100).datetime,
        is_patient_required=False,
        allow_custom_title=False,
        is_scheduleable_via_patient_portal=False,
        online_duration=0,
    )


def create_condition_with_coding(
    patient: Patient,
    value_set: Any,
    onset_date: date | None = None,
    resolution_date: date | None = None,
    display: str = "Test condition",
) -> Condition:
    """Create a condition with a coding from the specified value set."""
    code_info = get_value_set_code(value_set)
    if not code_info:
        raise ValueError(f"No codes found in value set {value_set}")

    code, system = code_info
    condition = ConditionFactory.create(
        patient=patient,
        onset_date=onset_date or date.today(),
        resolution_date=resolution_date,
    )
    ConditionCodingFactory.create(
        condition=condition,
        code=code,
        system=system,
        display=display,
    )
    return condition


def create_medication_with_coding(
    patient: Patient,
    value_set: Any,
    start_date: arrow.Arrow | None = None,
    end_date: arrow.Arrow | None = None,
    display: str = "Test medication",
) -> Medication:
    """Create a medication with a coding from the specified value set."""
    rxnorm_codes = list(getattr(value_set, "RXNORM", []) or [])
    if not rxnorm_codes:
        raise ValueError(f"No RxNorm codes found in value set {value_set}")

    now = arrow.now()
    start = start_date or now
    end = end_date or arrow.get("2199-12-31")

    start_datetime = timezone.make_aware(datetime.combine(start.date(), datetime.min.time()))
    end_datetime = timezone.make_aware(datetime.combine(end.date(), datetime.min.time()))

    medication = MedicationFactory.create(
        patient=patient,
        start_date=start_datetime,
        end_date=end_datetime,
    )
    MedicationCodingFactory.create(
        medication=medication,
        code=rxnorm_codes[0],
        system=RXNORM_SYSTEM,
        display=display,
    )
    return medication


def create_lab_report_with_coding(
    patient: Patient,
    value_set: Any,
    value: float | str,
    original_date: arrow.Arrow,
    display: str = "Test lab value",
) -> LabReport:
    """Create a lab report with a value and coding from the specified value set."""
    loinc_codes = list(getattr(value_set, "LOINC", []) or [])
    if not loinc_codes:
        raise ValueError(f"No LOINC codes found in value set {value_set}")

    note = NoteFactory.create(
        patient=patient,
        datetime_of_service=original_date.datetime,
    )
    lab_report = LabReportFactory.create(
        patient=patient,
        original_date=original_date.datetime,
        note_id=note.dbid,
    )
    lab_value = LabValueFactory.create(
        report=lab_report,
        value=str(value),
    )
    LabValueCodingFactory.create(
        value=lab_value,
        code=loinc_codes[0],
        system=LOINC_SYSTEM,
        name=display,
    )
    return lab_report


def create_observation_with_value_coding(
    patient: Patient,
    note_id: int,
    effective_datetime: arrow.Arrow,
    code: str,
    display: str = "Test observation",
    system: str = SNOMED_CT_SYSTEM,
    category: str = "vital-signs",
    name: str = "Test observation",
) -> Observation:
    """Create an observation with a value coding."""
    observation = ObservationFactory.create(
        patient=patient,
        note_id=note_id,
        effective_datetime=effective_datetime.datetime,
        category=category,
        units="",
        value="",
        name=name,
    )
    ObservationValueCodingFactory.create(
        observation=observation,
        code=code,
        system=system,
        display=display,
    )
    return observation
