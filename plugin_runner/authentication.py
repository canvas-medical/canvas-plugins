import os
from typing import cast

import arrow
from jwt import encode

from logger import log

ONE_DAY_IN_MINUTES = 60 * 24

INSECURE_DEFAULT_SIGNING_KEY = "INSECURE_KEY"


def token_for_plugin(
    plugin_name: str,
    audience: str,
    issuer: str = "plugin-runner",
    jwt_signing_key: str = cast(
        str, os.getenv("PLUGIN_RUNNER_SIGNING_KEY", INSECURE_DEFAULT_SIGNING_KEY)
    ),
    expiration_minutes: int = ONE_DAY_IN_MINUTES,
    extra_kwargs: dict | None = None,
) -> str:
    """
    Generate a JWT for the given plugin and audience.
    """
    if not extra_kwargs:
        extra_kwargs = {}

    if jwt_signing_key == INSECURE_DEFAULT_SIGNING_KEY:
        log.warning(
            "Using an insecure JWT signing key for GraphQL access. Set the PLUGIN_RUNNER_SIGNING_KEY environment variable to avoid this message."
        )

    token = encode(
        {
            "plugin_name": plugin_name,
            "customer_identifier": os.getenv("CUSTOMER_IDENTIFIER"),
            "exp": arrow.utcnow().shift(minutes=expiration_minutes).datetime,
            "aud": audience,
            "iss": issuer,
            **extra_kwargs,
        },
        jwt_signing_key,
        algorithm="HS256",
    )

    return token
