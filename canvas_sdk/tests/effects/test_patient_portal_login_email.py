import json

import pytest
from pydantic import ValidationError

from canvas_sdk.effects.base import EffectType
from canvas_sdk.effects.patient_portal.login_email import LoginEmailContent


def test_effect_carries_subject_and_body() -> None:
    """The payload carries the subject and the HTML body as given."""
    applied = LoginEmailContent(
        subject="Welcome to the Lanby portal",
        html_body='<p>Set your password: <a href="https://x/app/reset/?access_token=a&amp;next=%2F">here</a></p>',
    ).apply()

    assert applied.type == EffectType.PATIENT_PORTAL__LOGIN_EMAIL_CONTENT
    assert json.loads(applied.payload) == {
        "data": {
            "subject": "Welcome to the Lanby portal",
            "html_body": '<p>Set your password: <a href="https://x/app/reset/?access_token=a&amp;next=%2F">here</a></p>',
        }
    }


@pytest.mark.parametrize("subject", ["", "   "])
def test_subject_must_not_be_empty(subject: str) -> None:
    """An empty or blank subject is rejected."""
    with pytest.raises(ValidationError):
        LoginEmailContent(subject=subject, html_body="<p>body</p>").apply()


@pytest.mark.parametrize("html_body", ["", "  \n "])
def test_html_body_must_not_be_empty(html_body: str) -> None:
    """An empty or blank body is rejected."""
    with pytest.raises(ValidationError):
        LoginEmailContent(subject="Welcome", html_body=html_body).apply()


@pytest.mark.parametrize("subject", ["Welcome\nBcc: x@example.com", "Welcome\r", "Wel\r\ncome"])
def test_subject_must_not_contain_a_line_break(subject: str) -> None:
    """A line break in the subject is rejected, since it breaks the email header."""
    with pytest.raises(ValidationError):
        LoginEmailContent(subject=subject, html_body="<p>body</p>").apply()


def test_html_body_may_contain_line_breaks() -> None:
    """Line breaks in the body are ordinary HTML."""
    applied = LoginEmailContent(subject="Welcome", html_body="<p>one</p>\n<p>two</p>").apply()

    assert json.loads(applied.payload)["data"]["html_body"] == "<p>one</p>\n<p>two</p>"


def test_unknown_field_is_rejected() -> None:
    """A misspelled field is an error, so it does not silently do nothing."""
    with pytest.raises(ValidationError):
        LoginEmailContent(subject="Welcome", html_body="<p>body</p>", from_name="Lanby")  # type: ignore[call-arg]
