import datetime

import factory

from canvas_sdk.v1.data import Fax, FaxStatusModel
from canvas_sdk.v1.data.fax import FaxDirection, FaxStatus


class FaxFactory(factory.django.DjangoModelFactory[Fax]):
    """Factory for creating Fax."""

    class Meta:
        model = Fax

    fax_id = factory.Faker("uuid4")
    to_fax_number = factory.Faker("numerify", text="+1##########")
    from_fax_number = factory.Faker("numerify", text="+1##########")
    date_utc = factory.Faker("date_time", tzinfo=datetime.UTC)
    fax_pages = factory.Faker("random_int", min=1, max=20)
    direction = FaxDirection.OUTBOUND
    success = True


class FaxStatusModelFactory(factory.django.DjangoModelFactory[FaxStatusModel]):
    """Factory for creating FaxStatusModel."""

    class Meta:
        model = FaxStatusModel

    fax = factory.SubFactory(FaxFactory)
    status = FaxStatus.RECEIVED
