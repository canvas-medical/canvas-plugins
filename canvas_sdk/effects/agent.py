from typing import Annotated, Any

from pydantic import Field

from canvas_sdk.effects.base import EffectType, _BaseEffect


class RunAgentEffect(_BaseEffect):
    """Request that the platform invoke an :class:`AgentPlugin` in a worker.

    Plugin authors return this from a trigger handler's ``compute()`` to
    hand control off to the agent runtime. The platform's
    ``RunAgentEffectInterpreter`` enqueues a ``run_agent`` Celery task that
    instantiates the referenced agent class, acquires the per-``scope_key``
    lock (V1), and drives ``load_state`` → ``run`` → ``save_state``.

    Fields:
        agent_id: Class path of the :class:`AgentPlugin` subclass to instantiate,
            in ``module.path:ClassName`` form.
        scope_key: Per-``(agent_id, scope_key)`` namespace tuple used for
            state-store keying and (V1) single-flight locking.
        trigger_payload: Small dict carrying trigger-shaped data the agent
            needs in ``run``. Keep it small — full agent state is loaded
            from per-EHR storage inside ``load_state``, not threaded through
            this payload.

    Example::

        return [RunAgentEffect(
            agent_id="my_plugin.agents.chart_summary:ChartSummary",
            scope_key="my_plugin:chart_summary:patient:abc123",
            trigger_payload={"note_id": note_id, "patient_id": patient_id},
        )]
    """

    class Meta:
        effect_type = EffectType.RUN_AGENT

    agent_id: Annotated[str, Field(min_length=1)]
    scope_key: Annotated[str, Field(min_length=1)]
    trigger_payload: dict[str, Any] = Field(default_factory=dict)

    @property
    def values(self) -> dict[str, Any]:
        """Serialize the run-agent request into the effect payload."""
        return {
            "agent_id": self.agent_id,
            "scope_key": self.scope_key,
            "trigger_payload": self.trigger_payload,
        }


__exports__ = ("RunAgentEffect",)
