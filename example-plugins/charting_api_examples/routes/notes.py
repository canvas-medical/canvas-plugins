import arrow

from canvas_sdk.effects import Effect
from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.handlers.simple_api import APIKeyAuthMixin, SimpleAPI, api
from canvas_sdk.v1.data.note import Note

class NoteAPI(APIKeyAuthMixin, SimpleAPI):
    PREFIX = "/notes"

    """
    GET /plugin-io/api/charting_api_examples/notes
    Headers: "Authorization <your value for 'simpleapi-api-key'>"
    """
    @api.get("/")
    def index(self) -> list[Response | Effect]:
        notes = Note.objects.order_by('dbid')
        query_params = self.request.query_params
        if 'patient_id' in query_params:
            notes = notes.filter(patient__id=query_params['patient_id'])
        if 'note_type' in query_params:
            # You can search by just the code value or you can search by the
            # system and code in the format system|code (e.g
            # http://snomed.info/sct|308335008).
            if '|' in query_params['note_type']:
                system, code = query_params['note_type'].split('|')
                notes = notes.filter(note_type__system=system, note_type__code=code)
            else:
                notes = notes.filter(note_type__code=query_params['note_type'])
        if 'datetime_of_service' in query_params:
            notes = notes.filter(datetime_of_service=query_params['datetime_of_service'])
        if 'datetime_of_service__gt' in query_params:
            notes = notes.filter(datetime_of_service__gt=query_params['datetime_of_service__gt'])
        if 'datetime_of_service__gte' in query_params:
            notes = notes.filter(datetime_of_service__gte=query_params['datetime_of_service__gte'])
        if 'datetime_of_service__lt' in query_params:
            notes = notes.filter(datetime_of_service__lt=query_params['datetime_of_service__lt'])
        if 'datetime_of_service__lte' in query_params:
            notes = notes.filter(datetime_of_service__lte=query_params['datetime_of_service__lte'])
        return [
            JSONResponse({
                "notes": [{
                    "id": str(note.id),
                    "patient_id": str(note.patient.id),
                    "provider_id": str(note.provider.id),
                    "datetime_of_service": str(note.datetime_of_service),
                } for note in notes]
            })
        ]

    """
    POST /plugin-io/api/charting_api_examples/notes
    Headers: "Authorization <your value for 'simpleapi-api-key'>"
    Body: {
    }
    """
    @api.post("/")
    def create(self) -> list[Response | Effect]:
        return [
            JSONResponse({"message": "Note create!"})
        ]

    """
    GET /plugin-io/api/charting_api_examples/notes/<note-id>
    Headers: "Authorization <your value for 'simpleapi-api-key'>"
    """
    @api.get("/<id>")
    def read(self) -> list[Response | Effect]:
        return [
            JSONResponse({"message": "Note read!"})
        ]

    """
    POST /plugin-io/api/charting_api_examples/notes/<note-id>/billing_line_items
    Headers: "Authorization <your value for 'simpleapi-api-key'>"
    Body: {
    }
    """
    @api.post("/<id>/billing_line_items")
    def add_billing_line_item(self) -> list[Response | Effect]:
        return [
            JSONResponse({"message": "Billing line item create!"})
        ]
