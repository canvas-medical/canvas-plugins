import jwt
import pytest

from plugin_runner.authentication import token_for_plugin

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


def test_token_for_plugin_rejects_an_empty_signing_key() -> None:
    """Test that an unconfigured signing key fails instead of signing with an empty key."""
    with pytest.raises(ValueError, match="PLUGIN_RUNNER_SIGNING_KEY"):
        token_for_plugin(plugin_name="example_plugin", audience="home", jwt_signing_key="")
