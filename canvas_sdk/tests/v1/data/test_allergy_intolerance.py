import pytest

from canvas_sdk.test_utils.factories import (
    AllergyIntoleranceFactory,
    AllergyIntoleranceReactionFactory,
)
from canvas_sdk.v1.data import AllergyIntoleranceReaction


@pytest.mark.django_db
def test_allergy_intolerance_reactions_return_only_its_codings() -> None:
    """AllergyIntolerance.reactions returns only that allergy's reactions."""
    parent = AllergyIntoleranceFactory.create()
    coding = AllergyIntoleranceReactionFactory.create(allergy_intolerance=parent)
    AllergyIntoleranceReactionFactory.create()

    assert list(parent.reactions.all()) == [coding]


@pytest.mark.django_db
def test_allergy_intolerance_reaction_resolves_to_its_allergy_intolerance() -> None:
    """The allergy_intolerance foreign key resolves to the parent AllergyIntolerance."""
    parent = AllergyIntoleranceFactory.create()
    coding = AllergyIntoleranceReactionFactory.create(allergy_intolerance=parent)

    fetched = AllergyIntoleranceReaction.objects.get(dbid=coding.dbid)

    assert fetched.allergy_intolerance == parent
