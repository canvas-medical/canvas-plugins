import os
from typing import Any, Literal

import requests

from canvas_sdk.utils.http import Http, JsonOnlyResponse
from logger.logger import current_plugin_name


class PatientPortalLinkError(RuntimeError):
    """Raised when a patient portal link could not be minted.

    Attributes:
        status_code: The HTTP status code Canvas returned, or 0 if Canvas was never reached.
        message: The error message describing the failure.
    """

    def __init__(self, status_code: int, message: str):
        """Initialize a PatientPortalLinkError.

        Args:
            status_code: The HTTP status code Canvas returned, or 0 if never reached.
            message: The error message describing the failure.
        """
        super().__init__(message)
        self.status_code = status_code
        self.message = message


class PatientPortalHttp:
    """
    A client for minting patient portal links.

    The HTTP client is held privately rather than inherited, because its base URL is Canvas
    itself and a public request method here would be a way to reach other Canvas endpoints
    with the pre-shared key attached. `get_login_url` hands back a string, so plugin code
    holds the link and nothing else. That is a smaller target rather than a containment
    boundary: the sandbox is what confines plugin code.
    """

    def __init__(self) -> None:
        # CANVAS_PUBLIC_HOST is the instance's own URL and is required by its settings. The
        # runner does not share a listening port with the web process, so an address that
        # resolves only inside the web container reaches nothing.
        self._http_client = Http(base_url=os.getenv("CANVAS_PUBLIC_HOST", ""))

        self._http_client._session.headers.update(
            {"Authorization": os.getenv("PRE_SHARED_KEY", "")}
        )

    def get_login_url(
        self,
        patient_id: str,
        link_type: Literal["invite", "reset"] = "invite",
        next_path: str = "/",
        ttl: int | None = None,
    ) -> str:
        """Return a patient's portal link, without sending anything.

        The link is the same one Canvas's own invite sends, so the patient's experience does
        not depend on how it is delivered. Deliver it over any transport you like, and treat
        it as a credential: whoever opens it can set that patient's portal password.

        Args:
            patient_id: The patient's identifier, as exposed on `Patient.id`.
            link_type: Either "invite" or "reset". Both return the same kind of link — the
                portal decides whether to show account activation or a password reset from
                the recipient's `CanvasUser.is_portal_registered` when the link is opened.
                Choose your message copy from that same field.
            next_path: Where in the portal to land the patient. Canvas rejects a path that
                leaves the portal.
            ttl: Seconds the link stays valid. Defaults to the same expiry as a native
                invite, and Canvas caps how long it may be.

        Raises:
            PatientPortalLinkError: If the link could not be minted, including when Canvas
                could not be reached.
        """
        payload: dict[str, Any] = {
            "patient_id": patient_id,
            "link_type": link_type,
            "next_path": next_path,
        }

        if ttl is not None:
            payload["ttl"] = ttl

        # The plugin is named for the audit trail only; it is not a credential. This is empty
        # off the handler's own thread, since it comes from a context variable.
        plugin_name = current_plugin_name()
        headers = {"X-Canvas-Plugin-Name": plugin_name} if plugin_name else None

        try:
            response = JsonOnlyResponse(
                self._http_client.post("/patient-portal/login-url/", json=payload, headers=headers)
            )
        except requests.RequestException as error:
            # `requests` is not importable from a plugin, so its exceptions are uncatchable
            # there. Re-raise as the one type this module documents.
            raise PatientPortalLinkError(
                0, f"Could not reach Canvas to mint a portal link for patient {patient_id}."
            ) from error

        if response.status_code != 200:
            raise PatientPortalLinkError(
                response.status_code,
                f"Could not mint a portal link for patient {patient_id}.",
            )

        response_json = response.json()
        login_url = response_json.get("login_url") if isinstance(response_json, dict) else None

        if not login_url or not isinstance(login_url, str):
            raise PatientPortalLinkError(
                response.status_code,
                f"The portal link response for patient {patient_id} carried no link.",
            )

        return login_url


patient_portal_http = PatientPortalHttp()

__all__ = __exports__ = (
    "PatientPortalLinkError",
    "patient_portal_http",
)
