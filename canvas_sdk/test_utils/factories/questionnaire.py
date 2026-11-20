import factory

from canvas_sdk.v1.data import Interview, Question


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
