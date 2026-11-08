import os
import subprocess
import sys
from unittest.mock import patch

import jwt
import pytest
from django.core.exceptions import ImproperlyConfigured

import settings
from plugin_runner.authentication import token_for_plugin
from plugin_runner.plugin_runner import main

SIGNING_KEY = "insecure-signing-key-for-tests-only-abcd"


def test_token_for_plugin_is_signed_with_the_configured_key() -> None:
    """Test that the token carries the plugin claims and verifies against the signing key."""
    token = token_for_plugin(
        plugin_name="example_plugin",
        audience="home",
        jwt_signing_key=SIGNING_KEY,
    )

    claims = jwt.decode(token, SIGNING_KEY, algorithms=["HS256"], audience="home")

    assert claims["plugin_name"] == "example_plugin"
    assert claims["iss"] == "plugin-runner"


def test_main_refuses_to_serve_without_a_signing_key() -> None:
    """Test that the runner fails at startup rather than on every event."""
    with (
        patch.object(settings, "PLUGIN_RUNNER_SIGNING_KEY", ""),
        pytest.raises(ImproperlyConfigured) as raised,
    ):
        main()

    assert str(raised.value) == (
        "PLUGIN_RUNNER_SIGNING_KEY is not set. Deployed runners need it to sign each "
        "plugin's GraphQL token; with ENV other than production a development key is used."
    )


@pytest.mark.parametrize(
    "env, expected",
    [("production", ""), ("development", "insecure-signing-key-not-for-production")],
)
def test_only_a_non_production_runner_falls_back_to_the_public_signing_key(
    env: str, expected: str
) -> None:
    """A production runner with no key gets none, so `main` refuses to serve."""
    environment = {
        key: value for key, value in os.environ.items() if key != "PLUGIN_RUNNER_SIGNING_KEY"
    }
    environment["ENV"] = env

    loaded = subprocess.run(
        [sys.executable, "-c", "import settings; print(settings.PLUGIN_RUNNER_SIGNING_KEY)"],
        capture_output=True,
        text=True,
        env=environment,
        cwd=settings.BASE_DIR,
        check=True,
    )

    assert loaded.stdout.strip() == expected
