import dataclasses
import os
import urllib.parse

import requests

from canvas_sdk.utils.http import ServiceClient
from settings import CUSTOMER_IDENTIFIER


class PdfUrlResponse:
    """A response wrapper that exposes the presigned S3 URL for a generated PDF."""

    url: str

    def __init__(self, response: requests.Response):
        self.url = response.headers.get("Location", "")


@dataclasses.dataclass
class PdfAuthRequest:
    """Credentials forwarded as X-PDF-Auth-User / X-PDF-Auth-Password headers."""

    username: str
    password: str


class PdfGenerator(ServiceClient):
    """A client for the web-to-pdf service."""

    __exports__ = ("from_url", "from_html")

    def __init__(self) -> None:
        super().__init__(
            base_url=os.getenv("WEB_TO_PDF_ENDPOINT", "https://web-to-pdf.canvasmedical.com")
        )

    def _parse_redirect(self, response: requests.Response) -> PdfUrlResponse | None:
        if response.status_code != 302 or not response.headers.get("Location"):
            return None
        return PdfUrlResponse(response)

    def from_url(
        self,
        print_url: str,
        auth: PdfAuthRequest | None = None,
    ) -> PdfUrlResponse | None:
        """Generate a PDF from a URL that returns HTML."""
        host = os.getenv("CANVAS_PUBLIC_HOST", "")
        url = f"{host.rstrip('/')}/{print_url.lstrip('/')}"

        params = urllib.parse.urlencode(
            {
                "customerId": CUSTOMER_IDENTIFIER,
                "url": url,
            }
        )
        headers: dict[str, str] = {}
        if auth:
            headers["X-PDF-Auth-User"] = auth.username
            headers["X-PDF-Auth-Password"] = auth.password

        response = self._send(
            f"/generate/?{params}",
            lambda path: self._http_client._session.get(
                self._http_client.join_url(path),
                headers=headers,
                timeout=self._MAX_REQUEST_TIMEOUT_SECONDS,
                allow_redirects=False,
            ),
        )

        return self._parse_redirect(response)

    def from_html(self, content: str) -> PdfUrlResponse | None:
        """Generate a PDF from raw HTML content."""
        params = urllib.parse.urlencode(
            {
                "customerId": CUSTOMER_IDENTIFIER,
            }
        )
        response = self._send(
            f"/generate/?{params}",
            lambda path: self._http_client._session.post(
                self._http_client.join_url(path),
                data=content,
                headers={"Content-Type": "text/html"},
                timeout=self._MAX_REQUEST_TIMEOUT_SECONDS,
                allow_redirects=False,
            ),
        )

        return self._parse_redirect(response)


pdf_generator = PdfGenerator()

__all__ = __exports__ = (
    "PdfAuthRequest",
    "pdf_generator",
)
