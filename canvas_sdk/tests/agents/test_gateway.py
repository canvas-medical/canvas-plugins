from canvas_sdk.agents import LLMGateway


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
