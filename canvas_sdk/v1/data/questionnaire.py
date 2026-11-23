from collections.abc import Container
from typing import Self, cast

from django.db import models
from django.db.models import Q

from canvas_sdk.v1.data.base import (
    AuditedModel,
    BaseModelManager,
    BaseQuerySet,
    CommittableQuerySetMixin,
    ForPatientQuerySetMixin,
    IdentifiableModel,
    Model,
    TimestampedModel,
    ValueSetLookupByNameQuerySet,
    ValueSetLookupByNameQuerySetMixin,
)


class QuestionnaireStatus(models.TextChoices):
    """Active status of questionnaire catalog rows."""

    ACTIVE = "AC", "Active"
    INACTIVE = "IN", "Inactive"


class QuestionnaireUseCase(models.TextChoices):
    """Where a questionnaire or interview template is used in charting."""

    QUESTIONNAIRE = "QUES", "Questionnaire"
    REVIEW_OF_SYSTEMS = "ROS", "Review of Systems"
    PHYSICAL_EXAM = "EXAM", "Physical Exam"
    STRUCTURED_ASSESSMENT = "SA", "Structured Assessment"


class ResponseOptionSet(TimestampedModel):
    """ResponseOptionSet."""

    class Meta:
        db_table = "canvas_sdk_data_api_responseoptionset_001"

    status = models.CharField(max_length=2)
    name = models.CharField(max_length=255)
    code_system = models.CharField(max_length=255)
    code = models.CharField(max_length=100)
    type = models.CharField(max_length=4)
    use_in_shx = models.BooleanField()


class ResponseOption(TimestampedModel):
    """ResponseOption."""

    class Meta:
        db_table = "canvas_sdk_data_api_responseoption_001"

    status = models.CharField(max_length=2)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=100)
    code_description = models.CharField(max_length=255)
    value = models.CharField(max_length=1000)
    response_option_set = models.ForeignKey(
        ResponseOptionSet, on_delete=models.DO_NOTHING, related_name="options", null=True
    )
    ordering = models.IntegerField()


class Question(TimestampedModel, IdentifiableModel):
    """Question."""

    class Meta:
        db_table = "canvas_sdk_data_api_question_001"

    status = models.CharField(max_length=2)
    name = models.CharField(max_length=255)
    response_option_set = models.ForeignKey(
        ResponseOptionSet, on_delete=models.DO_NOTHING, related_name="questions", null=True
    )
    acknowledge_only = models.BooleanField()
    show_prologue = models.BooleanField()
    code_system = models.CharField(max_length=255)
    code = models.CharField(max_length=100)
    enable_behavior = models.CharField(max_length=4, null=True)


class QuestionEnablementCondition(TimestampedModel):
    """A condition controlling when a Question is enabled, following FHIR's enableWhen pattern."""

    class Meta:
        db_table = "canvas_sdk_data_api_questionenablementcondition_001"

    status = models.CharField(max_length=2)
    question = models.ForeignKey(
        Question, on_delete=models.DO_NOTHING, related_name="dependent_conditions"
    )
    dependent_on = models.ForeignKey(
        Question, on_delete=models.DO_NOTHING, related_name="triggers_condition"
    )
    operator = models.CharField(max_length=10)
    answer_option = models.ForeignKey(
        ResponseOption,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="enablement_conditions",
    )
    answer_value = models.CharField(max_length=255, null=True)


class QuestionnaireValueSetLookupQuerySet(ValueSetLookupByNameQuerySet):
    """QuerySet class for Questionaire ValueSet lookups."""

    @staticmethod
    def q_object(system: str, codes: Container[str]) -> Q:
        """The code system and code values for a Questionnaire are just attributes on the model."""
        return Q(code_system=system, code__in=codes)


class Questionnaire(TimestampedModel, IdentifiableModel):
    """Questionnaire."""

    class Meta:
        db_table = "canvas_sdk_data_api_questionnaire_001"

    objects = models.Manager.from_queryset(QuestionnaireValueSetLookupQuerySet)()

    status = models.CharField(max_length=2)
    name = models.CharField(max_length=255)
    expected_completion_time = models.FloatField()
    can_originate_in_charting = models.BooleanField()
    use_case_in_charting = models.CharField(max_length=4)
    scoring_function_name = models.TextField()
    scoring_code_system = models.CharField(max_length=255)
    scoring_code = models.CharField(max_length=100)
    code_system = models.CharField(max_length=255)
    code = models.CharField(max_length=100)
    search_tags = models.CharField(max_length=500)
    questions = models.ManyToManyField(Question, through="v1.QuestionnaireQuestionMap")
    use_in_shx = models.BooleanField()
    carry_forward = models.TextField()


class QuestionnaireQuestionMap(TimestampedModel):
    """QuestionnaireQuestionMap."""

    class Meta:
        db_table = "canvas_sdk_data_api_questionnairequestionmap_001"

    status = models.CharField(max_length=2)
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.DO_NOTHING, null=True)
    question = models.ForeignKey(Question, on_delete=models.DO_NOTHING, null=True)


class InterviewQuerySet(
    ForPatientQuerySetMixin,
    CommittableQuerySetMixin,
    ValueSetLookupByNameQuerySetMixin,
    BaseQuerySet,
):
    """InterviewQuerySet."""

    @staticmethod
    def q_object(system: str, codes: Container[str]) -> Q:
        """Match interviews whose questionnaire has a code in the value set.

        Code system names (e.g. "LOINC") and codes live on the related
        Questionnaire, so the lookup goes through the ``questionnaires`` M2M.
        """
        return Q(questionnaires__code_system=system, questionnaires__code__in=codes)


InterviewManager = BaseModelManager.from_queryset(InterviewQuerySet)


class Interview(TimestampedModel, IdentifiableModel):
    """Interview."""

    class Meta:
        db_table = "canvas_sdk_data_api_interview_001"

    objects = cast(InterviewQuerySet, InterviewManager())

    deleted = models.BooleanField()
    committer = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    entered_in_error = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    status = models.CharField(max_length=2)
    name = models.CharField(max_length=255)
    language_id = models.BigIntegerField()
    use_case_in_charting = models.CharField(max_length=4)
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="interviews", null=True
    )
    note_id = models.BigIntegerField()
    appointment_id = models.BigIntegerField()
    assessment = models.ForeignKey(
        "v1.Assessment",
        on_delete=models.DO_NOTHING,
        related_name="linked_interviews",
        null=True,
    )
    questionnaires = models.ManyToManyField(
        Questionnaire,
        through="v1.InterviewQuestionnaireMap",
    )
    progress_status = models.CharField(max_length=3)
    skipped_questions = models.ManyToManyField(Question, through="v1.InterviewSkippedQuestion")


class InterviewQuestionnaireMap(TimestampedModel):
    """InterviewQuestionnaireMap."""

    class Meta:
        db_table = "canvas_sdk_data_api_interviewquestionnairemap_001"

    status = models.CharField(max_length=2)
    interview = models.ForeignKey(Interview, on_delete=models.DO_NOTHING, null=True)
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.DO_NOTHING, null=True)


class InterviewSkippedQuestion(Model):
    """M2M for Interview -> Questions skipped in it."""

    class Meta:
        db_table = "canvas_sdk_data_api_interview_skipped_questions_001"

    interview = models.ForeignKey(Interview, on_delete=models.DO_NOTHING, related_name="+")
    question = models.ForeignKey(Question, on_delete=models.DO_NOTHING, related_name="+")


class InterviewQuestionResponse(TimestampedModel):
    """InterviewQuestionResponse."""

    class Meta:
        db_table = "canvas_sdk_data_api_interviewquestionresponse_001"

    status = models.CharField(max_length=2)
    interview = models.ForeignKey(
        Interview, on_delete=models.DO_NOTHING, related_name="interview_responses", null=True
    )
    questionnaire = models.ForeignKey(
        Questionnaire, on_delete=models.DO_NOTHING, related_name="interview_responses", null=True
    )
    question = models.ForeignKey(
        Question, on_delete=models.DO_NOTHING, related_name="interview_responses", null=True
    )
    response_option = models.ForeignKey(
        ResponseOption, on_delete=models.DO_NOTHING, related_name="interview_responses", null=True
    )
    response_option_value = models.TextField()
    response_option_date = models.DateField(null=True, blank=True)
    questionnaire_state = models.TextField()
    interview_state = models.TextField()
    comment = models.CharField(max_length=1024)


class QuestionnaireItemGroup(TimestampedModel, IdentifiableModel):
    """A group of items in a questionnaire, nested under another group or a question."""

    class Meta:
        db_table = "canvas_sdk_data_api_questionnaireitemgroup_001"

    questionnaire = models.ForeignKey(
        Questionnaire, on_delete=models.DO_NOTHING, related_name="item_groups"
    )
    parent_group = models.ForeignKey(
        "self", on_delete=models.DO_NOTHING, null=True, related_name="child_item_groups"
    )
    parent_question_map = models.ForeignKey(
        QuestionnaireQuestionMap,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="child_item_groups",
    )
    ordering = models.PositiveIntegerField()


class QuestionnaireResultQuerySet(BaseQuerySet):
    """QuestionnaireResultQuerySet."""

    def committed(self) -> Self:
        """Return results whose interview is committed and not entered in error."""
        return self.filter(
            interview__committer__isnull=False, interview__entered_in_error__isnull=True
        )


class QuestionnaireResult(TimestampedModel):
    """A questionnaire's scored result in an interview."""

    class Meta:
        db_table = "canvas_sdk_data_api_questionnaireresult_001"

    objects = cast(
        QuestionnaireResultQuerySet,
        models.Manager.from_queryset(QuestionnaireResultQuerySet)(),
    )

    interview = models.ForeignKey(
        Interview, on_delete=models.DO_NOTHING, related_name="questionnaire_results"
    )
    questionnaire = models.ForeignKey(
        Questionnaire, on_delete=models.DO_NOTHING, related_name="questionnaire_results"
    )
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="questionnaire_results"
    )
    score = models.FloatField(null=True)
    abnormal = models.BooleanField()
    narrative = models.CharField(max_length=1256)
    code_system = models.CharField(max_length=100)
    code = models.CharField(max_length=100)


class InterviewTemplate(TimestampedModel):
    """A reusable set of questionnaires an interview can start from."""

    class Meta:
        db_table = "canvas_sdk_data_api_interviewtemplate_001"

    status = models.CharField(max_length=2, choices=QuestionnaireStatus.choices)
    name = models.CharField(max_length=255)
    language_id = models.IntegerField()
    use_case_in_charting = models.CharField(max_length=4, choices=QuestionnaireUseCase.choices)
    questionnaires = models.ManyToManyField(
        Questionnaire,
        through="v1.InterviewTemplateQuestionnaireMap",
        related_name="interview_templates",
    )


class InterviewTemplateQuestionnaireMap(TimestampedModel):
    """A questionnaire included in an interview template."""

    class Meta:
        db_table = "canvas_sdk_data_api_interviewtemplatequestionnairemap_001"

    status = models.CharField(max_length=2, choices=QuestionnaireStatus.choices)
    interview_template = models.ForeignKey(
        InterviewTemplate, on_delete=models.DO_NOTHING, related_name="+"
    )
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.DO_NOTHING, related_name="+")


class InterviewSendEvent(TimestampedModel):
    """An attempt to send an interview to the patient by email or text message."""

    class Meta:
        db_table = "canvas_sdk_data_api_interviewsendevent_001"

    interview = models.ForeignKey(
        Interview, on_delete=models.DO_NOTHING, related_name="send_events"
    )
    consent_remark = models.CharField(max_length=100)
    to_email = models.CharField(max_length=255)
    email_succeeded = models.BooleanField()
    to_phone = models.CharField(max_length=50)
    text_message_succeeded = models.BooleanField()


class InterviewVisualFinding(AuditedModel):
    """Media attached to an interview."""

    class Meta:
        db_table = "canvas_sdk_data_api_interviewvisualfinding_001"

    objects = BaseModelManager()

    interview = models.ForeignKey(
        Interview, on_delete=models.DO_NOTHING, related_name="visual_findings"
    )
    media_url = models.URLField(null=True)


__exports__ = (
    "QuestionnaireStatus",
    "QuestionnaireUseCase",
    "QuestionnaireItemGroup",
    "QuestionnaireResult",
    "QuestionnaireResultQuerySet",
    "InterviewTemplate",
    "InterviewTemplateQuestionnaireMap",
    "InterviewSendEvent",
    "InterviewVisualFinding",
    "ResponseOptionSet",
    "ResponseOption",
    "Question",
    "QuestionEnablementCondition",
    "Questionnaire",
    "QuestionnaireQuestionMap",
    "InterviewQuerySet",
    "Interview",
    "InterviewQuestionnaireMap",
    "InterviewQuestionResponse",
    "InterviewSkippedQuestion",
)
