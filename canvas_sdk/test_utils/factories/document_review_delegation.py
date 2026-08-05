import factory

from canvas_sdk.test_utils.factories.django_content_type import ContentTypeFactory
from canvas_sdk.v1.data import DocumentReviewDelegation


class DocumentReviewDelegationFactory(factory.django.DjangoModelFactory[DocumentReviewDelegation]):
    """Factory for creating DocumentReviewDelegation."""

    class Meta:
        model = DocumentReviewDelegation

    content_type = factory.SubFactory(ContentTypeFactory, model="uncategorizedclinicaldocument")
    object_id = factory.Sequence(lambda n: n + 1)
    delegated_by = factory.SubFactory("canvas_sdk.test_utils.factories.StaffFactory")
    delegated_to_staff = factory.SubFactory("canvas_sdk.test_utils.factories.StaffFactory")
    on_behalf_of = factory.SelfAttribute("delegated_by")
    signature_consent = False
    comment = ""
    is_active = True
