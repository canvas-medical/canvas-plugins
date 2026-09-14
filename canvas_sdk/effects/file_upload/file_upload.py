import json
from typing import Any

from pydantic_core import InitErrorDetails

from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.effects import Effect


class FileUpload(TrackableFieldsModel):
    """
    Effect to upload a file (image / document) and receive back a URL the
    plugin can stash in subsequent effects (Organization logo, Staff signature,
    branding background, etc.).

    `content_base64` is the base64-encoded bytes; `filename` and `content_type`
    are required for the home-app interpreter to dispatch to the right storage
    backend.
    """

    class Meta:
        effect_type = "FILE"

    filename: str | None = None
    content_type: str | None = None
    content_base64: str | None = None
    folder: str | None = None
    max_bytes: int | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)
        if method == "upload":
            for required in ("filename", "content_type", "content_base64"):
                if not getattr(self, required):
                    errors.append(
                        self._create_error_detail(
                            "missing",
                            f"Field '{required}' is required to upload a file.",
                            getattr(self, required),
                        )
                    )
        return errors

    def upload(self) -> Effect:
        """Upload a file and receive a URL in the response."""
        self._validate_before_effect("upload")
        return Effect(
            type=f"UPLOAD_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )


__exports__ = ("FileUpload",)
