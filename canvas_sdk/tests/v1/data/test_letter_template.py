import pytest

from canvas_sdk.test_utils.factories import (
    LetterLanguageTemplateFactory,
    LetterTemplateFactory,
)
from canvas_sdk.v1.data.letter import (
    LetterLanguageTemplate,
    LetterTemplate,
    LetterTemplateType,
)


def test_letter_template_type_choices() -> None:
    """The template-type choices mirror the categories home-app exposes."""
    assert LetterTemplateType.INTERVENTION.value == "intervention"
    assert LetterTemplateType.LETTER.value == "letter"
    assert LetterTemplateType.MESSAGE.value == "message"


def test_letter_template_fields() -> None:
    """A template exposes its name, flags, categories, and locations."""
    template = LetterTemplate()
    template.name = "Referral Letter"
    template.active = True
    template.restrict_editing = False
    template.template_type = [LetterTemplateType.LETTER]
    template.locations = ["1", "2"]

    assert template.name == "Referral Letter"
    assert template.active is True
    assert template.restrict_editing is False
    assert template.template_type == [LetterTemplateType.LETTER]
    assert template.locations == ["1", "2"]


def test_letter_language_template_fields() -> None:
    """A language template exposes its header, content, footer, and FKs."""
    language_template = LetterLanguageTemplate()
    language_template.template_id = 5
    language_template.language_id = 7
    language_template.header = "Header text"
    language_template.content = "Body text"
    language_template.footer = "Footer text"

    assert language_template.template_id == 5
    assert language_template.language_id == 7
    assert language_template.header == "Header text"
    assert language_template.content == "Body text"
    assert language_template.footer == "Footer text"


@pytest.mark.django_db
def test_template_languages_reverse_relation() -> None:
    """A template reaches its language content through the template_languages relation."""
    template = LetterTemplateFactory()
    language_template = LetterLanguageTemplateFactory(template=template, content="Dear patient")

    assert list(template.template_languages.all()) == [language_template]
    assert template.template_languages.get().content == "Dear patient"
