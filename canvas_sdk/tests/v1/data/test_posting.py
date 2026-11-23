from decimal import Decimal

from canvas_sdk.v1.data.posting import PatientPosting


def test_patient_posting_discounted_amount_without_patient_payment() -> None:
    """A posting with no bulk patient payment has no discount."""
    assert PatientPosting(patient_payment=None).discounted_amount == Decimal(0)
