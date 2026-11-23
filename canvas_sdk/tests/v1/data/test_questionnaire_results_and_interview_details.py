import pytest

from canvas_sdk.test_utils.factories import (
    CanvasUserFactory,
    InterviewFactory,
    InterviewSendEventFactory,
    InterviewTemplateFactory,
    InterviewTemplateQuestionnaireMapFactory,
    InterviewVisualFindingFactory,
    PatientFactory,
    QuestionnaireFactory,
    QuestionnaireItemGroupFactory,
    QuestionnaireQuestionMapFactory,
    QuestionnaireResultFactory,
)
from canvas_sdk.v1.data import (
    Interview,
    InterviewTemplate,
    InterviewVisualFinding,
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


@pytest.mark.django_db
def test_interview_template_lists_its_questionnaires() -> None:
    """A template's questionnaires resolve through its questionnaire map, in both directions."""
    template = InterviewTemplateFactory.create()
    phq9 = InterviewTemplateQuestionnaireMapFactory.create(
        interview_template=template
    ).questionnaire
    gad7 = InterviewTemplateQuestionnaireMapFactory.create(
        interview_template=template
    ).questionnaire
    InterviewTemplateQuestionnaireMapFactory.create()

    fetched = InterviewTemplate.objects.get(dbid=template.dbid)

    assert set(fetched.questionnaires.all()) == {phq9, gad7}
    assert list(Questionnaire.objects.get(id=phq9.id).interview_templates.all()) == [template]


@pytest.mark.django_db
def test_interview_send_events_record_how_it_was_sent() -> None:
    """An interview's send events resolve with their recipients and channel outcomes."""
    interview = InterviewFactory.create()
    sent = InterviewSendEventFactory.create(
        interview=interview,
        to_email="patient@example.com",
        email_succeeded=True,
    )
    InterviewSendEventFactory.create()

    events = list(Interview.objects.get(id=interview.id).send_events.all())

    assert events == [sent]
    assert events[0].to_email == "patient@example.com"
    assert events[0].email_succeeded is True
    assert events[0].text_message_succeeded is False


@pytest.mark.django_db
def test_interview_visual_findings_hide_deleted_rows() -> None:
    """A finding with no committer, as home-app writes it, is returned; a deleted one is not."""
    interview = InterviewFactory.create()
    kept = InterviewVisualFindingFactory.create(interview=interview)
    InterviewVisualFindingFactory.create(interview=interview, deleted=True)

    assert kept.committer is None
    assert list(Interview.objects.get(id=interview.id).visual_findings.all()) == [kept]
    assert list(InterviewVisualFinding.objects.filter(interview=interview)) == [kept]


def test_visual_findings_offer_no_committed_filter() -> None:
    """Visual findings are never committed in home-app, so the manager has no committed()."""
    assert not hasattr(InterviewVisualFinding.objects, "committed")
