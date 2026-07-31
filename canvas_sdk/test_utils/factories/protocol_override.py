import datetime

import factory
from django.utils import timezone

from canvas_sdk.v1.data import ProtocolOverride
from canvas_sdk.v1.data.protocol_override import IntervalUnit, Status


class ProtocolOverrideFactory(factory.django.DjangoModelFactory[ProtocolOverride]):
    """Factory for creating a ProtocolOverride."""

    class Meta:
        model = ProtocolOverride

    deleted = False
    committer = factory.SubFactory("canvas_sdk.test_utils.factories.CanvasUserFactory")
    entered_in_error = None
    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    protocol_key = factory.Faker("slug")
    is_adjustment = False
    reference_date = factory.LazyFunction(timezone.now)
    cycle_in_days = 365
    is_snooze = False
    snooze_date = datetime.date(1000, 1, 1)
    snoozed_days = 0
    snooze_comment = ""
    narrative = ""
    cycle_quantity = 1
    cycle_unit = IntervalUnit.YEARS
    status = Status.ACTIVE
