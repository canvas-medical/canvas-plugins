import factory
from django.utils import timezone

from canvas_sdk.test_utils.factories.django_content_type import ContentTypeFactory
from canvas_sdk.v1.data import Provenance
from canvas_sdk.v1.data.provenance import ProvenanceAction, ProvenanceParticipantType


class ProvenanceFactory(factory.django.DjangoModelFactory[Provenance]):
    """Factory for creating a Provenance."""

    class Meta:
        model = Provenance

    target_object_type = factory.SubFactory(ContentTypeFactory, model="condition")
    target_object_id = factory.Sequence(lambda n: n + 1)
    occurred_date_time = factory.LazyFunction(timezone.now)
    agent_object_type = factory.SubFactory(ContentTypeFactory, model="staff")
    agent_object_id = factory.Sequence(lambda n: n + 1)
    agent_participation_type = ProvenanceParticipantType.AUTHOR
    action = ProvenanceAction.CREATED
    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
