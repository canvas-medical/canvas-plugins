from collections.abc import Container
from typing import cast

from django.db import models
from django.db.models import Q

from canvas_sdk.v1.data.base import (
    BaseModelManager,
    BaseQuerySet,
    CommittableQuerySetMixin,
    ForPatientQuerySetMixin,
    IdentifiableModel,
    Model,
    ValueSetLookupByNameQuerySet,
)


class ResponseOptionSet(Model):
    """ResponseOptionSet."""

    class Meta:
        db_table = "canvas_sdk_data_api_responseoptionset_001"

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2)
    name = models.CharField(max_length=255)
    code_system = models.CharField(max_length=255)
    code = models.CharField(max_length=100)
    type = models.CharField(max_length=4)
    use_in_shx = models.BooleanField()


class ResponseOption(Model):
    """ResponseOption."""

    class Meta:
        db_table = "canvas_sdk_data_api_responseoption_001"

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=100)
    code_description = models.CharField(max_length=255)
    value = models.CharField(max_length=1000)
    response_option_set = models.ForeignKey(
        ResponseOptionSet, on_delete=models.DO_NOTHING, related_name="options", null=True
    )
    ordering = models.IntegerField()


class Question(IdentifiableModel):
    """Question."""

    class Meta:
        db_table = "canvas_sdk_data_api_question_001"

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2)
    name = models.CharField(max_length=255)
    response_option_set = models.ForeignKey(
        ResponseOptionSet, on_delete=models.DO_NOTHING, related_name="questions", null=True
    )
    acknowledge_only = models.BooleanField()
    show_prologue = models.BooleanField()
    code_system = models.CharField(max_length=255)
    code = models.CharField(max_length=100)


class QuestionnaireValueSetLookupQuerySet(ValueSetLookupByNameQuerySet):
    """QuerySet class for Questionaire ValueSet lookups."""

    @staticmethod
    def q_object(system: str, codes: Container[str]) -> Q:
        """The code system and code values for a Questionnaire are just attributes on the model."""
        return Q(code_system=system, code__in=codes)


class Questionnaire(IdentifiableModel):
    """Questionnaire."""

    class Meta:
        db_table = "canvas_sdk_data_api_questionnaire_001"

    objects = models.Manager.from_queryset(QuestionnaireValueSetLookupQuerySet)()

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
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


class QuestionnaireQuestionMap(Model):
    """QuestionnaireQuestionMap."""

    class Meta:
        db_table = "canvas_sdk_data_api_questionnairequestionmap_001"

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2)
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.DO_NOTHING, null=True)
    question = models.ForeignKey(Question, on_delete=models.DO_NOTHING, null=True)


class InterviewQuerySet(BaseQuerySet, ForPatientQuerySetMixin, CommittableQuerySetMixin):
    """InterviewQuerySet."""

    pass


InterviewManager = BaseModelManager.from_queryset(InterviewQuerySet)


class Interview(IdentifiableModel):
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
    questionnaires = models.ManyToManyField(
        Questionnaire,
        through="v1.InterviewQuestionnaireMap",
    )
    progress_status = models.CharField(max_length=3)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class InterviewQuestionnaireMap(Model):
    """InterviewQuestionnaireMap."""

    class Meta:
        db_table = "canvas_sdk_data_api_interviewquestionnairemap_001"

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2)
    interview = models.ForeignKey(Interview, on_delete=models.DO_NOTHING, null=True)
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.DO_NOTHING, null=True)


class InterviewQuestionResponse(Model):
    """InterviewQuestionResponse."""

    class Meta:
        db_table = "canvas_sdk_data_api_interviewquestionresponse_001"

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
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
    questionnaire_state = models.TextField()
    interview_state = models.TextField()
    comment = models.CharField(max_length=1024)


__exports__ = (
    "ResponseOptionSet",
    "ResponseOption",
    "Question",
    "Questionnaire",
    "QuestionnaireQuestionMap",
    "InterviewQuerySet",
    "Interview",
    "InterviewQuestionnaireMap",
    "InterviewQuestionResponse",
)
