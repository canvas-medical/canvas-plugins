import datetime

import factory
from django.utils import timezone

from canvas_sdk.v1.data import AllergyIntolerance, AllergyIntoleranceReaction


class AllergyIntoleranceFactory(factory.django.DjangoModelFactory[AllergyIntolerance]):
    """Factory for creating an AllergyIntolerance."""

    class Meta:
        model = AllergyIntolerance

    deleted = False
    note_id = factory.Sequence(lambda n: n)
    allergy_intolerance_type = "A"
    category = 1
    status = "active"
    severity = "mild"
    onset_date = datetime.date(2024, 1, 1)
    onset_date_original_input = ""
    last_occurrence = datetime.date(2024, 1, 1)
    last_occurrence_original_input = ""
    recorded_date = factory.LazyFunction(timezone.now)
    narrative = ""


class AllergyIntoleranceReactionFactory(
    factory.django.DjangoModelFactory[AllergyIntoleranceReaction]
):
    """Factory for creating an AllergyIntoleranceReaction."""

    class Meta:
        model = AllergyIntoleranceReaction

    allergy_intolerance = factory.SubFactory(AllergyIntoleranceFactory)
    system = "http://snomed.info/sct"
    code = factory.Faker("numerify", text="#########")
    display = factory.Faker("text", max_nb_chars=200)
