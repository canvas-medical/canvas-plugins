import factory

from canvas_sdk.test_utils.factories.django_content_type import ContentTypeFactory
from canvas_sdk.v1.data import DocumentAnnotation


class DocumentAnnotationFactory(factory.django.DjangoModelFactory[DocumentAnnotation]):
    """Factory for creating DocumentAnnotation."""

    class Meta:
        model = DocumentAnnotation

    document = factory.Sequence(lambda n: f"document_annotations/annotation_{n}.pdf")
    created_by = factory.SubFactory("canvas_sdk.test_utils.factories.StaffFactory")
    content_type = factory.SubFactory(ContentTypeFactory, model="uncategorizedclinicaldocument")
    object_id = factory.Sequence(lambda n: n + 1)
