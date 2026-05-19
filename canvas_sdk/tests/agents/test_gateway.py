import pytest

from canvas_sdk.agents import LLMGateway, LLMGatewayConfigurationError


def test_llm_gateway_requires_api_key_and_model() -> None:
    """Both api_key and model are required positional fields."""
    gateway = LLMGateway(api_key="sk-test", model="claude-sonnet-4-6")
    assert gateway.api_key == "sk-test"
    assert gateway.model == "claude-sonnet-4-6"


def test_llm_gateway_base_url_defaults_to_none() -> None:
    """PoC: base_url is None so the Anthropic SDK uses its default endpoint."""
    gateway = LLMGateway(api_key="sk-test", model="claude-sonnet-4-6")
    assert gateway.base_url is None


def test_llm_gateway_accepts_base_url() -> None:
    """V1 will plumb a Canvas-gateway base_url through here."""
    gateway = LLMGateway(
        api_key="sk-session-tok",
        model="claude-sonnet-4-6",
        base_url="https://gateway.canvasmedical.com/v1",
    )
    assert gateway.base_url == "https://gateway.canvasmedical.com/v1"


# ---------------------------------------------------------------------------
# from_plugin_secrets
# ---------------------------------------------------------------------------


def test_from_plugin_secrets_uses_default_key_and_model_names() -> None:
    """Default key_name="ANTHROPIC_API_KEY", model_name="ANTHROPIC_MODEL"."""
    gateway = LLMGateway.from_plugin_secrets(
        {"ANTHROPIC_API_KEY": "sk-ant-test", "ANTHROPIC_MODEL": "claude-opus-4-7"}
    )
    assert gateway.api_key == "sk-ant-test"
    assert gateway.model == "claude-opus-4-7"


def test_from_plugin_secrets_falls_back_to_default_model() -> None:
    """When model_name isn't in secrets, default_model is used."""
    gateway = LLMGateway.from_plugin_secrets({"ANTHROPIC_API_KEY": "sk-ant-test"})
    assert gateway.api_key == "sk-ant-test"
    assert gateway.model == "claude-sonnet-4-6"  # the module-level default


def test_from_plugin_secrets_default_model_override() -> None:
    """Plugin authors can supply their own default model."""
    gateway = LLMGateway.from_plugin_secrets(
        {"ANTHROPIC_API_KEY": "sk-ant-test"},
        default_model="claude-haiku-4-5",
    )
    assert gateway.model == "claude-haiku-4-5"


def test_from_plugin_secrets_custom_key_name() -> None:
    """Plugin authors can pick any secret name for the key."""
    gateway = LLMGateway.from_plugin_secrets(
        {"MY_PROVIDER_KEY": "sk-custom"},
        key_name="MY_PROVIDER_KEY",
    )
    assert gateway.api_key == "sk-custom"


def test_from_plugin_secrets_missing_key_raises() -> None:
    """A missing API key surfaces as a typed configuration error."""
    with pytest.raises(LLMGatewayConfigurationError, match="ANTHROPIC_API_KEY"):
        LLMGateway.from_plugin_secrets({})


def test_from_plugin_secrets_empty_string_key_raises() -> None:
    """Empty-string secrets are treated as unset; otherwise the gateway would
    construct with an unusable key and fail at request time with an opaque
    auth error from Anthropic.
    """
    with pytest.raises(LLMGatewayConfigurationError):
        LLMGateway.from_plugin_secrets({"ANTHROPIC_API_KEY": ""})


# ---------------------------------------------------------------------------
# from_environment
# ---------------------------------------------------------------------------


def test_from_environment_reads_supplied_env_dict() -> None:
    """The ``env`` parameter lets tests bypass os.environ deterministically."""
    gateway = LLMGateway.from_environment(
        env={"ANTHROPIC_DEV_API_KEY": "sk-dev", "ANTHROPIC_DEV_MODEL": "claude-opus-4-7"}
    )
    assert gateway.api_key == "sk-dev"
    assert gateway.model == "claude-opus-4-7"


def test_from_environment_falls_back_to_default_model() -> None:
    """When model isn't in env, default_model is used."""
    gateway = LLMGateway.from_environment(env={"ANTHROPIC_DEV_API_KEY": "sk-dev"})
    assert gateway.model == "claude-sonnet-4-6"


def test_from_environment_missing_key_raises() -> None:
    """A missing env var surfaces as a typed configuration error."""
    with pytest.raises(LLMGatewayConfigurationError, match="ANTHROPIC_DEV_API_KEY"):
        LLMGateway.from_environment(env={})


def test_from_environment_reads_os_environ_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """Without an explicit env, the factory reads os.environ — the production path."""
    monkeypatch.setenv("ANTHROPIC_DEV_API_KEY", "sk-from-real-env")
    monkeypatch.setenv("ANTHROPIC_DEV_MODEL", "claude-from-env")

    gateway = LLMGateway.from_environment()
    assert gateway.api_key == "sk-from-real-env"
    assert gateway.model == "claude-from-env"
