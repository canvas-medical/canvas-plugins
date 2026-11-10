import factory

from canvas_sdk.v1.data.document_type import DocumentType


class DocumentTypeFactory(factory.django.DjangoModelFactory[DocumentType]):
    """Factory for creating a DocumentType, by default an administrative one."""

    class Meta:
        model = DocumentType

    key = factory.Sequence(lambda n: f"{n:032x}")
    name = factory.Sequence(lambda n: f"Document Type {n}")
    report_type = "ADMINISTRATIVE"
    template_type = None
    template_fields = factory.LazyFunction(list)
