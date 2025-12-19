from datetime import date
from typing import Any, TypeVar
from unittest.mock import Mock

import arrow

from canvas_sdk.commands.constants import CodeSystems
from canvas_sdk.protocols.clinical_quality_measure import ClinicalQualityMeasure
from canvas_sdk.protocols.timeframe import Timeframe
from canvas_sdk.test_utils.factories import (
    BillingLineItemFactory,
    ConditionCodingFactory,
    ConditionFactory,
    ImagingReportCodingFactory,
    ImagingReportFactory,
    LabReportFactory,
    LabValueCodingFactory,
    LabValueFactory,
    NoteFactory,
    ObservationCodingFactory,
    ObservationFactory,
    ObservationValueCodingFactory,
    ReferralReportFactory,
)
from canvas_sdk.v1.data.billing import BillingLineItem
from canvas_sdk.v1.data.condition import Condition
from canvas_sdk.v1.data.imaging import ImagingReport
from canvas_sdk.v1.data.lab import LabReport, LabValue
from canvas_sdk.v1.data.medication import Medication, MedicationCoding
from canvas_sdk.v1.data.note import Note
from canvas_sdk.v1.data.observation import Observation
from canvas_sdk.v1.data.patient import Patient
from canvas_sdk.v1.data.referral import ReferralReport, ReferralReportCoding
from canvas_sdk.value_set.value_set import CodeConstants, ValueSet

_CQM = TypeVar("_CQM", bound=ClinicalQualityMeasure)


def create_protocol_instance(
    protocol_class: type[_CQM],
    timeframe_start: arrow.Arrow | None = None,
    timeframe_end: arrow.Arrow | None = None,
) -> _CQM:
    """
    Create a protocol instance with a custom timeframe for testing.

    This helper is useful for testing Clinical Quality Measures with specific
    measurement periods. It properly overrides the timeframe property which is
    normally derived from the protocol's configuration.

    Args:
        protocol_class: The ClinicalQualityMeasure class to instantiate.
        timeframe_start: Optional start date for the measurement period.
            Defaults to one year before timeframe_end.
        timeframe_end: Optional end date for the measurement period.
            Defaults to now.

    Returns:
        An instance of the protocol with the specified timeframe.

    Example:
        >>> from canvas_sdk.protocols.clinical_quality_measure import ClinicalQualityMeasure
        >>>
        >>> # Create protocol with default timeframe (last year)
        >>> protocol = create_protocol_instance(MyCQM)
        >>>
        >>> # Create protocol with specific measurement period
        >>> start = arrow.get("2023-01-01")
        >>> end = arrow.get("2023-12-31")
        >>> protocol = create_protocol_instance(MyCQM, start, end)
        >>> assert protocol.timeframe.start == start
        >>> assert protocol.timeframe.end == end
    """
    # Set timeframe (default to current year)
    if timeframe_end is None:
        timeframe_end = arrow.now()
    if timeframe_start is None:
        timeframe_start = timeframe_end.shift(years=-1)

    # Create a custom timeframe to return
    custom_timeframe = Timeframe(start=timeframe_start, end=timeframe_end)

    # Create a dynamic subclass that overrides the timeframe property.
    # Python property descriptors take precedence over instance __dict__ entries,
    # so we need to override at the class level to properly replace the property.
    class CustomTimeframeProtocol(protocol_class):  # type: ignore[valid-type, misc]
        @property
        def timeframe(self) -> Timeframe:
            return custom_timeframe

    # Create mock event
    mock_event = Mock()
    mock_event.type = 1

    # Instantiate the customized protocol
    protocol = CustomTimeframeProtocol(event=mock_event)

    # Set now for consistency
    protocol.now = timeframe_end

    return protocol


def create_condition_with_coding(
    patient: Patient,
    value_set_class: type[ValueSet],
    onset_date: date | arrow.Arrow | None = None,
    surgical: bool = True,
    **kwargs: Any,
) -> Condition:
    """
    Create a Condition with proper ConditionCoding from a ValueSet.

    This helper automatically selects the first available code from the ValueSet
    and creates the appropriate ConditionCoding with the correct system URL. This
    ensures that the condition will be found by ValueSet queries.

    Args:
        patient: The patient for this condition.
        value_set_class: ValueSet class containing the codes to use.
        onset_date: Date of onset. Defaults to today. Can be a date or arrow object.
        surgical: Whether this is a surgical condition. Defaults to True.
        **kwargs: Additional fields to pass to ConditionFactory.

    Returns:
        Condition instance with associated ConditionCoding.

    Example:
        >>> from canvas_sdk.value_set.v2022.condition import Diabetes
        >>>
        >>> condition = create_condition_with_coding(
        ...     patient=patient,
        ...     value_set_class=Diabetes,
        ...     onset_date=arrow.get("2023-01-15").date()
        ... )
        >>>
        >>> # The condition will have a ConditionCoding that matches the ValueSet
        >>> assert condition.codings.exists()
        >>>
        >>> # It will be found by ValueSet queries
        >>> from canvas_sdk.v1.data.condition import Condition
        >>> found = Condition.objects.filter(patient=patient).find(Diabetes)
        >>> assert condition in found
    """
    # Convert onset_date to date object if it's an arrow object
    if onset_date is None:
        onset_date = arrow.now().date()
    elif hasattr(onset_date, "date"):
        onset_date = onset_date.date()

    # For ongoing conditions, use a date far in the future
    resolution_date = kwargs.pop("resolution_date", arrow.get("9999-12-31").date())

    # Create condition using factory
    condition = ConditionFactory.create(
        patient=patient,
        onset_date=onset_date,
        resolution_date=resolution_date,
        surgical=surgical,
        **kwargs,
    )

    # Add coding if value set has codes
    # values is a dict of {code_constant: set[code]}
    # We need to map code_constant to the actual system URL
    if hasattr(value_set_class, "values") and value_set_class.values:
        for code_constant, codes in value_set_class.values.items():
            if codes:
                # Map code constant to system URL using CODE_SYSTEM_MAPPING
                system_url = value_set_class.CODE_SYSTEM_MAPPING.get(code_constant)
                if system_url:
                    # Get first code from the set
                    code = next(iter(codes))
                    ConditionCodingFactory.create(
                        condition=condition,
                        system=system_url,
                        code=code,
                    )
                    # Only need one coding for testing
                    break

    return condition


def create_encounter_with_billing(
    patient: Patient,
    encounter_date: date | arrow.Arrow,
    value_set_class: type[ValueSet] | None = None,
    cpt_code: str | None = None,
) -> tuple[Note, BillingLineItem]:
    """
    Create an encounter (Note) with associated BillingLineItem.

    This helper creates both a Note and a BillingLineItem with the appropriate
    CPT/HCPCS code from a ValueSet. This is useful for testing protocols that
    require qualifying encounters.

    Args:
        patient: The patient for this encounter.
        encounter_date: Date of the encounter. Can be a date or arrow object.
        value_set_class: Optional ValueSet class containing CPT/HCPCS codes.
            If provided, uses the first code from the ValueSet.
        cpt_code: Optional explicit CPT code. If not provided, extracts from
            value_set_class. If neither is provided, defaults to "99213".

    Returns:
        A tuple of (Note, BillingLineItem).

    Example:
        >>> from canvas_sdk.value_set.v2022.encounter import OfficeVisit
        >>>
        >>> # Create encounter with ValueSet
        >>> note, billing = create_encounter_with_billing(
        ...     patient=patient,
        ...     encounter_date=arrow.get("2023-06-15"),
        ...     value_set_class=OfficeVisit
        ... )
        >>>
        >>> # Create encounter with explicit CPT code
        >>> note, billing = create_encounter_with_billing(
        ...     patient=patient,
        ...     encounter_date=arrow.now().shift(days=-30),
        ...     cpt_code="99214"
        ... )
    """
    # Extract CPT/HCPCS code from value set if not explicitly provided
    if (
        cpt_code is None
        and value_set_class is not None
        and hasattr(value_set_class, "values")
        and value_set_class.values
    ):
        # Try HCPCS first (what BillingLineItem.find() looks for)
        if CodeConstants.HCPCS in value_set_class.values:
            codes = value_set_class.values[CodeConstants.HCPCS]
            if codes:
                cpt_code = next(iter(codes))

        # If no HCPCS, try CPT codes
        if not cpt_code and CodeConstants.CPT in value_set_class.values:
            codes = value_set_class.values[CodeConstants.CPT]
            if codes:
                cpt_code = next(iter(codes))

    # If no CPT code found, use a generic one
    if not cpt_code:
        cpt_code = "99213"  # Office visit code

    # Convert encounter_date to datetime if needed
    if hasattr(encounter_date, "datetime"):
        encounter_datetime = encounter_date.datetime
    elif hasattr(encounter_date, "date"):
        # It's a datetime.date, convert to arrow then to datetime
        encounter_datetime = arrow.get(encounter_date).datetime
    else:
        # Assume it's already a datetime
        encounter_datetime = encounter_date

    # Create a note with datetime_of_service using factory
    note = NoteFactory.create(
        patient=patient,
        datetime_of_service=encounter_datetime,
    )

    # Create billing line item using factory
    billing_item = BillingLineItemFactory.create(
        patient=patient,
        note=note,
        cpt=cpt_code,
    )

    return note, billing_item


def create_imaging_report_with_coding(
    patient: Patient,
    value_set_class: type[ValueSet],
    original_date: date | arrow.Arrow | None = None,
    result_date: date | arrow.Arrow | None = None,
    **kwargs: Any,
) -> ImagingReport:
    """
    Create an ImagingReport with proper ImagingReportCoding from a ValueSet.

    This helper automatically selects the first available code from the ValueSet
    and creates the appropriate ImagingReportCoding with the correct system URL.
    This ensures that the imaging report will be found by ValueSet queries.

    Args:
        patient: The patient for this imaging report.
        value_set_class: ValueSet class containing the codes to use.
        original_date: Date of imaging. Defaults to today. Can be a date or arrow object.
        result_date: Date results available. Defaults to original_date.
        **kwargs: Additional fields to pass to ImagingReportFactory.

    Returns:
        ImagingReport instance with associated ImagingReportCoding.

    Example:
        >>> from canvas_sdk.value_set.v2022.procedure import Mammography
        >>>
        >>> report = create_imaging_report_with_coding(
        ...     patient=patient,
        ...     value_set_class=Mammography,
        ...     original_date=arrow.get("2023-01-15").date()
        ... )
        >>>
        >>> # The report will have an ImagingReportCoding that matches the ValueSet
        >>> assert report.codings.exists()
        >>>
        >>> # It will be found by ValueSet queries
        >>> from canvas_sdk.v1.data.imaging import ImagingReport
        >>> found = ImagingReport.objects.filter(patient=patient).find(Mammography)
        >>> assert report in found
    """
    # Convert dates to date objects if they're arrow objects
    if original_date is None:
        original_date = arrow.now().date()
    elif hasattr(original_date, "date"):
        original_date = original_date.date()

    if result_date is None:
        result_date = original_date
    elif hasattr(result_date, "date"):
        result_date = result_date.date()

    # Create imaging report using factory
    report = ImagingReportFactory.create(
        patient=patient,
        original_date=original_date,
        result_date=result_date,
        **kwargs,
    )

    # Add coding if value set has codes
    # values is a dict of {code_constant: set[code]}
    # We need to map code_constant to the actual system URL
    if hasattr(value_set_class, "values") and value_set_class.values:
        for code_constant, codes in value_set_class.values.items():
            if codes:
                # Map code constant to system URL using CODE_SYSTEM_MAPPING
                system_url = value_set_class.CODE_SYSTEM_MAPPING.get(code_constant)
                if system_url:
                    # Get first code from the set
                    code = next(iter(codes))
                    ImagingReportCodingFactory.create(
                        report=report,
                        system=system_url,
                        code=code,
                    )
                    # Only need one coding for testing
                    break

    return report


def create_observation_with_value_coding(
    patient: Patient,
    snomed_code: str,
    effective_datetime: arrow.Arrow | None = None,
    display: str = "Test observation value",
    **kwargs: Any,
) -> Observation:
    """
    Create an Observation with proper ObservationValueCoding using a SNOMED code.

    Args:
        patient: The patient for this observation.
        snomed_code: The SNOMED code for the observation value.
        effective_datetime: When the observation was made. Defaults to now.
        display: Display text for the coding. Defaults to "Test observation value".
        **kwargs: Additional fields to pass to ObservationFactory.

    Returns:
        Observation instance with associated ObservationValueCoding.
    """
    if effective_datetime is None:
        effective_datetime = arrow.now()

    observation = ObservationFactory.create(
        patient=patient,
        effective_datetime=effective_datetime.datetime,
        **kwargs,
    )

    ObservationValueCodingFactory.create(
        observation=observation,
        system=CodeSystems.SNOMED,
        code=snomed_code,
        display=display,
    )

    return observation


def create_observation_with_coding(
    patient: Patient,
    codings_code: str,
    codings_system: str,
    effective_datetime: arrow.Arrow | None = None,
    value_codings_code: str | None = None,
    value_codings_system: str | None = None,
    **kwargs: Any,
) -> Observation:
    """
    Create an Observation with both ObservationCoding and optionally ObservationValueCoding.

    This helper creates an Observation with the required ObservationCoding and optionally
    an ObservationValueCoding. This is useful for testing protocols that check both
    observation codes and observation value codes.

    Args:
        patient: The patient for this observation.
        codings_code: The code for the ObservationCoding.
        codings_system: The system URL for the ObservationCoding.
        effective_datetime: When the observation was made. Defaults to now.
        value_codings_code: Optional code for the ObservationValueCoding.
        value_codings_system: Optional system URL for the ObservationValueCoding.
        **kwargs: Additional fields to pass to ObservationFactory.

    Returns:
        Observation instance with associated ObservationCoding and optionally ObservationValueCoding.

    Example:
        >>> # Create observation with both codings
        >>> observation = create_observation_with_coding(
        ...     patient=patient,
        ...     codings_code="71802-3",
        ...     codings_system="http://loinc.org",
        ...     value_codings_code="160734000",
        ...     value_codings_system="http://snomed.info/sct",
        ...     effective_datetime=arrow.get("2023-01-15")
        ... )
        >>>
        >>> assert observation.codings.exists()
        >>> assert observation.value_codings.exists()
    """
    if effective_datetime is None:
        effective_datetime = arrow.now()

    # Create a note first (required for observation)
    note = NoteFactory.create(patient=patient, datetime_of_service=effective_datetime.datetime)

    # Create observation using factory
    observation = ObservationFactory.create(
        patient=patient,
        note_id=note.dbid,
        effective_datetime=effective_datetime.datetime,
        **kwargs,
    )

    # Add observation coding
    ObservationCodingFactory.create(
        observation=observation,
        code=codings_code,
        system=codings_system,
        display=kwargs.get("name", "Test Observation"),
    )

    # Add value coding if provided
    if value_codings_code and value_codings_system:
        ObservationValueCodingFactory.create(
            observation=observation,
            code=value_codings_code,
            system=value_codings_system,
            display=kwargs.get("value_display", "Test Result"),
        )

    return observation


def create_lab_report_with_loinc(
    patient: Patient,
    original_date: date | arrow.Arrow | None = None,
    loinc_code: str = "",
    name: str = "",
    **kwargs: Any,
) -> tuple[LabReport, LabValue]:
    """
    Create a LabReport with LabValue and LabValueCoding using a LOINC code.

    This helper creates a complete lab report structure with a lab value and its coding.
    This is useful for testing protocols that check for lab results.

    Args:
        patient: The patient for this lab report.
        original_date: Date of the lab report. Defaults to today. Can be a date, arrow object, or datetime.
        loinc_code: The LOINC code for the lab test.
        name: Display name for the lab value coding. Defaults to the LOINC code.
        **kwargs: Additional fields to pass to LabReportFactory or LabValueFactory.

    Returns:
        A tuple of (LabReport, LabValue).

    Example:
        >>> report, value = create_lab_report_with_loinc(
        ...     patient=patient,
        ...     original_date=arrow.get("2023-01-15"),
        ...     loinc_code="2335-8",
        ...     name="FOBT"
        ... )
        >>>
        >>> assert report.patient == patient
        >>> assert value.codings.exists()
    """
    # Convert original_date to date/datetime as needed
    from datetime import datetime as dt_datetime

    if original_date is None:
        original_date = arrow.now()
        original_date_obj = original_date.date()
        original_datetime = original_date.datetime
    elif isinstance(original_date, dt_datetime):
        # It's a datetime object
        original_date_obj = original_date.date()
        original_datetime = original_date
    elif hasattr(original_date, "date") and hasattr(original_date, "datetime"):
        # It's an arrow object
        original_date_obj = original_date.date()
        original_datetime = original_date.datetime
    else:
        # It's a date object
        original_date_obj = original_date
        original_datetime = arrow.get(original_date).datetime

    # Extract kwargs for LabValueFactory
    lab_value_kwargs = {
        "value": kwargs.pop("value", "Negative"),
        "units": kwargs.pop("units", ""),
        "abnormal_flag": kwargs.pop("abnormal_flag", ""),
        "reference_range": kwargs.pop("reference_range", ""),
        "low_threshold": kwargs.pop("low_threshold", ""),
        "high_threshold": kwargs.pop("high_threshold", ""),
        "comment": kwargs.pop("comment", ""),
        "observation_status": kwargs.pop("observation_status", "final"),
    }

    # Create lab report using factory
    report = LabReportFactory.create(
        patient=patient,
        original_date=original_date_obj,
        assigned_date=original_datetime,
        date_performed=original_date_obj,
        **kwargs,
    )

    # Create lab value using factory
    value = LabValueFactory.create(report=report, **lab_value_kwargs)

    # Add LOINC coding
    LabValueCodingFactory.create(
        value=value,
        code=loinc_code,
        system=CodeSystems.LOINC,
        name=name or loinc_code,
    )

    return report, value


def create_medication_with_coding(
    patient: Patient,
    code: str,
    system: str,
    start_date: date | arrow.Arrow | None = None,
    end_date: date | arrow.Arrow | None = None,
    display: str = "",
    **kwargs: Any,
) -> Medication:
    """
    Create a Medication with MedicationCoding.

    This helper creates a Medication with the appropriate MedicationCoding.
    This is useful for testing protocols that check for medications.

    Args:
        patient: The patient for this medication.
        code: The medication code (e.g., RxNorm code).
        system: The system URL for the medication code.
        start_date: Start date of the medication. Defaults to today. Can be a date or arrow object.
        end_date: End date of the medication. Defaults to far future. Can be a date or arrow object.
        display: Display text for the coding. Defaults to empty string.
        **kwargs: Additional fields to pass to Medication creation.

    Returns:
        Medication instance with associated MedicationCoding.

    Example:
        >>> medication = create_medication_with_coding(
        ...     patient=patient,
        ...     code="123456",
        ...     system="http://www.nlm.nih.gov/research/umls/rxnorm",
        ...     start_date=arrow.get("2023-01-15").date(),
        ...     display="Test Medication"
        ... )
        >>>
        >>> assert medication.patient == patient
        >>> assert medication.codings.exists()
    """
    # Convert dates to datetime objects if needed
    if start_date is None:
        start_datetime = arrow.now().datetime
    elif hasattr(start_date, "datetime"):
        start_datetime = start_date.datetime
    elif hasattr(start_date, "date"):
        start_datetime = arrow.get(start_date).datetime
    else:
        start_datetime = start_date

    if end_date is None:
        end_datetime = arrow.get("9999-12-31").datetime
    elif hasattr(end_date, "datetime"):
        end_datetime = end_date.datetime
    elif hasattr(end_date, "date"):
        end_datetime = arrow.get(end_date).datetime
    else:
        end_datetime = end_date

    # Extract required fields with defaults
    from canvas_sdk.test_utils.factories import CanvasUserFactory

    user = kwargs.pop("committer", CanvasUserFactory())

    # Create medication
    medication = Medication.objects.create(
        patient=patient,
        start_date=start_datetime,
        end_date=end_datetime,
        deleted=kwargs.pop("deleted", False),
        committer=user,
        erx_quantity=kwargs.pop("erx_quantity", 0.0),
        status=kwargs.pop("status", "active"),
        quantity_qualifier_description=kwargs.pop("quantity_qualifier_description", ""),
        clinical_quantity_description=kwargs.pop("clinical_quantity_description", ""),
        potency_unit_code=kwargs.pop("potency_unit_code", ""),
        national_drug_code=kwargs.pop("national_drug_code", ""),
        **kwargs,
    )

    # Add medication coding (no factory available, create directly)
    MedicationCoding.objects.create(
        medication=medication,
        code=code,
        system=system,
        display=display,
    )

    return medication


def create_referral_report_with_cpt(
    patient: Patient,
    cpt_code: str,
    original_date: date | arrow.Arrow | None = None,
    display: str = "",
    specialty: str = "Gastroenterology",
    **kwargs: Any,
) -> ReferralReport:
    """
    Create a ReferralReport with CPT coding.

    This helper creates a ReferralReport with the appropriate ReferralReportCoding using CPT codes.
    This is useful for testing protocols that check for referral reports.

    Args:
        patient: The patient for this referral report.
        cpt_code: The CPT code.
        original_date: Date of the referral report. Defaults to today. Can be a date or arrow object.
        display: Display text for the coding. Defaults to empty string.
        specialty: Specialty for the referral. Defaults to "Gastroenterology".
        **kwargs: Additional fields to pass to ReferralReportFactory.

    Returns:
        ReferralReport instance with associated ReferralReportCoding.

    Example:
        >>> report = create_referral_report_with_cpt(
        ...     patient=patient,
        ...     cpt_code="45378",
        ...     original_date=arrow.get("2023-01-15").date(),
        ...     display="Colonoscopy"
        ... )
        >>>
        >>> assert report.patient == patient
        >>> assert report.codings.exists()
    """
    # Convert original_date to date object if it's an arrow object
    if original_date is None:
        original_date = arrow.now().date()
    elif hasattr(original_date, "date"):
        original_date = original_date.date()

    # Create referral report using factory
    report = ReferralReportFactory.create(
        patient=patient,
        original_date=original_date,
        specialty=specialty,
        **kwargs,
    )

    # Add referral report coding
    ReferralReportCoding.objects.create(
        report=report,
        code=cpt_code,
        system="http://www.ama-assn.org/go/cpt",
        display=display,
    )

    return report


def create_referral_report_with_loinc(
    patient: Patient,
    loinc_code: str,
    original_date: date | arrow.Arrow | None = None,
    display: str = "",
    specialty: str = "Gastroenterology",
    **kwargs: Any,
) -> ReferralReport:
    """
    Create a ReferralReport with LOINC coding.

    This helper creates a ReferralReport with the appropriate ReferralReportCoding using LOINC codes.
    This is useful for testing protocols that check for referral reports.

    Args:
        patient: The patient for this referral report.
        loinc_code: The LOINC code.
        original_date: Date of the referral report. Defaults to today. Can be a date or arrow object.
        display: Display text for the coding. Defaults to empty string.
        specialty: Specialty for the referral. Defaults to "Gastroenterology".
        **kwargs: Additional fields to pass to ReferralReportFactory.

    Returns:
        ReferralReport instance with associated ReferralReportCoding.

    Example:
        >>> report = create_referral_report_with_loinc(
        ...     patient=patient,
        ...     loinc_code="12345-6",
        ...     original_date=arrow.get("2023-01-15").date(),
        ...     display="CT Colonography"
        ... )
        >>>
        >>> assert report.patient == patient
        >>> assert report.codings.exists()
    """
    # Convert original_date to date object if it's an arrow object
    if original_date is None:
        original_date = arrow.now().date()
    elif hasattr(original_date, "date"):
        original_date = original_date.date()

    # Create referral report using factory
    report = ReferralReportFactory.create(
        patient=patient,
        original_date=original_date,
        specialty=specialty,
        **kwargs,
    )

    # Add referral report coding
    ReferralReportCoding.objects.create(
        report=report,
        code=loinc_code,
        system=CodeSystems.LOINC,
        display=display,
    )

    return report


__exports__ = (
    "create_condition_with_coding",
    "create_encounter_with_billing",
    "create_imaging_report_with_coding",
    "create_lab_report_with_loinc",
    "create_medication_with_coding",
    "create_observation_with_coding",
    "create_observation_with_value_coding",
    "create_protocol_instance",
    "create_referral_report_with_cpt",
    "create_referral_report_with_loinc",
)
