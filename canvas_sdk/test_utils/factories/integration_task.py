import factory

from canvas_sdk.v1.data import IntegrationTask
from canvas_sdk.v1.data.integration_task import IntegrationTaskChannel, IntegrationTaskStatus


class IntegrationTaskFactory(factory.django.DjangoModelFactory[IntegrationTask]):
    """Factory for creating IntegrationTask."""

    class Meta:
        model = IntegrationTask

    id = factory.Sequence(lambda n: n + 1)
    status = IntegrationTaskStatus.UNREAD
    type = factory.Faker("word")
    title = factory.Faker("sentence", nb_words=4)
    channel = IntegrationTaskChannel.FAX
    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    service_provider = factory.SubFactory("canvas_sdk.test_utils.factories.ServiceProviderFactory")
