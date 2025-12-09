from typing import Any

import factory
from django.utils import timezone

from canvas_sdk.v1.data import (
    LabOrder,
    LabOrderReason,
    LabOrderReasonCondition,
    LabPartner,
    LabPartnerTest,
    LabReport,
    LabReview,
    LabTest,
    LabValue,
    LabValueCoding,
)
from canvas_sdk.v1.data.common import (
    DocumentReviewMode,
    ReviewPatientCommunicationMethod,
    ReviewStatus,
)
from canvas_sdk.v1.data.lab import TransmissionType


class LabReportFactory(factory.django.DjangoModelFactory[LabReport]):
    """Factory for creating a LabReport."""

    class Meta:
        model = LabReport

    review_mode = DocumentReviewMode.REVIEW_REQUIRED
    junked = False
    requires_signature = False
    assigned_date = factory.LazyFunction(lambda: timezone.now())
    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    transmission_type = TransmissionType.HL7
    for_test_only = False
    external_id = factory.Faker("uuid4")
    version = 1
    requisition_number = factory.Faker("bothify", text="REQ-########")
    review = None  # Optional field
    original_date = factory.LazyFunction(lambda: timezone.now())
    date_performed = factory.LazyFunction(lambda: timezone.now())
    custom_document_name = factory.Faker("text", max_nb_chars=500)


class LabReviewFactory(factory.django.DjangoModelFactory[LabReview]):
    """Factory for creating a LabReview."""

    class Meta:
        model = LabReview

    internal_comment = factory.Faker("paragraph")
    message_to_patient = factory.Faker("text", max_nb_chars=2048)
    status = ReviewStatus.STATUS_REVIEWING
    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    patient_communication_method = ReviewPatientCommunicationMethod.DELEGATED_CALL_CAN_LEAVE_MESSAGE


class LabValueFactory(factory.django.DjangoModelFactory[LabValue]):
    """Factory for creating a LabValue."""

    class Meta:
        model = LabValue

    report = factory.SubFactory(LabReportFactory)
    value = factory.Faker("bothify", text="##.#")
    units = factory.Faker("random_element", elements=["mg/dL", "mmol/L", "g/dL", "%", "U/L"])
    abnormal_flag = factory.Faker("random_element", elements=["", "H", "L", "HH", "LL"])
    reference_range = factory.Faker("bothify", text="#.#-##.#")
    low_threshold = factory.Faker("bothify", text="#.#")
    high_threshold = factory.Faker("bothify", text="##.#")
    comment = factory.Faker("sentence")
    observation_status = factory.Faker(
        "random_element", elements=["final", "preliminary", "corrected"]
    )


class LabValueCodingFactory(factory.django.DjangoModelFactory[LabValueCoding]):
    """Factory for creating a LabValueCoding."""

    class Meta:
        model = LabValueCoding

    value = factory.SubFactory(LabValueFactory)
    code = factory.Faker("bothify", text="#####-#")
    name = factory.Faker("text", max_nb_chars=256)
    system = factory.Faker("random_element", elements=["LOINC", "SNOMED", "CPT"])


class LabOrderFactory(factory.django.DjangoModelFactory[LabOrder]):
    """Factory for creating a LabOrder."""

    class Meta:
        model = LabOrder
        skip_postgeneration_save = True

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    ontology_lab_partner = factory.Faker("company")
    note = factory.SubFactory("canvas_sdk.test_utils.factories.NoteFactory")
    comment = factory.Faker("text", max_nb_chars=128)
    requisition_number = factory.Faker("bothify", text="REQ-########")
    is_patient_bill = False
    date_ordered = factory.LazyFunction(lambda: timezone.now())
    fasting_status = None  # Optional field
    specimen_collection_type = LabOrder.SpecimenCollectionType.ON_LOCATION
    transmission_type = TransmissionType.HL7
    courtesy_copy_type = None  # Optional field
    courtesy_copy_number = ""
    courtesy_copy_text = ""
    ordering_provider = factory.SubFactory("canvas_sdk.test_utils.factories.StaffFactory")
    parent_order = None  # Optional field
    healthgorilla_id = ""
    manual_processing_status = None  # Optional field
    manual_processing_comment = None  # Optional field
    labcorp_abn_url = ""

    @factory.post_generation
    def reports(self, create: Any, extracted: Any, **kwargs: Any) -> None:
        """Handle many-to-many relationship for reports."""
        if not create:
            return

        if extracted:
            for report in extracted:
                self.reports.add(report)


class LabOrderReasonFactory(factory.django.DjangoModelFactory[LabOrderReason]):
    """Factory for creating a LabOrderReason."""

    class Meta:
        model = LabOrderReason

    order = factory.SubFactory(LabOrderFactory)
    mode = LabOrderReason.LabReasonMode.MONITOR


class LabOrderReasonConditionFactory(factory.django.DjangoModelFactory[LabOrderReasonCondition]):
    """Factory for creating a LabOrderReasonCondition."""

    class Meta:
        model = LabOrderReasonCondition

    reason = factory.SubFactory(LabOrderReasonFactory)
    condition = None  # Optional field - would need a ConditionFactory


class LabTestFactory(factory.django.DjangoModelFactory[LabTest]):
    """Factory for creating a LabTest."""

    class Meta:
        model = LabTest

    ontology_test_name = factory.Faker("text", max_nb_chars=512)
    ontology_test_code = factory.Faker("bothify", text="####-#")
    status = LabTest.LabTestOrderStatus.NEW
    report = factory.SubFactory(LabReportFactory)
    aoe_code = ""
    procedure_class = ""
    specimen_type = factory.Faker("random_element", elements=["blood", "urine", "serum", "plasma"])
    specimen_source_code = factory.Faker("bothify", text="###")
    specimen_source_description = factory.Faker("text", max_nb_chars=255)
    specimen_source_coding_system = factory.Faker("random_element", elements=["LOINC", "SNOMED"])
    order = factory.SubFactory(LabOrderFactory)


class LabPartnerFactory(factory.django.DjangoModelFactory[LabPartner]):
    """Factory for creating a LabPartner."""

    class Meta:
        model = LabPartner

    name = factory.Faker("company")
    active = True
    electronic_ordering_enabled = True
    keywords = factory.Faker("words", nb=5)
    default_lab_account_number = factory.Faker("bothify", text="LAB-######")


class LabPartnerTestFactory(factory.django.DjangoModelFactory[LabPartnerTest]):
    """Factory for creating a LabPartnerTest."""

    class Meta:
        model = LabPartnerTest

    lab_partner = factory.SubFactory(LabPartnerFactory)
    order_code = factory.Faker("bothify", text="####")
    order_name = factory.Faker("text", max_nb_chars=256)
    keywords = factory.Faker("words", nb=5)
    cpt_code = factory.Faker("bothify", text="#####")
