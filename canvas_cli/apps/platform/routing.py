"""Per-instance routing: does an instance command go through Canvas Platform?

This lives apart from ``commands`` because the instance commands (``list``, ``logs``,
``namespace *``) import it, and ``commands`` itself imports ``plugin.plugin``.
``commands`` re-exports ``managed_instance``.
"""

from __future__ import annotations

import click

from canvas_cli.apps.auth.utils import instance_slug
from canvas_cli.apps.platform import auth
from canvas_cli.apps.platform.client import PlatformClient
from canvas_cli.utils.platform_notice import print_credentials_ini_deprecation


def platform_sign_out() -> str:
    """Return how to stop using Canvas Platform, for the credential in force.

    Returns:
        str: ``unset CANVAS_PLATFORM_TOKEN`` under a service account token, which ``canvas
            logout`` leaves in force, and "sign out with `canvas logout`" otherwise.
    """
    if auth.service_token() is not None:
        return f"unset {auth.SERVICE_TOKEN_ENV}"
    return "sign out with `canvas logout`"


def refuse_unmanaged(cause: str, target: str) -> click.ClickException:
    """Return the refusal for a target Canvas Platform does not manage, while signed in.

    Args:
        cause (str): The sentence saying why Platform cannot handle the target.
        target (str): The instance or plugin, named in the way to use credentials.ini.

    Returns:
        click.ClickException: The refusal, naming the way to sign out.
    """
    return click.ClickException(
        f"{cause} While you are signed in to Canvas Platform, instance commands go through "
        f"it. To use credentials.ini for {target}, {platform_sign_out()}."
    )


def managed_instance(host: str, command: str) -> tuple[PlatformClient, str] | None:
    """Platform's client and the instance slug when the command goes through Platform.

    Signed in to Canvas Platform, a Canvas instance goes through Platform when it is in the
    person's list with ``managed`` set, and is refused otherwise. Signed out, or for
    localhost and other hosts that are not Canvas instances, the answer is None and the
    caller uses credentials.ini. The deprecation notice for ``command`` is printed for a
    Canvas instance only, since `canvas login` cannot serve the other hosts. A failed
    Platform lookup raises ``PlatformError`` and is never read as "unmanaged".

    Args:
        host (str): The Canvas instance URL.
        command (str): The command as typed after ``canvas``, for the deprecation notice.

    Returns:
        tuple[PlatformClient, str] | None: The client and slug, or None for credentials.ini.

    Raises:
        click.ClickException: Signed in, and Platform does not manage the instance.
    """
    slug: str | None = instance_slug(host)
    if slug is None:
        return None
    platform: str = auth.resolve_platform_url()
    if auth.stored_tokens(platform) is None:
        print_credentials_ini_deprecation(command)
        return None
    client = PlatformClient(platform)
    row = next((r for r in client.instances() if r.get("slug") == slug), None)
    if row is None:
        raise refuse_unmanaged(f"{slug} is not one of your instances on Canvas Platform.", slug)
    if not row.get("managed"):
        raise refuse_unmanaged(f"Canvas Platform does not manage {slug}.", slug)
    return client, slug
