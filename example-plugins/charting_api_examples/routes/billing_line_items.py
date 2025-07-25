from http import HTTPStatus

from canvas_sdk.effects import Effect
from canvas_sdk.effects.billing_line_item import AddBillingLineItem
from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.handlers.simple_api import APIKeyAuthMixin, SimpleAPI, api
from canvas_sdk.v1.data.note import Note

from charting_api_examples.util import get_note_from_path_params, note_not_found_response


class BillingLineItemAPI(APIKeyAuthMixin, SimpleAPI):
    PREFIX = "/notes"

    """
    POST /plugin-io/api/charting_api_examples/notes/<note-id>/billing_line_items/
    Headers: "Authorization <your value for 'simpleapi-api-key'>"
    Body: {
        "cpt_code": "98006"
    }
    """
    @api.post("/<id>/billing_line_items/")
    def add_billing_line_item(self) -> list[Response | Effect]:
        required_attributes = {"cpt_code",}
        request_body = self.request.json()
        missing_attributes = required_attributes - request_body.keys()
        if len(missing_attributes) > 0:
            return [
                JSONResponse(
                    {"error": f"Missing required attribute(s): {', '.join(missing_attributes)}"},
                    # Normally you should use a constant, but this status
                    # code's constant changes in 3.13 from
                    # UNPROCESSABLE_ENTITY to UNPROCESSABLE_CONTENT. Using the
                    # number directly here avoids that future breakage.
                    status_code=422,
                )
            ]

        note = get_note_from_path_params(self.request.path_params)
        if not note:
            return note_not_found_response()

        # To see what else you can do with billing line items, visit our docs:
        # https://docs.canvasmedical.com/sdk/effect-billing-line-items/#adding-a-billing-line-item
        effect = AddBillingLineItem(
            note_id=str(note.id),
            cpt=request_body["cpt_code"],
        )

        return [
            effect.apply(),
            JSONResponse({"message": "Billing line item data accepted for creation"}, status_code=HTTPStatus.ACCEPTED)
        ]
