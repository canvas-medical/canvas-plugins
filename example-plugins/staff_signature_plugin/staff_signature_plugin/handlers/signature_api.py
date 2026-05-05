from http import HTTPStatus

from canvas_sdk.effects.simple_api import HTMLResponse, JSONResponse
from canvas_sdk.handlers.simple_api import SimpleAPIRoute, StaffSessionAuthMixin
from canvas_sdk.templates import render_to_string
from canvas_sdk.v1.data import Staff


class StaffSignatureAPI(StaffSessionAuthMixin, SimpleAPIRoute):
    """Serves the modal HTML that renders the logged-in staff's signature image."""

    PATH = "/signature"

    def get(self) -> list[HTMLResponse | JSONResponse]:
        """Render the signature modal for the logged-in staff member."""
        staff_id = self.request.headers["canvas-logged-in-user-id"]

        try:
            staff = Staff.objects.get(id=staff_id)
        except Staff.DoesNotExist:
            return [
                JSONResponse(
                    {"error": f"Staff with id {staff_id} not found."},
                    status_code=HTTPStatus.NOT_FOUND,
                )
            ]

        context = {
            "staff_name": staff.full_name,
            "signature_url": staff.signature_url,
        }
        return [
            HTMLResponse(
                render_to_string("templates/signature_modal.html", context),
                status_code=HTTPStatus.OK,
            )
        ]
