from unittest.mock import patch

import pytest

from canvas_sdk.v1.data.invoice import Invoice


def test_invoice_pdf_url_with_pdf() -> None:
    """invoice_pdf_url returns a presigned URL when a PDF is set."""
    invoice = Invoice()
    invoice.invoice_pdf = "invoices/abc_20260101_120000.pdf"

    with patch(
        "canvas_sdk.v1.data.invoice.presigned_url",
        return_value="https://s3.example.com/presigned",
    ) as mock:
        assert invoice.invoice_pdf_url == "https://s3.example.com/presigned"
        mock.assert_called_once_with("invoices/abc_20260101_120000.pdf")


@pytest.mark.parametrize("value", [None, ""])
def test_invoice_pdf_url_returns_none_when_unset(value: str | None) -> None:
    """invoice_pdf_url returns None when no PDF is set."""
    invoice = Invoice()
    invoice.invoice_pdf = value

    assert invoice.invoice_pdf_url is None
