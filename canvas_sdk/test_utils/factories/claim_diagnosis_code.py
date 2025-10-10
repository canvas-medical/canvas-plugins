import factory
from factory.fuzzy import FuzzyInteger

from canvas_sdk.v1.data import ClaimDiagnosisCode


class ClaimDiagnosisCodeFactory(factory.django.DjangoModelFactory[ClaimDiagnosisCode]):
    """Factory for creating a ClaimDiagnosisCode."""

    class Meta:
        model = ClaimDiagnosisCode

    rank = FuzzyInteger(1, 12)  # ICD-10 allows up to 12 diagnosis codes on a claim
    code = factory.Faker("bothify", text="?##.##")  # ICD-10 format like A01.23
    display = factory.Faker("sentence", nb_words=4)  # Human readable diagnosis description
    claim = factory.SubFactory("canvas_sdk.test_utils.factories.ClaimFactory")
