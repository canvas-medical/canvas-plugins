from django.db import models

from canvas_sdk.v1.data.family_history import FamilyHistory, FamilyHistoryCoding


def test_family_history_exposes_relation_fields() -> None:
    """FamilyHistory exposes the relative's SNOMED code/term and the narrative."""
    code_field = FamilyHistory._meta.get_field("relation_snomed_code")
    assert isinstance(code_field, models.BigIntegerField)

    term_field = FamilyHistory._meta.get_field("relation_snomed_term")
    assert isinstance(term_field, models.CharField)
    assert term_field.max_length == 255


def test_family_history_coding_links_back_via_codings() -> None:
    """FamilyHistoryCoding links to FamilyHistory with a `codings` reverse accessor."""
    accessor = FamilyHistoryCoding._meta.get_field(
        "family_history"
    ).remote_field.get_accessor_name()
    assert accessor == "codings"
    assert hasattr(FamilyHistory, "codings")
