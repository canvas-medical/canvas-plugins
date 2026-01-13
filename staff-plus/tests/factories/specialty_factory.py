import factory

from staff_plus.models.specialty import Specialty, StaffSpecialty


class SpecialtyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Specialty
        django_get_or_create = ("name",)

    name = factory.Faker("random_element", elements=[
        "cardiology", "dermatology", "neurology", "orthopedics",
        "pediatrics", "psychiatry", "radiology", "surgery",
        "family medicine", "internal medicine", "emergency medicine"
    ])


class StaffSpecialtyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StaffSpecialty

    staff = factory.SubFactory("staff_plus.tests.factories.staff_proxy_factory.StaffProxyFactory")
    specialty = factory.SubFactory(SpecialtyFactory)