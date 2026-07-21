import factory
from django.utils import timezone

from canvas_sdk.v1.data import Medication
from canvas_sdk.v1.data.medication import Status


class MedicationFactory(factory.django.DjangoModelFactory[Medication]):
    """Factory for Medication."""

    class Meta:
        model = Medication

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    committer = factory.SubFactory("canvas_sdk.test_utils.factories.CanvasUserFactory")
    deleted = False
    status = Status.ACTIVE
    start_date = factory.LazyFunction(timezone.now)
    end_date = factory.LazyFunction(timezone.now)
    quantity_qualifier_description = ""
    clinical_quantity_description = ""
    potency_unit_code = ""
    national_drug_code = ""
    erx_quantity = 1.0
