import factory

from staff_plus.models.biography import Biography
from staff_plus.models.proxy import StaffProxy


class BiographyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Biography

    staff = factory.SubFactory("staff_plus.tests.factories.staff_proxy_factory.StaffProxyFactory")
    biography = factory.Faker("paragraph", nb_sentences=5)