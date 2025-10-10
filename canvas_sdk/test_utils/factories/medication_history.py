import datetime

import factory
from django.utils import timezone
from factory.fuzzy import FuzzyDate, FuzzyDateTime

from canvas_sdk.test_utils.factories.patient import PatientFactory
from canvas_sdk.v1.data.medication_history import (
    MedicationHistoryMedication,
    MedicationHistoryMedicationCoding,
    MedicationHistoryResponse,
    MedicationHistoryResponseStatus,
)


class MedicationHistoryMedicationFactory(
    factory.django.DjangoModelFactory[MedicationHistoryMedication]
):
    """Factory for creating a MedicationHistoryMedication."""

    class Meta:
        model = MedicationHistoryMedication

    patient = factory.SubFactory(PatientFactory)
    last_fill_date = FuzzyDateTime(
        start_dt=timezone.now() - datetime.timedelta(days=365), end_dt=timezone.now()
    )

    drug_description = factory.Faker("word")
    strength_value = "10"
    strength_form = "tablet"
    strength_unit_of_measure = "mg"
    quantity = 30.0
    quantity_unit_of_measure = "tablets"
    days_supply = 30
    sig = factory.Faker("sentence", nb_words=4)


class MedicationHistoryMedicationCodingFactory(
    factory.django.DjangoModelFactory[MedicationHistoryMedicationCoding]
):
    """Factory for creating a MedicationHistoryMedicationCoding."""

    class Meta:
        model = MedicationHistoryMedicationCoding

    medication = factory.SubFactory(MedicationHistoryMedicationFactory)

    system = "http://www.nlm.nih.gov/research/umls/rxnorm"
    version = "1.0"
    code = factory.Faker("numerify", text="######")
    display = factory.Faker("word")
    user_selected = False


class MedicationHistoryResponseFactory(
    factory.django.DjangoModelFactory[MedicationHistoryResponse]
):
    """Factory for creating a MedicationHistoryResponse."""

    class Meta:
        model = MedicationHistoryResponse

    patient = factory.SubFactory(PatientFactory)
    status = MedicationHistoryResponseStatus.STATUS_APPROVED
    start_date = FuzzyDate(
        start_date=datetime.date.today() - datetime.timedelta(days=365),
        end_date=datetime.date.today(),
    )
    end_date = FuzzyDate(
        start_date=datetime.date.today(),
        end_date=datetime.date.today() + datetime.timedelta(days=365),
    )
    message_id = factory.Faker("uuid4")
    related_to_message_id = factory.Faker("uuid4")
