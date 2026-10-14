from typing import Any

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.commands.base import _BaseCommand as BaseCommand
from canvas_sdk.effects._upload_key import is_plugin_upload_key, upload_key_error


class VisualExamFindingCommand(BaseCommand):
    """
    A class for managing a Visual Exam Finding command within a specific note.

    The image (PNG or JPEG) is attached by passing the ``key`` of a ``StoredFilePart``
    received on a SimpleAPI route declared with ``file_uploads="stored"``. Canvas copies the
    file into the finding, then deletes the upload, so a key can be attached once.
    """

    class Meta:
        key = "visualExamFinding"

    title: str | None = Field(default=None, max_length=255)
    narrative: str | None = None
    image_upload_key: str | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)
        if self.image_upload_key is not None and not is_plugin_upload_key(self.image_upload_key):
            errors.append(
                self._create_error_detail(
                    "value", upload_key_error("image_upload_key"), self.image_upload_key
                )
            )
        return errors


__exports__ = ("VisualExamFindingCommand",)
