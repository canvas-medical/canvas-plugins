import factory

from canvas_sdk.test_utils.factories.patient import PatientFactory
from canvas_sdk.v1.data import PaymentCard


class PaymentCardFactory(factory.django.DjangoModelFactory[PaymentCard]):
    """Factory for creating a PaymentCard (a patient's stored card on file)."""

    class Meta:
        model = PaymentCard

    patient = factory.SubFactory(PatientFactory)
    card_last_four_digits = factory.Sequence(lambda n: f"{n % 10000:04d}")
    brand = "visa"
    expiration_month = "12"
    expiration_year = "2030"
    card_holder_name = factory.Faker("name")
    postal_code = "94107"
    is_default = False
