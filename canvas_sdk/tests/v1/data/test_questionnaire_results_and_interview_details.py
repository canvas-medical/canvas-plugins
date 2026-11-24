import pytest

from canvas_sdk.test_utils.factories import (
    CanvasUserFactory,
    InterviewFactory,
    PatientFactory,
    QuestionnaireFactory,
    QuestionnaireItemGroupFactory,
    QuestionnaireQuestionMapFactory,
    QuestionnaireResultFactory,
)
from canvas_sdk.v1.data import (
    Interview,
    Patient,
    Questionnaire,
    QuestionnaireItemGroup,
    QuestionnaireQuestionMap,
    QuestionnaireResult,
)


@pytest.mark.django_db
def test_questionnaire_result_is_reachable_from_interview_questionnaire_and_patient() -> None:
    """A scored result resolves from its interview, its questionnaire and its patient."""
    result = QuestionnaireResultFactory.create(score=17.0, abnormal=True, narrative="Moderate")
    QuestionnaireResultFactory.create()

    interview = Interview.objects.get(id=result.interview.id)
    questionnaire = Questionnaire.objects.get(id=result.questionnaire.id)
    patient = Patient.objects.get(id=result.patient.id)

    assert list(interview.questionnaire_results.all()) == [result]
    assert list(questionnaire.questionnaire_results.all()) == [result]
    assert list(patient.questionnaire_results.all()) == [result]
    fetched = interview.questionnaire_results.get()
    assert (fetched.score, fetched.abnormal, fetched.narrative) == (17.0, True, "Moderate")


@pytest.mark.django_db
def test_questionnaire_result_score_can_be_empty() -> None:
    """An unscored result has no score."""
    result = QuestionnaireResultFactory.create(score=None)

    assert Interview.objects.get(id=result.interview.id).questionnaire_results.get().score is None


@pytest.mark.django_db
def test_committed_results_exclude_uncommitted_and_entered_in_error_interviews() -> None:
    """committed() keeps only results from signed interviews not entered in error."""
    user = CanvasUserFactory.create()
    patient = PatientFactory.create()
    signed = QuestionnaireResultFactory.create(
        interview=InterviewFactory.create(patient=patient, committer=user)
    )
    QuestionnaireResultFactory.create(interview=InterviewFactory.create(patient=patient))
    QuestionnaireResultFactory.create(
        interview=InterviewFactory.create(patient=patient, committer=user, entered_in_error=user)
    )

    assert list(Patient.objects.get(id=patient.id).questionnaire_results.committed()) == [signed]


@pytest.mark.django_db
def test_default_result_sits_on_a_committed_interview() -> None:
    """A result built with factory defaults is committed, as home-app writes results on commit."""
    result = QuestionnaireResultFactory.create()

    assert list(QuestionnaireResult.objects.committed()) == [result]


@pytest.mark.django_db
def test_item_groups_nest_under_a_questionnaire_a_group_and_a_question() -> None:
    """Item groups resolve from their questionnaire, parent group and parent question."""
    questionnaire = QuestionnaireFactory.create()
    question_map = QuestionnaireQuestionMapFactory.create(questionnaire=questionnaire)
    top = QuestionnaireItemGroupFactory.create(questionnaire=questionnaire, ordering=0)
    nested = QuestionnaireItemGroupFactory.create(
        questionnaire=questionnaire, parent_group=top, ordering=1
    )
    under_question = QuestionnaireItemGroupFactory.create(
        questionnaire=questionnaire, parent_question_map=question_map, ordering=2
    )

    fetched = Questionnaire.objects.get(id=questionnaire.id)

    assert list(fetched.item_groups.order_by("ordering")) == [top, nested, under_question]
    assert list(QuestionnaireItemGroup.objects.get(id=top.id).child_item_groups.all()) == [nested]
    assert list(
        QuestionnaireQuestionMap.objects.get(dbid=question_map.dbid).child_item_groups.all()
    ) == [under_question]
    assert QuestionnaireItemGroup.objects.get(id=nested.id).parent_group == top
    assert QuestionnaireItemGroup.objects.get(id=top.id).parent_group is None
