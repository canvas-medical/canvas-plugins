def is_plugin_upload_key(key: str) -> bool:
    """Return whether the key looks like one returned by a ``file_uploads="stored"`` route.

    Canvas checks that the key belongs to the calling plugin when the effect is applied.
    """
    return key.startswith("plugin-uploads/") or "/plugin-uploads/" in key


def upload_key_error(field: str) -> str:
    """The error message for a field holding something other than a plugin upload key."""
    return (
        f"Field '{field}' must be the key of a file uploaded through a SimpleAPI route "
        "declared with file_uploads='stored'."
    )


__exports__ = ()
