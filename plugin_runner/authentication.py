import os
from typing import cast

import arrow
from jwt import encode

# import base64


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
        algorithm="HS512",
    )

    return token


# def jwt_header_for_plugin(plugin_name: str, audience: str = "home", expiration_minutes: int = 5):
#     jwt = token_for_plugin(plugin_name, audience=audience, expiration_minutes=expiration_minutes)
#
#     return base64.b64encode(f"jwt:{jwt}".encode()).decode()
