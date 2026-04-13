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
