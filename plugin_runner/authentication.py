import os
from typing import cast

import arrow
from jwt import encode

ONE_DAY_IN_MINUTES = 60 * 24


def token_for_plugin(
    plugin_name: str,
    audience: str,
    issuer: str = "plugin-runner",
    jwt_signing_key: str = cast(str, os.getenv('PLUGIN_RUNNER_SIGNING_KEY')),
    expiration_minutes: int = ONE_DAY_IN_MINUTES,
    extra_kwargs: dict | None = None,
) -> str:
    """
    Generate a JWT for the given plugin and audience.
    """
    if not extra_kwargs:
        extra_kwargs = {}

    token = encode(
        {
            "plugin_name": plugin_name,
            "customer_identifier": os.getenv('CUSTOMER_IDENTIFIER'),
            "exp": arrow.utcnow().shift(minutes=expiration_minutes).datetime,
            "aud": audience,
            "iss": issuer,
            **extra_kwargs,
        },
        jwt_signing_key,
        algorithm="HS256",
    )

    return token
