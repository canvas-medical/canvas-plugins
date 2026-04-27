from unittest.mock import patch

from canvas_sdk.v1.data.patient_consent import PatientConsentCoding


def test_patient_consent_coding_has_document_field() -> None:
    """PatientConsentCoding.document exposes the consent template file."""
    coding = PatientConsentCoding()
    coding.document = "consents/my-consent.pdf"

    assert coding.document == "consents/my-consent.pdf"


def test_patient_consent_coding_document_is_nullable() -> None:
    """PatientConsentCoding.document can be None when no document is uploaded."""
    coding = PatientConsentCoding()

    assert coding.document is None


def test_document_url_with_document() -> None:
    """document_url returns a presigned URL when document is set."""
    coding = PatientConsentCoding()
    coding.document = "consents/my-consent.pdf"

    with patch(
        "canvas_sdk.v1.data.patient_consent.presigned_url",
        return_value="https://s3.example.com/presigned",
    ) as mock:
        assert coding.document_url == "https://s3.example.com/presigned"
        mock.assert_called_once_with("consents/my-consent.pdf")


def test_document_url_returns_none_when_no_document() -> None:
    """document_url returns None when document is not set."""
    coding = PatientConsentCoding()
    coding.document = ""

    assert coding.document_url is None
