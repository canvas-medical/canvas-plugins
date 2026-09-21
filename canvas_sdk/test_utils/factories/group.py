import factory

from canvas_sdk.test_utils.factories.django_content_type import ContentTypeFactory
from canvas_sdk.v1.data import Group


class GroupFactory(factory.django.DjangoModelFactory[Group]):
    """Factory for creating a Group."""

    class Meta:
        model = Group

    content_type = factory.SubFactory(ContentTypeFactory, app_label="api", model="patientgroup")
    object_id = factory.Sequence(lambda n: n + 1)
