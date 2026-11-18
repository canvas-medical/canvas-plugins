import pytest

from canvas_sdk.test_utils.factories import (
    LanguageFactory,
    LetterFactory,
    LetterLanguageTemplateFactory,
    LetterTemplateFactory,
)
from canvas_sdk.v1.data import Letter, LetterTemplate, LetterTemplateType, Message


@pytest.mark.django_db
def test_letter_template_reads_its_kinds_locations_and_languages() -> None:
    """A template is found by kind and lists its per-language content."""
    template = LetterTemplateFactory.create(
        name="Referral letter",
        restrict_editing=True,
        template_type=[LetterTemplateType.LETTER],
        locations=["1", "2"],
    )
    language = LanguageFactory.create(code="es")
    content = LetterLanguageTemplateFactory.create(
        template=template,
        language=language,
        header="Encabezado",
        content="Estimado paciente",
        footer="Pie",
    )

    fetched = LetterTemplate.objects.get(id=template.id)

    assert fetched.name == "Referral letter"
    assert fetched.active is True
    assert fetched.restrict_editing is True
    assert fetched.template_type == ["letter"]
    assert fetched.locations == ["1", "2"]
    assert list(fetched.template_languages.values_list("header", "content", "footer")) == [
        ("Encabezado", "Estimado paciente", "Pie")
    ]
    assert list(language.letter_template_contents.all()) == [content]


@pytest.mark.django_db
def test_letter_reads_its_template() -> None:
    """A letter resolves the language template it was written from, and back."""
    language_template = LetterLanguageTemplateFactory.create()
    letter = LetterFactory.create(template=language_template)
    LetterFactory.create()

    assert Letter.objects.get(id=letter.id).template == language_template
    assert list(language_template.letters.all()) == [letter]


@pytest.mark.django_db
def test_message_reads_its_template() -> None:
    """A message resolves the language template it was written from, and back."""
    language_template = LetterLanguageTemplateFactory.create()
    message = Message.objects.create(content="Hello", template=language_template)
    Message.objects.create(content="No template")

    assert Message.objects.get(id=message.id).template == language_template
    assert list(language_template.messages.all()) == [message]
