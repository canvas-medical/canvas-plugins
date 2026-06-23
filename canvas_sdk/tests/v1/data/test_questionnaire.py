from django.db.models import Q

from canvas_sdk.v1.data.questionnaire import InterviewQuerySet
from canvas_sdk.value_set.value_set import ValueSet


class _LoincSampleValueSet(ValueSet):
    """Tiny value set fixture for the find() lookup tests."""

    VALUE_SET_NAME = "Loinc Sample"
    OID = "tests.loinc-sample"
    LOINC = {"68536-0", "72166-2"}


def test_interview_queryset_find_q_object_targets_questionnaire_codes() -> None:
    """Interview.find() routes through the related Questionnaire's code_system+code."""
    expected = Q(
        questionnaires__code_system="LOINC",
        questionnaires__code__in=["68536-0", "72166-2"],
    )
    actual = InterviewQuerySet.q_object("LOINC", ["68536-0", "72166-2"])
    assert actual == expected


def test_interview_queryset_codings_uses_value_set_name_not_url() -> None:
    """Lookup uses the code system *name* (LOINC) per ValueSetLookupByNameQuerySetMixin."""
    codings = dict(InterviewQuerySet.codings(_LoincSampleValueSet))
    assert codings == {"LOINC": {"68536-0", "72166-2"}}
