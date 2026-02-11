from http import HTTPStatus

from aws_manip.constants.secrets import Secrets
from canvas_sdk.clients.aws.libraries import S3
from canvas_sdk.clients.aws.structures import Credentials as S3Credentials
from canvas_sdk.effects import Effect
from canvas_sdk.effects.simple_api import JSONResponse, PlainTextResponse, Response
from canvas_sdk.handlers.simple_api import Credentials, SimpleAPI, api


class AwsManip(SimpleAPI):
    """Simple API handler for AWS S3 object management operations."""

    PREFIX = None
    USER_TYPE_STAFF = "Staff"

    def authenticate(self, credentials: Credentials) -> bool:
        """Authenticate API requests.

        Args:
            credentials: The credentials provided with the request.

        Returns:
            True to allow all requests (authentication bypassed).
        """
        return True

    def _s3_client(self) -> S3:
        """Create and configure an S3 client with credentials from secrets.

        Returns:
            Configured S3 client instance.
        """
        return S3(
            S3Credentials(
                key=self.secrets[Secrets.s3_key],
                secret=self.secrets[Secrets.s3_secret],
                region=self.secrets[Secrets.s3_region],
                bucket=self.secrets[Secrets.s3_bucket],
            )
        )

    @api.get("/list_items")
    def list_items(self) -> list[Response | Effect]:
        """List all objects in the S3 bucket.

        Returns:
            JSON response containing list of object keys, or empty list if not ready.
        """
        client = self._s3_client()
        if client.is_ready():
            content = [p.key for p in client.list_s3_objects("")]
            status_code = HTTPStatus(HTTPStatus.OK)
            return [JSONResponse(content, status_code=status_code)]
        return []

    @api.get("/get_item/<item_key>")
    def get_item(self) -> list[Response | Effect]:
        """Retrieve an object's content from S3 by key.

        Returns:
            Response containing the object's binary content, or empty list if not ready.
        """
        item_key = self.request.path_params["item_key"]
        client = self._s3_client()
        if client.is_ready() and item_key:
            content = client.access_s3_object(item_key).content
            status_code = HTTPStatus(HTTPStatus.OK)
            return [Response(content, status_code=status_code)]
        return []

    @api.get("/presigned_url/<item_key>")
    def presigned_url(self) -> list[Response | Effect]:
        """Generate a presigned URL for temporary access to an S3 object.

        Returns:
            Plain text response containing the presigned URL (valid for 1 hour),
            or empty list if not ready.
        """
        item_key = self.request.path_params["item_key"]
        client = self._s3_client()
        if client.is_ready() and item_key:
            content = client.generate_presigned_url(item_key, 3600)
            status_code = HTTPStatus(HTTPStatus.OK)
            return [PlainTextResponse(content, status_code=status_code)]
        return []

    @api.post("/upload_item/<item_key>")
    def upload_item(self) -> list[Response | Effect]:
        """Upload content to S3 with the specified key.

        Handles both text/plain and binary content types.

        Returns:
            Response from S3 upload operation, or empty list if not ready.
        """
        item_key = self.request.path_params["item_key"]
        client = self._s3_client()
        content = self.request.body
        content_type = self.request.content_type
        if client.is_ready() and item_key:
            if content_type == "text/plain":
                response = client.upload_text_to_s3(item_key, content.decode("utf-8"))
            else:
                response = client.upload_binary_to_s3(item_key, content, content_type)
            return [Response(response.content, status_code=response.status_code)]
        return []

    @api.delete("/delete_item/<item_key>")
    def delete_item(self) -> list[Response | Effect]:
        """Delete an object from S3 by key.

        Returns:
            Response from S3 delete operation, or empty list if not ready.
        """
        item_key = self.request.path_params["item_key"]
        client = self._s3_client()
        if client.is_ready() and item_key:
            content = client.delete_object(item_key).content
            status_code = HTTPStatus(HTTPStatus.OK)
            return [Response(content, status_code=status_code)]
        return []
