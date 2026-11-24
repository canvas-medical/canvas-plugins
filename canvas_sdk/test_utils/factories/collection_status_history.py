import datetime

import factory

from canvas_sdk.v1.data import CollectionStatus, CollectionStatusHistory


class CollectionStatusHistoryFactory(factory.django.DjangoModelFactory[CollectionStatusHistory]):
    """Factory for creating a CollectionStatusHistory."""

    class Meta:
        model = CollectionStatusHistory

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    status = CollectionStatus.INTERNAL
    status_date = datetime.date(2026, 1, 1)
