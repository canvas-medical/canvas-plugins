from django.db import models

from canvas_sdk.v1.data import Patient
from canvas_sdk.v1.data.base import CommittableModelManager
from canvas_sdk.v1.data.user import CanvasUser


class ResponseOptionSet(models.Model):
    """ResponseOptionSet."""

    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_responseoptionset_001"

    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    status = models.CharField()
    name = models.CharField()
    code_system = models.CharField()
    code = models.CharField()
    type = models.CharField()
    use_in_shx = models.BooleanField()


class ResponseOption(models.Model):
    """ResponseOption."""

    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_responseoption_001"

    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    status = models.CharField()
    name = models.CharField()
    code = models.CharField()
    code_description = models.CharField()
    value = models.CharField()
    response_option_set = models.ForeignKey(
        ResponseOptionSet, on_delete=models.CASCADE, related_name="options"
    )
    ordering = models.IntegerField()


class Question(models.Model):
    """Question."""

    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_question_001"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    status = models.CharField()
    name = models.CharField()
    response_option_set = models.ForeignKey(
        ResponseOptionSet, on_delete=models.CASCADE, related_name="questions"
    )
    acknowledge_only = models.BooleanField()
    show_prologue = models.BooleanField()
    code_system = models.CharField()
    code = models.CharField()


class Questionnaire(models.Model):
    """Questionnaire."""

    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_questionnaire_001"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    status = models.CharField()
    # graph_header
    # graph_nodes
    # graph_edges
    name = models.CharField()
    expected_completion_time = models.FloatField()
    can_originate_in_charting = models.BooleanField()
    use_case_in_charting = models.CharField()
    scoring_function_name = models.TextField()
    scoring_code_system = models.CharField()
    scoring_code = models.CharField()
    code_system = models.CharField()
    code = models.CharField()
    search_tags = models.CharField()
    # TODO: Need to bring over questionnaire question map?
    # questions = models.ManyToManyField(Question, through="QuestionnaireQuestionMap")
    use_in_shx = models.BooleanField()
    carry_forward = models.TextField()


class Interview(models.Model):
    """Interview."""

    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_interview_001"

    objects = CommittableModelManager()

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    deleted = models.BooleanField()
    committer = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING)
    entered_in_error = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING)
    status = models.CharField()
    # graph_header
    # graph_nodes
    # graph_edges
    # skipped_questions
    name = models.CharField()
    language_id = models.BigIntegerField()
    use_case_in_charting = models.CharField()
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="interviews")
    note_id = models.BigIntegerField()
    appointment_id = models.BigIntegerField()
    # TODO: Need to bring over interview quesiton map?
    # questionnaires = models.ManyToManyField(Questionnaire, through="InterviewQuestionnaireMap")
    # data = models.JSONField()
    progress_status = models.CharField()
    created = models.DateTimeField()
    modified = models.DateTimeField()


class InterviewQuestionResponse(models.Model):
    """InterviewQuestionResponse."""

    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_interviewquestionresponse_001"

    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    status = models.CharField()
    interview = models.ForeignKey(
        Interview, on_delete=models.CASCADE, related_name="interview_responses"
    )
    questionnaire = models.ForeignKey(
        Questionnaire, on_delete=models.CASCADE, related_name="interview_responses"
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="interview_responses"
    )
    response_option = models.ForeignKey(
        ResponseOption, on_delete=models.CASCADE, related_name="interview_responses"
    )
    response_option_value = models.TextField()
    questionnaire_state = models.TextField()
    interview_state = models.TextField()
    comment = models.CharField()
