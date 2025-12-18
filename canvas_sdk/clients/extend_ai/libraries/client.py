from collections.abc import Iterator
from http import HTTPStatus
from typing import TypeVar
from urllib.parse import urlencode

from requests import Response
from requests import delete as requests_delete

from canvas_sdk.clients.extend_ai.constants.version_name import VersionName
from canvas_sdk.clients.extend_ai.structures.config.config_base import ConfigBase
from canvas_sdk.clients.extend_ai.structures.config.config_extraction import ConfigExtraction
from canvas_sdk.clients.extend_ai.structures.processor_meta import ProcessorMeta
from canvas_sdk.clients.extend_ai.structures.processor_run import ProcessorRun
from canvas_sdk.clients.extend_ai.structures.processor_version import ProcessorVersion
from canvas_sdk.clients.extend_ai.structures.request_failed import RequestFailed
from canvas_sdk.clients.extend_ai.structures.stored_file import StoredFile
from canvas_sdk.clients.extend_ai.structures.structure import Structure
from canvas_sdk.utils.http import Http

Data = TypeVar("Data", bound=Structure)


class Client:
    """Client for interacting with the Extend AI API.

    This client provides methods for managing files, processors, and processor runs
    through the Extend AI API. It handles authentication and API versioning.
    """

    @classmethod
    def _valid_content(cls, request: Response, key: str, returned: type[Data]) -> Data:
        """Validate and extract data from an API response.

        Args:
            request: The HTTP response from the API.
            key: The key in the response JSON containing the data.
            returned: The class to instantiate with the response data.

        Returns:
            An instance of the returned with data from the response.

        Raises:
            RequestFailed: If the request was not successful or returned an error.
        """
        if (
            request.status_code == HTTPStatus.OK
            and (response := request.json())
            and response["success"]
        ):
            return returned.from_dict(response[key])
        raise RequestFailed(request.status_code, request.content.decode())

    def __init__(self, key: str) -> None:
        """Initialize the Extend AI client.

        Args:
            key: The API key for authentication with Extend AI.
        """
        self.http = Http("https://api.extend.ai")
        self.headers = {
            "x-extend-api-version": "2025-04-21",
            "Authorization": f"Bearer {key}",
        }

    def _valid_content_list(self, url: str, key: str, returned: type[Data]) -> Iterator[Data]:
        """Fetch and yield paginated data from an API endpoint.

        Args:
            url: The API endpoint URL to fetch from.
            key: The key in the response JSON containing the list data.
            returned: The class to instantiate for each item in the list.

        Yields:
            Instances of the returned for each item in the paginated results.

        Raises:
            RequestFailed: If any request was not successful or returned an error.
        """
        base_url = url
        while True:
            request = self.http.get(url, headers=self.headers)
            if (
                request.status_code == HTTPStatus.OK
                and (response := request.json())
                and response["success"]
            ):
                for item in response[key]:
                    yield returned.from_dict(item)
                next_page_token = response.get("nextPageToken")
                if not next_page_token:
                    break
                url = f"{base_url}?{urlencode({'nextPageToken': next_page_token})}"
            else:
                raise RequestFailed(request.status_code, request.content.decode())

    def list_files(self) -> Iterator[StoredFile]:
        """List all files stored in Extend AI.

        Yields:
            StoredFile instances for each file in the account.

        Raises:
            RequestFailed: If the request was not successful.
        """
        yield from self._valid_content_list("/files", "files", StoredFile)

    def delete_file(self, file_id: str) -> bool:
        """Delete a file from Extend AI.

        Args:
            file_id: The unique identifier of the file to delete.

        Returns:
            True if the file was successfully deleted.

        Raises:
            RequestFailed: If the request was not successful.
        """
        url = f"https://api.extend.ai/files/{file_id}"
        request = requests_delete(url, headers=self.headers)
        if (
            request.status_code == HTTPStatus.OK
            and (response := request.json())
            and response["success"]
        ):
            return bool(response["success"])
        raise RequestFailed(status_code=request.status_code, message=request.content.decode())

    def list_processors(self) -> Iterator[ProcessorMeta]:
        """List all processors in the Extend AI account.

        Yields:
            ProcessorMeta instances for each processor.

        Raises:
            RequestFailed: If the request was not successful.
        """
        yield from self._valid_content_list("/processors", "processors", ProcessorMeta)

    def processor(self, processor_id: str, version: str) -> ProcessorVersion:
        """Get details for a specific processor version.

        Args:
            processor_id: The unique identifier of the processor.
            version: The version name or ID. Defaults to "draft" if empty.

        Returns:
            ProcessorVersion containing the processor configuration and details.

        Raises:
            RequestFailed: If the request was not successful.
        """
        if not version:
            version = VersionName.DRAFT.value
        request = self.http.get(
            f"/processors/{processor_id}/versions/{version}",
            headers=self.headers,
        )
        return self._valid_content(request, "version", ProcessorVersion)

    def create_processor(self, name: str, config: ConfigBase) -> ProcessorMeta:
        """Create a new processor in Extend AI.

        Args:
            name: The name for the new processor.
            config: The processor configuration object.

        Returns:
            ProcessorMeta containing metadata for the newly created processor.

        Raises:
            RequestFailed: If the request was not successful.
        """
        headers = self.headers | {"Content-Type": "application/json"}
        data = {
            "name": name,
            "type": config.processor_type().value,
            "config": config.to_dict(),
        }
        request = self.http.post("/processors", headers=headers, json=data)
        return self._valid_content(request, "processor", ProcessorMeta)

    def run_status(self, run_id: str) -> ProcessorRun:
        """Get the status of a processor run.

        Args:
            run_id: The unique identifier of the processor run.

        Returns:
            ProcessorRun containing the run status and results.

        Raises:
            RequestFailed: If the request was not successful.
        """
        request = self.http.get(f"/processor_runs/{run_id}", headers=self.headers)
        return self._valid_content(request, "processorRun", ProcessorRun)

    def run_processor(
        self,
        processor_id: str,
        file_name: str,
        file_url: str,
        config: ConfigExtraction | None,
    ) -> ProcessorRun:
        """Execute a processor on a file.

        Args:
            processor_id: The unique identifier of the processor to run.
            file_name: The name of the file to process.
            file_url: The URL where the file can be accessed.
            config: Optional extraction configuration to override processor defaults.

        Returns:
            ProcessorRun containing the initial run status and ID.

        Raises:
            RequestFailed: If the request was not successful.
        """
        headers = self.headers | {"Content-Type": "application/json"}
        data = {
            "processorId": processor_id,
            "file": {
                "fileName": file_name,
                "fileUrl": file_url,
            },
        }
        if config is not None:
            data = data | {"config": config.to_dict()}
        request = self.http.post("/processor_runs", headers=headers, json=data)
        return self._valid_content(request, "processorRun", ProcessorRun)


__exports__ = ()
