import factory

from canvas_sdk.test_utils.factories.patient import PatientFactory
from canvas_sdk.v1.data import PatientGroup, PatientGroupMember


class PatientGroupFactory(factory.django.DjangoModelFactory[PatientGroup]):
    """Factory for creating a PatientGroup."""

    class Meta:
        model = PatientGroup

    name = factory.Sequence(lambda n: f"Test Group {n}")


class PatientGroupMemberFactory(factory.django.DjangoModelFactory[PatientGroupMember]):
    """Factory for creating a PatientGroupMember."""

    class Meta:
        model = PatientGroupMember

    patient_group = factory.SubFactory(PatientGroupFactory)
    member = factory.SubFactory(PatientFactory)
    locked = False
    active = True
