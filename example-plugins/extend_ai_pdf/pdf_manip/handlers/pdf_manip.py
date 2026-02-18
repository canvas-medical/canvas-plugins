from datetime import datetime
from http import HTTPStatus

from canvas_sdk.clients.extend_ai.constants import RunStatus, VersionName
from canvas_sdk.clients.extend_ai.libraries import Client
from canvas_sdk.clients.extend_ai.structures import RequestFailed
from canvas_sdk.effects import Effect
from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.handlers.simple_api import SimpleAPI, StaffSessionAuthMixin, api
from pdf_manip.constants.secrets import Secrets


class PdfManip(StaffSessionAuthMixin, SimpleAPI):
    """API handler for Extend AI PDF processing operations."""

    PREFIX = None
    USER_TYPE_STAFF = "Staff"

    def _extend_client(self) -> Client:
        """Create and return a configured Extend AI client."""
        return Client(self.secrets[Secrets.extend_ai_key])

    @api.get("/processors")
    def list_processors(self) -> list[Response | Effect]:
        """Retrieve all available Extend AI processors."""
        try:
            content: list | dict = [p.to_dict() for p in self._extend_client().list_processors()]
            status_code = HTTPStatus(HTTPStatus.OK)
        except RequestFailed as e:
            content = {"information": e.message}
            status_code = HTTPStatus(e.status_code)
        return [JSONResponse(content, status_code=status_code)]

    @api.get("/processors/<processor_id>")
    def get_processor(self) -> list[Response | Effect]:
        """Retrieve the configuration for a specific processor by ID."""
        try:
            processor_id = self.request.path_params["processor_id"]
            response = self._extend_client().processor(processor_id, VersionName.DRAFT.value)
            content = response.config.to_dict()
            status_code = HTTPStatus(HTTPStatus.OK)
        except RequestFailed as e:
            content = {"information": e.message}
            status_code = HTTPStatus(e.status_code)
        return [JSONResponse(content, status_code=status_code)]

    @api.get("/result/<run_id>")
    def run_result(self) -> list[Response | Effect]:
        """Retrieve the processing result for a completed run."""
        try:
            run_id = self.request.path_params["run_id"]
            response = self._extend_client().run_status(run_id)
            if response.status == RunStatus.PROCESSED:
                content = {"result": response.output.to_dict()}
                status_code = HTTPStatus(HTTPStatus.OK)
            else:
                content = {"result": response.status}
                status_code = HTTPStatus(HTTPStatus.UNPROCESSABLE_ENTITY)
        except RequestFailed as e:
            content = {"information": e.message}
            status_code = HTTPStatus(e.status_code)
        return [JSONResponse(content, status_code=status_code)]

    @api.get("/status/<run_id>")
    def run_status(self) -> list[Response | Effect]:
        """Check the status of a processor run and clean up files if completed."""
        try:
            run_id = self.request.path_params["run_id"]
            extend_ai = self._extend_client()
            response = extend_ai.run_status(run_id)
            if response.status == RunStatus.PROCESSED:
                # if correctly processed, remove the files
                for file in response.files:
                    extend_ai.delete_file(file.id)
            content = {"runId": response.id, "status": response.status.value}
            status_code = HTTPStatus(HTTPStatus.OK)
        except RequestFailed as e:
            content = {"information": e.message}
            status_code = HTTPStatus(e.status_code)
        return [JSONResponse(content, status_code=status_code)]

    @api.get("/stored_files")
    def extend_stored_files(self) -> list[Response | Effect]:
        """List all files stored in Extend AI."""
        try:
            content: list | dict = [f.to_dict() for f in self._extend_client().list_files()]
            status_code = HTTPStatus(HTTPStatus.OK)
        except RequestFailed as e:
            content = {"information": e.message}
            status_code = HTTPStatus(e.status_code)
        return [JSONResponse(content, status_code=status_code)]

    @api.post("/delete_files")
    def extend_delete_files(self) -> list[Response | Effect]:
        """Delete specified files from Extend AI storage."""
        try:
            content: list | dict = [
                {
                    "id": file_id,
                    "deleted": self._extend_client().delete_file(file_id),
                }
                for file_id in self.request.json().get("fileIds") or []
            ]
            status_code = HTTPStatus(HTTPStatus.OK)
        except RequestFailed as e:
            content = {"information": e.message}
            status_code = HTTPStatus(e.status_code)
        return [JSONResponse(content, status_code=status_code)]

    @api.post("/execute")
    def run_start(self) -> list[Response | Effect]:
        """Start a processor run on a document from a public S3 URL."""
        try:
            received = self.request.json()
            aws_s3_url = received.get("fileAwsS3Url")  # the URL has to be publicly available
            processor_id = received.get("processorId")

            response = self._extend_client().run_processor(
                processor_id=processor_id,
                file_name=f"processed-{datetime.now().isoformat(timespec='seconds')}",
                file_url=aws_s3_url,
                config=None,
            )
            content = {"runId": response.id, "status": response.status.value}
            status_code = HTTPStatus(HTTPStatus.OK)
        except RequestFailed as e:
            content = {"information": e.message}
            status_code = HTTPStatus(e.status_code)
        return [JSONResponse(content, status_code=status_code)]
