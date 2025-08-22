from http import HTTPStatus
from uuid import uuid4

from charting_api_examples.util import get_note_from_path_params, note_not_found_response

from canvas_sdk.commands import (
    DiagnoseCommand,
    PhysicalExamCommand,
    PlanCommand,
    ReasonForVisitCommand,
)
from canvas_sdk.effects import Effect
from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.handlers.simple_api import APIKeyAuthMixin, SimpleAPI, api


class CommandAPI(APIKeyAuthMixin, SimpleAPI):
    PREFIX = "/notes"

    """
    This shows how you can create an endpoint to insert a particular type of
    command. In this example, it's a diagnose command. It can be committed or
    left uncommitted.

    POST /plugin-io/api/charting_api_examples/notes/<note-id>/diagnose/
    Headers: "Authorization <your value for 'simpleapi-api-key'>"
    Body: {
        "icd10_code": "E11.9",
        "committed": false
    }
    """

    @api.post("/<id>/diagnose/")
    def add_diagnose_command(self) -> list[Response | Effect]:
        required_attributes = {
            "icd10_code",
        }
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

        diagnose_command = DiagnoseCommand(
            note_uuid=str(note.id),
            icd10_code=request_body["icd10_code"].upper(),
        )

        if request_body.get("committed"):
            # To chain command effects, you must know what the command's id
            # is. To accomplish that, we set the id ourselves rather than
            # allow the database to assign one.
            diagnose_command.command_uuid = str(uuid4())
            command_effects = [diagnose_command.originate(), diagnose_command.commit()]
        else:
            command_effects = [diagnose_command.originate()]

        return [
            *command_effects,
            JSONResponse(
                {"message": "Command data accepted for creation"}, status_code=HTTPStatus.ACCEPTED
            ),
        ]

    """
    This shows how you can originate many commands from the same request.

    POST /plugin-io/api/charting_api_examples/notes/<note-id>/prechart/
    Headers: "Authorization <your value for 'simpleapi-api-key'>"
    Body: {
    }
    """

    @api.post("/<id>/prechart/")
    def add_precharting_commands(self) -> list[Response | Effect]:
        request_body = self.request.json()

        note = get_note_from_path_params(self.request.path_params)
        if not note:
            return note_not_found_response()

        rfv = ReasonForVisitCommand(note_uuid=str(note.id))
        exam = PhysicalExamCommand(note_uuid=str(note.id))
        diagnose = DiagnoseCommand(note_uuid=str(note.id))
        plan = PlanCommand(note_uuid=str(note.id))
        return [
            rfv.originate(),
            exam.originate(),
            diagnose.originate(),
            plan.originate(),
            JSONResponse(
                {"message": "Command data accepted for creation"}, status_code=HTTPStatus.ACCEPTED
            ),
        ]
