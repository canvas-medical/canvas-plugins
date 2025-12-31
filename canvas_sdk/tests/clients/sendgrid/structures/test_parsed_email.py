import pytest

from canvas_sdk.clients.sendgrid.structures.parsed_attachment import ParsedAttachment
from canvas_sdk.clients.sendgrid.structures.parsed_email import ParsedEmail
from canvas_sdk.clients.sendgrid.structures.parsed_envelope import ParsedEnvelope
from canvas_sdk.clients.sendgrid.structures.parsed_header import ParsedHeader
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test ParsedEmail dataclass has correct field types."""
    tested = ParsedEmail
    fields = {
        "headers": list[ParsedHeader],
        "charsets": dict[str, str],
        "envelope": ParsedEnvelope,
        "email_from": str,
        "email_to": str,
        "subject": str,
        "text": str,
        "html": str,
        "attachments": int,
        "attachment_info": dict[str, ParsedAttachment],
        "content_ids": dict[str, str],
        "spf": str,
        "dkim": str,
        "spam_report": list[str],
        "spam_score": float,
    }
    assert is_dataclass(tested, fields)


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        pytest.param(
            {
                "headers": "From: sender@example.com\nTo: recipient@example.com\nSubject: Test Email",
                "charsets": '{"to": "UTF-8", "subject": "UTF-8"}',
                "envelope": '{"from": "sender@example.com", "to": ["recipient@example.com"]}',
                "from": "sender@example.com",
                "to": "recipient@example.com",
                "subject": "Test Email",
                "text": "This is a test email",
                "html": "<p>This is a test email</p>",
                "SPF": "pass",
                "dkim": "{@example.com : pass}",
            },
            ParsedEmail(
                headers=[
                    ParsedHeader(name="From", value="sender@example.com"),
                    ParsedHeader(name="To", value="recipient@example.com"),
                    ParsedHeader(name="Subject", value="Test Email"),
                ],
                charsets={"to": "UTF-8", "subject": "UTF-8"},
                envelope=ParsedEnvelope(
                    email_from="sender@example.com",
                    email_to=["recipient@example.com"],
                ),
                email_from="sender@example.com",
                email_to="recipient@example.com",
                subject="Test Email",
                text="This is a test email",
                html="<p>This is a test email</p>",
                attachments=0,
                attachment_info={},
                content_ids={},
                spf="pass",
                dkim="{@example.com : pass}",
                spam_report=[],
                spam_score=0.0,
            ),
            id="basic_email_no_attachments",
        ),
        pytest.param(
            {
                "headers": "From: sender@example.com\nTo: recipient@example.com\nSubject: Email with Attachment",
                "charsets": '{"to": "UTF-8", "subject": "UTF-8", "text": "UTF-8"}',
                "envelope": '{"from": "sender@example.com", "to": ["recipient@example.com"]}',
                "from": "sender@example.com",
                "to": "recipient@example.com",
                "subject": "Email with Attachment",
                "text": "Please find attached",
                "html": "<p>Please find attached</p>",
                "attachments": "1",
                "attachment_info": '{"attachment1": {"filename": "document.pdf", "name": "document", "type": "application/pdf", "content-id": "attach123"}}',
                "content-ids": '{"attach123": "document.pdf"}',
                "SPF": "pass",
                "dkim": "{@example.com : pass}",
                "spam_score": "0.5",
                "spam_report": "Spam detection software, running on the system\nhas NOT identified this incoming email as spam",
            },
            ParsedEmail(
                headers=[
                    ParsedHeader(name="From", value="sender@example.com"),
                    ParsedHeader(name="To", value="recipient@example.com"),
                    ParsedHeader(name="Subject", value="Email with Attachment"),
                ],
                charsets={"to": "UTF-8", "subject": "UTF-8", "text": "UTF-8"},
                envelope=ParsedEnvelope(
                    email_from="sender@example.com",
                    email_to=["recipient@example.com"],
                ),
                email_from="sender@example.com",
                email_to="recipient@example.com",
                subject="Email with Attachment",
                text="Please find attached",
                html="<p>Please find attached</p>",
                attachments=1,
                attachment_info={
                    "attachment1": ParsedAttachment(
                        filename="document.pdf",
                        name="document",
                        type="application/pdf",
                        content_id="attach123",
                    )
                },
                content_ids={"attach123": "document.pdf"},
                spf="pass",
                dkim="{@example.com : pass}",
                spam_report=[
                    "Spam detection software, running on the system",
                    "has NOT identified this incoming email as spam",
                ],
                spam_score=0.5,
            ),
            id="email_with_attachment",
        ),
    ],
)
def test_from_dict(data: dict, expected: ParsedEmail) -> None:
    """Test ParsedEmail.from_dict creates instance from dictionary."""
    test = ParsedEmail
    result = test.from_dict(data)
    assert result == expected


@pytest.mark.parametrize(
    ("parsed_email", "expected"),
    [
        pytest.param(
            ParsedEmail(
                headers=[
                    ParsedHeader(name="From", value="sender@example.com"),
                    ParsedHeader(name="To", value="recipient@example.com"),
                    ParsedHeader(name="Subject", value="Test Email"),
                ],
                charsets={"to": "UTF-8", "subject": "UTF-8"},
                envelope=ParsedEnvelope(
                    email_from="sender@example.com",
                    email_to=["recipient@example.com"],
                ),
                email_from="sender@example.com",
                email_to="recipient@example.com",
                subject="Test Email",
                text="This is a test email",
                html="<p>This is a test email</p>",
                attachments=0,
                attachment_info={},
                content_ids={},
                spf="pass",
                dkim="{@example.com : pass}",
                spam_report=[],
                spam_score=0.0,
            ),
            {
                "headers": [
                    {"name": "From", "value": "sender@example.com"},
                    {"name": "To", "value": "recipient@example.com"},
                    {"name": "Subject", "value": "Test Email"},
                ],
                "charsets": {"to": "UTF-8", "subject": "UTF-8"},
                "envelope": {
                    "emailFrom": "sender@example.com",
                    "emailTo": ["recipient@example.com"],
                },
                "emailFrom": "sender@example.com",
                "emailTo": "recipient@example.com",
                "subject": "Test Email",
                "text": "This is a test email",
                "html": "<p>This is a test email</p>",
                "attachments": 0,
                "attachmentInfo": {},
                "contentIds": {},
                "spf": "pass",
                "dkim": "{@example.com : pass}",
                "spamReport": [],
                "spamScore": "0.0",
            },
            id="basic_email_no_attachments",
        ),
        pytest.param(
            ParsedEmail(
                headers=[
                    ParsedHeader(name="From", value="sender@example.com"),
                    ParsedHeader(name="Subject", value="Email with Attachment"),
                ],
                charsets={"to": "UTF-8"},
                envelope=ParsedEnvelope(
                    email_from="sender@example.com",
                    email_to=["recipient@example.com"],
                ),
                email_from="sender@example.com",
                email_to="recipient@example.com",
                subject="Email with Attachment",
                text="Please find attached",
                html="<p>Please find attached</p>",
                attachments=2,
                attachment_info={
                    "attachment1": ParsedAttachment(
                        filename="document.pdf",
                        name="document",
                        type="application/pdf",
                        content_id="attach123",
                    ),
                    "attachment2": ParsedAttachment(
                        filename="image.png",
                        name="logo",
                        type="image/png",
                        content_id="img456",
                    ),
                },
                content_ids={"attach123": "document.pdf", "img456": "image.png"},
                spf="pass",
                dkim="{@example.com : pass}",
                spam_report=["Line 1", "Line 2"],
                spam_score=1.25,
            ),
            {
                "headers": [
                    {"name": "From", "value": "sender@example.com"},
                    {"name": "Subject", "value": "Email with Attachment"},
                ],
                "charsets": {"to": "UTF-8"},
                "envelope": {
                    "emailFrom": "sender@example.com",
                    "emailTo": ["recipient@example.com"],
                },
                "emailFrom": "sender@example.com",
                "emailTo": "recipient@example.com",
                "subject": "Email with Attachment",
                "text": "Please find attached",
                "html": "<p>Please find attached</p>",
                "attachments": 2,
                "attachmentInfo": {
                    "attachment1": {
                        "filename": "document.pdf",
                        "name": "document",
                        "type": "application/pdf",
                        "contentId": "attach123",
                    },
                    "attachment2": {
                        "filename": "image.png",
                        "name": "logo",
                        "type": "image/png",
                        "contentId": "img456",
                    },
                },
                "contentIds": {"attach123": "document.pdf", "img456": "image.png"},
                "spf": "pass",
                "dkim": "{@example.com : pass}",
                "spamReport": ["Line 1", "Line 2"],
                "spamScore": "1.25",
            },
            id="email_with_multiple_attachments",
        ),
    ],
)
def test_to_dict(parsed_email: ParsedEmail, expected: dict) -> None:
    """Test ParsedEmail.to_dict converts instance to dictionary."""
    result = parsed_email.to_dict()
    assert result == expected
