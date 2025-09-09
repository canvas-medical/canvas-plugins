import datetime

import factory
from factory.fuzzy import FuzzyChoice, FuzzyDate, FuzzyInteger

from canvas_sdk.test_utils.factories.patient import PatientFactory
from canvas_sdk.v1.data import ProtocolCurrent
from canvas_sdk.v1.data.protocol_result import ProtocolResultStatus


class ProtocolCurrentFactory(factory.django.DjangoModelFactory[ProtocolCurrent]):
    """Factory for creating a ProtocolCurrent."""

    class Meta:
        model = ProtocolCurrent

    # Fields from ProtocolResult (abstract base class)
    title = factory.Faker("sentence", nb_words=4)
    narrative = factory.Faker("text", max_nb_chars=200)
    types = factory.LazyFunction(lambda: ["screening", "preventive"])
    protocol_key = factory.Faker("slug")
    plugin_name = factory.Faker("slug")
    status = FuzzyChoice(ProtocolResultStatus.choices, getter=lambda c: c[0])
    due_in = FuzzyInteger(-30, 365)  # Days until due (can be negative for overdue)
    days_of_notice = FuzzyInteger(7, 60)
    snoozed = factory.Faker("boolean", chance_of_getting_true=20)
    sources = factory.LazyFunction(lambda: {"conditions": [], "medications": [], "labs": []})
    recommendations = factory.LazyFunction(lambda: {"primary": "Schedule annual checkup"})
    top_recommendation_key = factory.Faker("slug")
    next_review = factory.Faker("date_time_between", start_date="+1d", end_date="+1y")
    feedback_enabled = factory.Faker("boolean", chance_of_getting_true=30)
    plugin_can_be_snoozed = factory.Faker("boolean", chance_of_getting_true=70)

    # Fields specific to ProtocolCurrent
    patient = factory.SubFactory(PatientFactory)
    result_hash = factory.Faker("md5")
    snooze_date = factory.Maybe(
        "snoozed",
        yes_declaration=FuzzyDate(
            start_date=datetime.date.today(),
            end_date=datetime.date.today() + datetime.timedelta(days=90),
        ),
        no_declaration=None,
    )
