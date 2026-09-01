import pytest
from django.db import models

from canvas_sdk.test_utils.factories import FamilyHistoryCodingFactory, FamilyHistoryFactory
from canvas_sdk.v1.data.family_history import FamilyHistory, FamilyHistoryCoding
from canvas_sdk.value_set.value_set import ValueSet


class _DiabetesSampleValueSet(ValueSet):
    """Tiny value set fixture for find() tests."""

    VALUE_SET_NAME = "Diabetes Sample"
    OID = "tests.diabetes-sample"
    SNOMEDCT = {"73211009"}


def test_family_history_exposes_relation_fields() -> None:
    """FamilyHistory exposes the relative's SNOMED code/term and the narrative."""
    code_field = FamilyHistory._meta.get_field("relation_snomed_code")
    assert isinstance(code_field, models.BigIntegerField)

    term_field = FamilyHistory._meta.get_field("relation_snomed_term")
    assert isinstance(term_field, models.CharField)
    assert term_field.max_length == 255


def test_family_history_coding_links_back_via_coding() -> None:
    """FamilyHistoryCoding links to FamilyHistory with a `coding` reverse accessor."""
    accessor = FamilyHistoryCoding._meta.get_field(
        "family_history"
    ).remote_field.get_accessor_name()
    assert accessor == "coding"
    assert hasattr(FamilyHistory, "coding")


@pytest.mark.django_db
def test_find_matches_via_singular_coding_accessor() -> None:
    """FamilyHistory.objects.find() resolves through the singular `coding` accessor (KOALA-6939)."""
    matching = FamilyHistoryFactory.create()
    FamilyHistoryCodingFactory.create(
        family_history=matching, system="http://snomed.info/sct", code="73211009"
    )
    other = FamilyHistoryFactory.create()
    FamilyHistoryCodingFactory.create(
        family_history=other, system="http://snomed.info/sct", code="99999999"
    )

    found = list(FamilyHistory.objects.find(_DiabetesSampleValueSet))

    assert [fh.id for fh in found] == [matching.id]
