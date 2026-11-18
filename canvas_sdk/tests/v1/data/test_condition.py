import pytest
from django.db import models

from canvas_sdk.test_utils.factories import ConditionCategoryCodingFactory, ConditionFactory
from canvas_sdk.v1.data.condition import Condition, ConditionCategoryCoding


def test_condition_exposes_notes_field() -> None:
    """The notes field is exposed on the Condition model with the expected max_length."""
    field = Condition._meta.get_field("notes")
    assert isinstance(field, models.CharField)
    assert field.max_length == 1000


@pytest.mark.django_db
def test_condition_category_codings_return_only_its_codings() -> None:
    """Condition.category_codings returns only that condition's codings."""
    parent = ConditionFactory.create()
    coding = ConditionCategoryCodingFactory.create(condition=parent)
    ConditionCategoryCodingFactory.create()

    assert list(parent.category_codings.all()) == [coding]


@pytest.mark.django_db
def test_condition_category_coding_resolves_to_its_condition() -> None:
    """The condition foreign key resolves to the parent Condition."""
    parent = ConditionFactory.create()
    coding = ConditionCategoryCodingFactory.create(condition=parent)

    fetched = ConditionCategoryCoding.objects.get(dbid=coding.dbid)

    assert fetched.condition == parent
