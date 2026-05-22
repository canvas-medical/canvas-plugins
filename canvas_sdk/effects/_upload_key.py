"""Shared sanity-check for S3 upload keys carried on plugin write effects.

Plugin-uploaded files arrive via SimpleAPI routes declared with
``upload_files=True``. The platform returns each upload's S3 key in the form
``<customer>/plugin-uploads/<your-plugin>/<timestamp>-<uuid>-<filename>``.
Effects that accept such a key (e.g. ``Coverage.card_image_front_upload_key``,
``Message.attachment_upload_keys``) use this helper as a coarse client-side
guard. The platform-side interpreter performs the **strict** prefix check
against the customer + plugin name and is the actual security boundary.
"""

from __future__ import annotations

_PLUGIN_UPLOAD_SEGMENT = "/plugin-uploads/"


def check_upload_key(key: str | None, *, field_label: str = "Upload key") -> str | None:
    """Return an error message if ``key`` is malformed, else None.

    A valid key contains ``/plugin-uploads/`` somewhere after the customer
    prefix. ``None`` is accepted (no key supplied).
    """
    if key is None:
        return None
    if _PLUGIN_UPLOAD_SEGMENT not in ("/" + key):
        return (
            f"{field_label} must contain '{_PLUGIN_UPLOAD_SEGMENT}'. Got: {key!r}"
        )
    return None
