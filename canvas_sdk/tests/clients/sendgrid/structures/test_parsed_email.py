from json import dumps

from canvas_sdk.clients.sendgrid.structures.parsed_attachment import ParsedAttachment
from canvas_sdk.clients.sendgrid.structures.parsed_email import ParsedEmail
from canvas_sdk.clients.sendgrid.structures.parsed_envelope import ParsedEnvelope
from canvas_sdk.clients.sendgrid.structures.parsed_header import ParsedHeader
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Verify ParsedEmail is a frozen dataclass with correct fields."""
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
    result = is_dataclass(tested, fields)
    expected = True
    assert result is expected


def test_from_dict__minimal() -> None:
    """Test creating ParsedEmail from dictionary with minimal data."""
    tested = ParsedEmail
    data = {
        "headers": "Content-Type: text/plain\nFrom: sender@example.com",
        "charsets": dumps({"to": "UTF-8", "subject": "UTF-8"}),
        "envelope": dumps({"from": "sender@example.com", "to": ["recipient@example.com"]}),
        "from": "sender@example.com",
        "to": "recipient@example.com",
        "subject": "Test Subject",
        "text": "Hello, World!",
        "html": "<p>Hello, World!</p>",
        "SPF": "pass",
        "dkim": "pass",
    }
    result = tested.from_dict(data)
    expected = ParsedEmail(
        headers=[
            ParsedHeader(name="Content-Type", value="text/plain"),
            ParsedHeader(name="From", value="sender@example.com"),
        ],
        charsets={"to": "UTF-8", "subject": "UTF-8"},
        envelope=ParsedEnvelope(
            email_from="sender@example.com", email_to=["recipient@example.com"]
        ),
        email_from="sender@example.com",
        email_to="recipient@example.com",
        subject="Test Subject",
        text="Hello, World!",
        html="<p>Hello, World!</p>",
        attachments=0,
        attachment_info={},
        content_ids={},
        spf="pass",
        dkim="pass",
        spam_report=[],
        spam_score=0.0,
    )
    assert result == expected


def test_from_dict__with_attachments() -> None:
    """Test creating ParsedEmail from dictionary with attachments."""
    tested = ParsedEmail
    data = {
        "headers": "Subject: Test",
        "charsets": dumps({"to": "UTF-8"}),
        "envelope": dumps({"from": "sender@example.com", "to": ["recipient@example.com"]}),
        "from": "sender@example.com",
        "to": "recipient@example.com",
        "subject": "Test",
        "text": "Body",
        "html": "<p>Body</p>",
        "SPF": "pass",
        "dkim": "pass",
        "attachments": "2",
        "attachment_info": dumps(
            {
                "attachment1": {
                    "filename": "doc.pdf",
                    "name": "doc",
                    "type": "application/pdf",
                    "content-id": "cid1",
                },
            }
        ),
        "content-ids": dumps({"cid1": "attachment1"}),
        "spam_score": "3.5",
        "spam_report": "SPAM_RULE_1\nSPAM_RULE_2",
    }
    result = tested.from_dict(data)
    expected = ParsedEmail(
        headers=[ParsedHeader(name="Subject", value="Test")],
        charsets={"to": "UTF-8"},
        envelope=ParsedEnvelope(
            email_from="sender@example.com", email_to=["recipient@example.com"]
        ),
        email_from="sender@example.com",
        email_to="recipient@example.com",
        subject="Test",
        text="Body",
        html="<p>Body</p>",
        attachments=2,
        attachment_info={
            "attachment1": ParsedAttachment(
                filename="doc.pdf",
                name="doc",
                type="application/pdf",
                content_id="cid1",
            ),
        },
        content_ids={"cid1": "attachment1"},
        spf="pass",
        dkim="pass",
        spam_report=["SPAM_RULE_1", "SPAM_RULE_2"],
        spam_score=3.5,
    )
    assert result == expected


def test_to_dict() -> None:
    """Test converting ParsedEmail to dictionary."""
    tested = ParsedEmail(
        headers=[
            ParsedHeader(name="Content-Type", value="text/html"),
        ],
        charsets={"body": "UTF-8"},
        envelope=ParsedEnvelope(email_from="from@example.com", email_to=["to@example.com"]),
        email_from="from@example.com",
        email_to="to@example.com",
        subject="Subject Line",
        text="Plain text",
        html="<p>HTML</p>",
        attachments=1,
        attachment_info={
            "file1": ParsedAttachment(
                filename="image.png",
                name="image",
                type="image/png",
                content_id="img1",
            ),
        },
        content_ids={"img1": "file1"},
        spf="pass",
        dkim="none",
        spam_report=["RULE_A"],
        spam_score=1.23,
    )
    result = tested.to_dict()
    expected = {
        "headers": [{"name": "Content-Type", "value": "text/html"}],
        "charsets": {"body": "UTF-8"},
        "envelope": {"emailFrom": "from@example.com", "emailTo": ["to@example.com"]},
        "emailFrom": "from@example.com",
        "emailTo": "to@example.com",
        "subject": "Subject Line",
        "text": "Plain text",
        "html": "<p>HTML</p>",
        "attachments": 1,
        "attachmentInfo": {
            "file1": {
                "filename": "image.png",
                "name": "image",
                "type": "image/png",
                "contentId": "img1",
            },
        },
        "contentIds": {"img1": "file1"},
        "spf": "pass",
        "dkim": "none",
        "spamReport": ["RULE_A"],
        "spamScore": "1.23",
    }
    assert result == expected
