import json
from typing import Any

import arrow

from canvas__adk_loadtest.agents.tools import tools as _registered_tools
from canvas__adk_loadtest.models import Counter, ProbeRecord
from canvas_sdk.agents import AgentPlugin, AgentRunResult, AgentState, LLMGateway

DEFAULT_SCRIPT: dict[str, Any] = {"tools": [["find_note_types", {}]], "text": "done"}


def _system(script: dict[str, Any]) -> str:
    """The prompt the fake gateway reads its script from."""
    return f"Agent Development Kit load test probe. LOADTEST_SCRIPT={json.dumps(script)}"


def _read_counter(key: str) -> int:
    counter = Counter.objects.filter(key=key).first()
    return counter.value if counter is not None else 0


def _write_counter(key: str, value: int) -> None:
    counter = Counter.objects.filter(key=key).first()
    if counter is None:
        Counter.objects.create(key=key, value=value)
    else:
        counter.value = value
        counter.save()


class ProbeAgent(AgentPlugin):
    """Runs a scripted tool loop against the fake gateway and counts runs per scope.

    ``load_state`` reads the scope's counter, ``run`` drives the scripted loop, and
    ``save_state`` writes the counter back one higher with a record of the run. The
    lease runs one invocation at a time per scope, so K runs on one scope leave the
    counter at K; overlapping runs would read the same value and lose updates.
    """

    tools = _registered_tools
    KIND = "probe"

    def load_state(self, scope_key: str) -> AgentState:
        """The scope's counter, as this run found it."""
        return AgentState(data={"scope_key": scope_key, "saw": _read_counter(scope_key)})

    def run(
        self, state: AgentState, gateway: LLMGateway, trigger_payload: dict[str, Any]
    ) -> AgentRunResult:
        """Drive the scripted tool loop, timing it."""
        started = arrow.utcnow().datetime
        script = trigger_payload.get("script") or DEFAULT_SCRIPT
        result = self.run_tool_loop(
            gateway,
            system=_system(script),
            messages=[{"role": "user", "content": "Run the script."}],
            max_turns=len(script.get("tools") or []) + 2,
        )
        state.data.update(
            scenario=str(trigger_payload.get("scenario") or ""),
            seq=int(trigger_payload.get("seq") or 0),
            started_at=started.isoformat(),
            finished_at=arrow.utcnow().datetime.isoformat(),
        )
        return AgentRunResult(state=state, effects=result.effects)

    def save_state(self, scope_key: str, state: AgentState) -> None:
        """Count this run on its scope and record what it saw."""
        _write_counter(scope_key, state.data["saw"] + 1)
        ProbeRecord.objects.create(
            run_id=str(self.run_id),
            scenario=state.data["scenario"],
            kind=self.KIND,
            scope_key=scope_key,
            seq=state.data["seq"],
            saw=state.data["saw"],
            started_at=arrow.get(state.data["started_at"]).datetime,
            finished_at=arrow.get(state.data["finished_at"]).datetime,
        )


class ExtendedProbeAgent(ProbeAgent):
    """A ProbeAgent whose manifest asks for more than the default run time, so the
    plugin runner admits it only within its share of extended runs.
    """

    KIND = "extended"


class ChatProbeAgent(ProbeAgent):
    """A chat turn: records the previous turn it saw, so the driver can check that a
    conversation's messages run in the order they were sent.

    Its counter holds the last message number the conversation saw; each turn records
    that as ``saw`` and writes its own.
    """

    KIND = "chat"

    def save_state(self, scope_key: str, state: AgentState) -> None:
        """Make this turn the conversation's last, and record the turn before it."""
        _write_counter(scope_key, state.data["seq"])
        ProbeRecord.objects.create(
            run_id=str(self.run_id),
            scenario=state.data["scenario"],
            kind=self.KIND,
            scope_key=scope_key,
            seq=state.data["seq"],
            saw=state.data["saw"],
            started_at=arrow.get(state.data["started_at"]).datetime,
            finished_at=arrow.get(state.data["finished_at"]).datetime,
        )
