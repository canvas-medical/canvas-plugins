import factory

from canvas_sdk.test_utils.factories.patient import PatientFactory
from canvas_sdk.v1.data import ExternalEvent, ExternalVisit


class ExternalVisitFactory(factory.django.DjangoModelFactory[ExternalVisit]):
    """Factory for creating an ExternalVisit."""

    class Meta:
        model = ExternalVisit

    patient = factory.SubFactory(PatientFactory)
    visit_identifier = factory.Sequence(lambda n: f"visit-{n}")
    information_source = factory.Faker("company")
    facility_name = factory.Faker("company")


class ExternalEventFactory(factory.django.DjangoModelFactory[ExternalEvent]):
    """Factory for creating an ExternalEvent."""

    class Meta:
        model = ExternalEvent

    external_visit = factory.SubFactory(ExternalVisitFactory)
    patient = factory.LazyAttribute(lambda obj: obj.external_visit.patient)
    message_control_id = factory.Sequence(lambda n: f"msg-{n}")
    message_datetime = factory.Faker("date_time_this_year")
    event_type = "ADT^A01"
    event_datetime = factory.Faker("date_time_this_year")
    event_cancelation_datetime = None
    raw_message = factory.Faker("text", max_nb_chars=200)
