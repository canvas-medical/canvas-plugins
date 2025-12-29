import datetime

import factory
from factory.fuzzy import FuzzyChoice, FuzzyDate, FuzzyInteger

from canvas_sdk.test_utils.factories.patient import PatientFactory
from canvas_sdk.test_utils.factories.user import CanvasUserFactory
from canvas_sdk.v1.data.protocol_override import IntervalUnit, ProtocolOverride, Status


class ProtocolOverrideFactory(factory.django.DjangoModelFactory[ProtocolOverride]):
    """ProtocolOverride testing factory."""
    class Meta:
        model = ProtocolOverride

    deleted = False
    committer = factory.SubFactory(CanvasUserFactory)
    entered_in_error = None
    patient = factory.SubFactory(PatientFactory)
    protocol_key = factory.Faker("slug")
    is_adjustment = True
    reference_date = factory.Faker(
        "date_time_between", start_date="-1y", end_date="now", tzinfo=datetime.UTC
    )
    cycle_in_days = FuzzyInteger(30, 365)
    is_snooze = False
    snooze_date = FuzzyDate(
        start_date=datetime.date.today(),
        end_date=datetime.date.today() + datetime.timedelta(days=90),
    )
    snoozed_days = FuzzyInteger(1, 30)
    snooze_comment = factory.Faker("text", max_nb_chars=100)
    narrative = factory.Faker("sentence", nb_words=6)
    cycle_quantity = FuzzyInteger(1, 12)
    cycle_unit = FuzzyChoice(IntervalUnit.choices, getter=lambda c: c[0])
    status = Status.ACTIVE
