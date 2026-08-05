import factory

from canvas_sdk.test_utils.factories.django_content_type import ContentTypeFactory
from canvas_sdk.v1.data import OrganizationalEntity


class OrganizationalEntityFactory(factory.django.DjangoModelFactory[OrganizationalEntity]):
    """Factory for creating OrganizationalEntity."""

    class Meta:
        model = OrganizationalEntity

    content_type = factory.SubFactory(
        ContentTypeFactory, app_label="data_integration", model="serviceprovider"
    )
    object_id = factory.Sequence(lambda n: n + 1)
    name = factory.Faker("company")
    active = True
    type = OrganizationalEntity.OrganizationalEntityType.SERVICE_PROVIDER
