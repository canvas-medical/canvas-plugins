from dataclasses import dataclass


@dataclass
class LLMGateway:
    """LLM access handed to AgentPlugin.run() by the run_agent worker.

    PoC: ``api_key`` is a developer Anthropic key sourced from a worker
    environment variable, ``base_url`` is None (the Anthropic SDK uses its
    default endpoint), and the plugin calls Anthropic directly.

    V1 (per the Agent Runner Framework doc §6.10): ``api_key`` becomes a
    short-lived session token and ``base_url`` points at the Canvas LLM
    gateway, which materializes the real per-customer subaccount key at the
    HTTP boundary and writes audit/cost rows there. Plugin code does not
    change shape between PoC and V1.
    """

    api_key: str
    model: str
    base_url: str | None = None


__exports__ = ("LLMGateway",)
