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

T = TypeVar("T", bound=Structure)


class Client:
    """Client for interacting with the Extend AI API.

    This client provides methods for managing files, processors, and processor runs
    through the Extend AI API. It handles authentication and API versioning.
    """

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

    @classmethod
    def valid_content(
        cls, request: Response, key: str, returned_class: type[T]
    ) -> T | RequestFailed:
        """Validate and extract content from an API response.

        Args:
            request: The HTTP response from the API.
            key: The key in the response JSON to extract the data from.
            returned_class: The class type to instantiate from the response data.

        Returns:
            An instance of the returned_class if successful, otherwise a RequestFailed object.
        """
        if (
            request.status_code == HTTPStatus.OK
            and (response := request.json())
            and response["success"]
        ):
            return returned_class.from_dict(response[key])
        return RequestFailed(status_code=request.status_code, message=request.content.decode())

    def valid_content_list(
        self, url: str, key: str, returned_class: type[T]
    ) -> list[T] | RequestFailed:
        """Retrieve and validate a paginated list of content from the API.

        Handles pagination by following nextPageToken values until all results are retrieved.

        Args:
            url: The API endpoint URL to request.
            key: The key in the response JSON containing the list data.
            returned_class: The class type to instantiate for each list item.

        Returns:
            A list of instances of returned_class if successful, otherwise a RequestFailed object.
        """
        result: list[T] = []
        base_url = url
        while True:
            request = self.http.get(url, headers=self.headers)
            if (
                request.status_code == HTTPStatus.OK
                and (response := request.json())
                and response["success"]
            ):
                result.extend([returned_class.from_dict(item) for item in response[key]])
                next_page_token = response.get("nextPageToken")
                if not next_page_token:
                    break
                url = f"{base_url}?{urlencode({'nextPageToken': next_page_token})}"
            else:
                return RequestFailed(
                    status_code=request.status_code, message=request.content.decode()
                )
        return result

    def list_files(self) -> list[StoredFile] | RequestFailed:
        """List all stored files in Extend AI.

        Returns:
            A list of StoredFile objects if successful, otherwise a RequestFailed object.
        """
        return self.valid_content_list("/files", "files", StoredFile)

    def delete_file(self, file_id: str) -> bool | RequestFailed:
        """Delete a stored file from Extend AI.

        Args:
            file_id: The unique identifier of the file to delete.

        Returns:
            True if the file was successfully deleted, otherwise a RequestFailed object.
        """
        url = f"https://api.extend.ai/files/{file_id}"
        request = requests_delete(url, headers=self.headers)
        if (
            request.status_code == HTTPStatus.OK
            and (response := request.json())
            and response["success"]
        ):
            return bool(response["success"])
        return RequestFailed(status_code=request.status_code, message=request.content.decode())

    def list_processors(self) -> list[ProcessorMeta] | RequestFailed:
        """List all available processors.

        Returns:
            A list of ProcessorMeta objects if successful, otherwise a RequestFailed object.
        """
        return self.valid_content_list("/processors", "processors", ProcessorMeta)

    def processor(self, processor_id: str, version: str) -> ProcessorVersion | RequestFailed:
        """Get a specific version of a processor.

        Args:
            processor_id: The unique identifier of the processor.
            version: The version name to retrieve. Defaults to DRAFT if empty.

        Returns:
            A ProcessorVersion object if successful, otherwise a RequestFailed object.
        """
        if not version:
            version = VersionName.DRAFT.value
        request = self.http.get(
            f"/processors/{processor_id}/versions/{version}", headers=self.headers
        )
        return self.valid_content(request, "version", ProcessorVersion)

    def create_processor(
        self,
        name: str,
        config: ConfigBase,
    ) -> ProcessorMeta | RequestFailed:
        """Create a new processor with the specified configuration.

        Args:
            name: The name for the new processor.
            config: The configuration object defining the processor's behavior.

        Returns:
            A ProcessorMeta object if successful, otherwise a RequestFailed object.
        """
        headers = self.headers | {"Content-Type": "application/json"}
        data = {
            "name": name,
            "type": config.processor_type().value,
            "config": config.to_dict(),
        }
        request = self.http.post("/processors", headers=headers, json=data)
        return self.valid_content(request, "processor", ProcessorMeta)

    def run_status(self, run_id: str) -> ProcessorRun | RequestFailed:
        """Get the status and results of a processor run.

        Args:
            run_id: The unique identifier of the processor run.

        Returns:
            A ProcessorRun object if successful, otherwise a RequestFailed object.
        """
        request = self.http.get(f"/processor_runs/{run_id}", headers=self.headers)
        return self.valid_content(request, "processorRun", ProcessorRun)

    def run_processor(
        self,
        processor_id: str,
        file_name: str,
        file_url: str,
        config: ConfigExtraction | None,
    ) -> ProcessorRun | RequestFailed:
        """Execute a processor on a file.

        Args:
            processor_id: The unique identifier of the processor to run.
            file_name: The name of the file to process.
            file_url: The URL where the file can be accessed.
            config: Optional extraction configuration to override the processor's default config.

        Returns:
            A ProcessorRun object if successful, otherwise a RequestFailed object.
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
        return self.valid_content(request, "processorRun", ProcessorRun)


__exports__ = ()
