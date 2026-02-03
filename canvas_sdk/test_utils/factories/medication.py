"""Factories for Medication and MedicationCoding models."""

from datetime import datetime

import factory
from django.utils import timezone

from canvas_sdk.test_utils.factories.patient import PatientFactory
from canvas_sdk.v1.data.medication import Medication, MedicationCoding
from canvas_sdk.v1.data.medication import Status as MedicationStatus


class MedicationFactory(factory.django.DjangoModelFactory[Medication]):
    """Factory for creating a Medication."""

    class Meta:
        model = Medication

    patient = factory.SubFactory(PatientFactory)
    status = MedicationStatus.ACTIVE
    start_date = factory.LazyFunction(lambda: timezone.make_aware(datetime.now()))
    end_date = factory.LazyFunction(lambda: timezone.make_aware(datetime(2199, 12, 31, 23, 59, 59)))
    deleted = False
    quantity_qualifier_description = ""
    clinical_quantity_description = ""
    potency_unit_code = ""
    national_drug_code = ""
    erx_quantity = 0.0


class MedicationCodingFactory(factory.django.DjangoModelFactory[MedicationCoding]):
    """Factory for creating a MedicationCoding."""

    class Meta:
        model = MedicationCoding

    medication = factory.SubFactory(MedicationFactory)
    system = "http://www.nlm.nih.gov/research/umls/rxnorm"
    code = factory.Faker("numerify", text="######")
    display = factory.Faker("sentence", nb_words=3)
