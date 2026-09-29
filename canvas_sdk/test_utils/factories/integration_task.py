import uuid

import factory

from canvas_sdk.v1.data import IntegrationTask, IntegrationTaskActionEvent, IntegrationTaskReview
from canvas_sdk.v1.data.action_event_base import EventTypeChoices
from canvas_sdk.v1.data.integration_task import IntegrationTaskChannel, IntegrationTaskStatus


class IntegrationTaskFactory(factory.django.DjangoModelFactory[IntegrationTask]):
    """Factory for creating IntegrationTask."""

    class Meta:
        model = IntegrationTask

    id = factory.LazyFunction(uuid.uuid4)
    status = IntegrationTaskStatus.UNREAD
    type = factory.Faker("word")
    title = factory.Faker("sentence", nb_words=4)
    channel = IntegrationTaskChannel.FAX
    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    service_provider = factory.SubFactory("canvas_sdk.test_utils.factories.ServiceProviderFactory")


class IntegrationTaskReviewFactory(factory.django.DjangoModelFactory[IntegrationTaskReview]):
    """Factory for creating IntegrationTaskReview."""

    class Meta:
        model = IntegrationTaskReview

    id = factory.LazyFunction(uuid.uuid4)
    task = factory.SubFactory(IntegrationTaskFactory)
    template_name = factory.Faker("sentence", nb_words=3)
    document_key = factory.Faker("uuid4")
    reviewer = factory.SubFactory("canvas_sdk.test_utils.factories.StaffFactory")
    team_reviewer = None
    junked = False


class IntegrationTaskActionEventFactory(
    factory.django.DjangoModelFactory[IntegrationTaskActionEvent]
):
    """Factory for creating IntegrationTaskActionEvent."""

    class Meta:
        model = IntegrationTaskActionEvent

    event_type = EventTypeChoices.FAXED
    send_fax_id = factory.Faker("uuid4")
    received_by_fax = True
    delivered_by_fax = None
    fax_result_msg = ""
    originator = factory.SubFactory("canvas_sdk.test_utils.factories.CanvasUserFactory")
    fax = factory.SubFactory("canvas_sdk.test_utils.factories.FaxFactory")
    integration_task = factory.SubFactory("canvas_sdk.test_utils.factories.IntegrationTaskFactory")
