from typing import Any

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.commands.base import _BaseCommand as BaseCommand
from canvas_sdk.effects._field_errors import upload_key_errors


class VisualExamFindingCommand(BaseCommand):
    """
    A class for managing a Visual Exam Finding command within a specific note.

    The image (PNG or JPEG) is attached by passing the ``key`` of a ``StoredFilePart``
    received on a SimpleAPI route declared with ``file_uploads="stored"``. Canvas copies the
    file into the finding, then deletes the upload, so a key can be attached once. A
    recommendation can't carry an upload key, because the upload is gone after its first use.
    """

    class Meta:
        key = "visualExamFinding"

    title: str | None = Field(default=None, max_length=255)
    narrative: str | None = None
    image_upload_key: str | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)
        errors.extend(upload_key_errors(self, "image_upload_key"))
        if method == "recommend" and self.is_dirty("image_upload_key"):
            errors.append(
                self._create_error_detail(
                    "value",
                    "A recommended Visual Exam Finding can't carry an image_upload_key.",
                    self.image_upload_key,
                )
            )
        return errors

    def recommendation_context(self) -> dict:
        """Return the context of a recommendation, which can't carry an upload key."""
        self._validate_before_effect("recommend")
        return super().recommendation_context()


__exports__ = ("VisualExamFindingCommand",)
