import factory

from canvas_sdk.test_utils.factories.django_content_type import ContentTypeFactory
from canvas_sdk.v1.data import DocumentHistoryEvent
from canvas_sdk.v1.data.document_history_event import DocumentHistoryEventType


class DocumentHistoryEventFactory(factory.django.DjangoModelFactory[DocumentHistoryEvent]):
    """Factory for creating DocumentHistoryEvent."""

    class Meta:
        model = DocumentHistoryEvent

    content_type = factory.SubFactory(ContentTypeFactory, model="uncategorizedclinicaldocument")
    object_id = factory.Sequence(lambda n: n + 1)
    event_type = DocumentHistoryEventType.COMMENTED
    actor = factory.SubFactory("canvas_sdk.test_utils.factories.StaffFactory")
    comment = ""
