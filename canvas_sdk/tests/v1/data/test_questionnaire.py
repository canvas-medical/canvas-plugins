from django.db import models
from django.db.models import Q

from canvas_sdk.v1.data.questionnaire import InterviewQuerySet, InterviewQuestionResponse
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


def test_interview_question_response_exposes_the_date_answer() -> None:
    """A date answer is available as a real date, and is null for other question types."""
    field = InterviewQuestionResponse._meta.get_field("response_option_date")
    assert isinstance(field, models.DateField)
    assert field.null
