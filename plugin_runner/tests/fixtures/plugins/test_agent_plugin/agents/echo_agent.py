import json

from canvas_sdk.agents import AgentPlugin, AgentRunResult, AgentState, LLMGateway, ToolRegistry
from canvas_sdk.effects import Effect, EffectType

tools = ToolRegistry()


@tools.tool(
    name="echo",
    description="Log the arguments.",
    input_schema={"type": "object"},
    effect_types=("LOG",),
)
def _echo(arguments: dict, *, ctx: dict) -> dict:
    """Stage a LOG effect carrying the arguments."""
    ctx["effects"].append(Effect(type=EffectType.LOG, payload=json.dumps(arguments)))
    return {"ok": True}


class EchoAgent(AgentPlugin):
    """Test agent: returns a single LOG effect carrying the trigger payload.

    The manifest grants its `echo` tool, which is what lets it return LOG effects.
    """

    tools = tools

    def load_state(self, scope_key: str) -> AgentState:
        """Stash the scope_key on the state so save_state can verify it round-trips."""
        return AgentState(data={"loaded_with": scope_key})

    def run(
        self,
        state: AgentState,
        gateway: LLMGateway,
        trigger_payload: dict,
    ) -> AgentRunResult:
        """Emit a LOG effect echoing the trigger payload plus the loaded scope_key."""
        payload = json.dumps(
            {
                "loaded_with": state.data.get("loaded_with"),
                "trigger": trigger_payload,
                "gateway_model": gateway.model,
            }
        )
        return AgentRunResult(
            state=state,
            effects=[Effect(type=EffectType.LOG, payload=payload)],
        )

    def save_state(self, scope_key: str, state: AgentState) -> None:
        """No-op for the test fixture; the runtime calls it after run() returns."""
        return None
