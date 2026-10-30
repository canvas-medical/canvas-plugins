"""Per-instance routing: does an instance command go through Canvas Platform?

This lives apart from ``commands`` because the instance commands (``list``, ``logs``,
``namespace *``) import it, and ``commands`` itself imports ``plugin.plugin``.
``commands`` re-exports ``managed_instance``.
"""

from __future__ import annotations

from canvas_cli.apps.auth.utils import instance_slug
from canvas_cli.apps.platform import auth
from canvas_cli.apps.platform.client import PlatformClient


def managed_instance(host: str) -> tuple[PlatformClient, str] | None:
    """Platform's client and the instance slug when Platform manages ``host``, else None.

    Platform manages the instance when the person is signed in to Canvas Platform and the
    instance is in their list with ``managed`` set. Signed out, localhost, or an instance
    Platform does not manage answers None, and the caller uses credentials.ini. A failed
    Platform lookup raises ``PlatformError`` and is never read as "unmanaged".

    Args:
        host (str): The Canvas instance URL.

    Returns:
        tuple[PlatformClient, str] | None: The client and slug, or None.
    """
    slug: str | None = instance_slug(host)
    if slug is None:
        return None
    platform: str = auth.resolve_platform_url()
    if auth.stored_tokens(platform) is None:
        return None
    client = PlatformClient(platform)
    row = next((r for r in client.instances() if r.get("slug") == slug), None)
    if row is None or not row.get("managed"):
        return None
    return client, slug
