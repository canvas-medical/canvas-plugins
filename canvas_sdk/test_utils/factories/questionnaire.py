import factory

from canvas_sdk.v1.data import (
    Interview,
    Question,
    Questionnaire,
    QuestionnaireItemGroup,
    QuestionnaireQuestionMap,
    QuestionnaireResult,
    QuestionnaireStatus,
    QuestionnaireUseCase,
    ResponseOption,
    ResponseOptionSet,
)


class ResponseOptionSetFactory(factory.django.DjangoModelFactory[ResponseOptionSet]):
    """Factory for creating a ResponseOptionSet."""

    class Meta:
        model = ResponseOptionSet

    status = "AC"
    name = factory.Faker("word")
    code_system = "http://loinc.org"
    code = factory.Sequence(lambda n: f"LL{1000 + n}-1")
    type = "TXT"
    use_in_shx = False


class ResponseOptionFactory(factory.django.DjangoModelFactory[ResponseOption]):
    """Factory for creating a ResponseOption."""

    class Meta:
        model = ResponseOption

    status = "AC"
    name = factory.Faker("word")
    code = factory.Sequence(lambda n: f"LA{1000 + n}-1")
    code_description = ""
    value = factory.Sequence(str)
    response_option_set = factory.SubFactory(ResponseOptionSetFactory, type="SING")
    ordering = factory.Sequence(int)


class QuestionFactory(factory.django.DjangoModelFactory[Question]):
    """Factory for creating a Question."""

    class Meta:
        model = Question

    status = "AC"
    name = factory.Faker("sentence", nb_words=4)
    acknowledge_only = False
    show_prologue = False
    code_system = "http://loinc.org"
    code = factory.Sequence(lambda n: f"{10000 + n}-1")


class InterviewFactory(factory.django.DjangoModelFactory[Interview]):
    """Factory for creating an Interview."""

    class Meta:
        model = Interview

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    deleted = False
    status = "AC"
    name = ""
    language_id = 1
    use_case_in_charting = "QUES"
    note_id = 0
    appointment_id = 0
    progress_status = "F"


class QuestionnaireFactory(factory.django.DjangoModelFactory[Questionnaire]):
    """Factory for creating a Questionnaire."""

    class Meta:
        model = Questionnaire

    status = QuestionnaireStatus.ACTIVE
    name = factory.Faker("sentence", nb_words=3)
    expected_completion_time = 5.0
    can_originate_in_charting = True
    use_case_in_charting = QuestionnaireUseCase.QUESTIONNAIRE
    scoring_function_name = ""
    scoring_code_system = "http://loinc.org"
    scoring_code = "44261-6"
    code_system = "LOINC"
    code = factory.Sequence(lambda n: f"{20000 + n}-2")
    search_tags = ""
    use_in_shx = False
    carry_forward = "off"


class QuestionnaireQuestionMapFactory(factory.django.DjangoModelFactory[QuestionnaireQuestionMap]):
    """Factory for creating a QuestionnaireQuestionMap."""

    class Meta:
        model = QuestionnaireQuestionMap

    status = QuestionnaireStatus.ACTIVE
    questionnaire = factory.SubFactory(QuestionnaireFactory)
    question = factory.SubFactory(QuestionFactory)


class QuestionnaireItemGroupFactory(factory.django.DjangoModelFactory[QuestionnaireItemGroup]):
    """Factory for creating a QuestionnaireItemGroup."""

    class Meta:
        model = QuestionnaireItemGroup

    questionnaire = factory.SubFactory(QuestionnaireFactory)
    ordering = factory.Sequence(lambda n: n)


class QuestionnaireResultFactory(factory.django.DjangoModelFactory[QuestionnaireResult]):
    """Factory for creating a QuestionnaireResult."""

    class Meta:
        model = QuestionnaireResult

    # home-app writes results while committing the interview, so default to a committed one.
    interview = factory.SubFactory(
        InterviewFactory,
        committer=factory.SubFactory("canvas_sdk.test_utils.factories.CanvasUserFactory"),
    )
    questionnaire = factory.SubFactory(QuestionnaireFactory)
    patient = factory.SelfAttribute("interview.patient")
    score = 12.0
    abnormal = False
    narrative = ""
    code_system = "http://loinc.org"
    code = "44261-6"
