from abc import ABC, abstractmethod
from typing import Any

from canvas_sdk.agents.capabilities import Capability
from canvas_sdk.agents.gateway import LLMGateway
from canvas_sdk.agents.note_helpers import find_open_note
from canvas_sdk.agents.result import AgentRunResult
from canvas_sdk.agents.state import AgentState
from canvas_sdk.agents.subject import RunRequester, RunSubject
from canvas_sdk.agents.tool_loop import ToolLoopResult, run_tool_loop
from canvas_sdk.agents.tool_registry import ToolRegistry

# The tool context keys AgentPlugin.tool_context sets from the run.
TOOL_CONTEXT_KEYS = frozenset(
    {
        "patient_id",
        "staff_id",
        "note_id",
        "claim_id",
        "permissions",
        "capabilities",
        "effects",
        "gateway",
        "parent_tools",
    }
)


class AgentPlugin(ABC):
    """Base class for agents invoked by the ``run_agent`` Celery task.

    Not a :class:`canvas_sdk.handlers.BaseHandler`: agents do not register
    for events and have no ``compute()``. A trigger handler (which IS a
    :class:`BaseHandler`) emits a ``RunAgentEffect``; the platform
    interpreter enqueues the ``run_agent`` task; the worker instantiates
    this class by class path and invokes the three required methods in
    order — ``load_state`` → ``run`` → ``save_state``. Runs of one agent
    on one ``scope_key`` happen one at a time, each starting after the
    previous run's effects have been applied.
    """

    # The agent's tool registry. Set as a class attribute by subclasses
    # to the module-level registry the agent uses (e.g., ``tools =
    # chart_chat_tools_registry``). Before ``run()`` fires, the
    # platform replaces this with a *scoped* view containing only the
    # tools the manifest's ``components.agents[].tools`` grants; an agent
    # whose manifest grants nothing gets an empty registry. The agent uses
    # ``self.tools.definitions()`` / ``self.tools.execute(...)`` directly
    # and the ungranted entries aren't reachable.
    #
    # The grant also bounds the agent's output: the platform drops any
    # effect in ``AgentRunResult.effects`` whose type no granted tool
    # declares (``ToolRegistry.effect_types``), so building an effect
    # directly, or through the module-level registry, can't widen it.
    tools: ToolRegistry | None = None

    # The tool names the manifest grants this run, set by the platform on
    # the agent instance before lifecycle hooks fire. Empty when the
    # manifest grants none.
    tools_allowed: frozenset[str] = frozenset()

    # The most model calls one run may make, sub-agents included. run_tool_loop stops
    # with stopped="call_limit" when a run reaches it. Override on the subclass.
    max_model_calls: int = 40

    # What this run is about, validated by the platform and set on the agent
    # instance before lifecycle hooks fire. ``run_tool_loop`` hands it to every
    # tool, so tools act on the platform's patient, not one the agent chose.
    subject: RunSubject = RunSubject()

    # Who started this run, taken by the platform from the event and set with the subject.
    requester: RunRequester = RunRequester()

    # What this run may do beyond its manifest's tool grant, decided by the platform
    # from the requester's permissions and set with the subject.
    capabilities: frozenset[Capability] = frozenset()

    # This run's id, the id of its canvas_sdk.v1.data.AgentRun record, set by the
    # platform with the subject. Plugin-owned audit rows can carry it to join that record.
    run_id: str = ""

    @abstractmethod
    def load_state(self, scope_key: str) -> AgentState:
        """Load this run's starting state from per-EHR storage."""
        ...

    @abstractmethod
    def run(
        self,
        state: AgentState,
        gateway: LLMGateway,
        trigger_payload: dict[str, Any],
    ) -> AgentRunResult:
        """Drive the agent. Return updated state and effects to emit."""
        ...

    @abstractmethod
    def save_state(self, scope_key: str, state: AgentState) -> None:
        """Write the updated state back to per-EHR storage."""
        ...

    def on_run_start(self, scope_key: str) -> None:
        """Optional hook fired before ``load_state``. Default: no-op."""
        return None

    def on_turn(self, turn_index: int) -> None:
        """Optional hook fired before each LLM call ``run_tool_loop`` makes. Default: no-op."""
        return None

    def run_tool_loop(
        self,
        gateway: LLMGateway,
        *,
        system: str,
        messages: list[dict[str, Any]],
        ctx: dict[str, Any] | None = None,
        **options: Any,
    ) -> ToolLoopResult:
        """Run :func:`canvas_sdk.agents.run_tool_loop` with this agent's tools and hooks.

        Uses ``self.tools``, the registry scoped to the manifest's grant, and calls
        :meth:`on_turn` before each LLM call. The tools get the context
        :meth:`tool_context` builds, plus any extra keys in ``ctx``. The effects the
        tools stage come back on :attr:`ToolLoopResult.effects`. ``options`` are the
        remaining ``run_tool_loop`` arguments (``max_turns``, ``max_tokens``,
        ``model``, ``history_chars``, ``cache_system``).
        """
        return run_tool_loop(
            gateway,
            tools=self.tools or ToolRegistry(),
            ctx=self.tool_context(gateway, ctx),
            system=system,
            messages=messages,
            on_turn=self.on_turn,
            **options,
        )

    def tool_context(
        self, gateway: LLMGateway, extra: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """The context every tool call of this run receives.

        Holds the run's subject (``patient_id``, ``note_id``, ``claim_id``), its
        requester's ``staff_id`` and ``permissions``, its ``capabilities``, a fresh
        ``effects`` list, and the ``gateway`` and ``parent_tools`` that composition
        tools hand to sub-agents. ``note_id`` is the subject's note, or for a run a
        staff member started, that staff member's open note on the patient.
        ``extra`` adds agent-specific keys and cannot replace any of these.
        """
        extra = extra or {}
        if reserved := sorted(TOOL_CONTEXT_KEYS & extra.keys()):
            raise ValueError(
                f"{reserved} are set from the run; pass only agent-specific keys in ctx"
            )
        subject = self.subject
        staff_id = self.requester.staff_id
        note_id = subject.note_id
        if note_id is None and subject.patient_id and staff_id:
            note = find_open_note(subject.patient_id, provider_id=staff_id)
            note_id = str(note.id) if note is not None else None
        return {
            **extra,
            "patient_id": subject.patient_id,
            "staff_id": staff_id,
            "note_id": note_id,
            "claim_id": subject.claim_id,
            "permissions": self.requester.permissions,
            "capabilities": frozenset(self.capabilities),
            "effects": [],
            "gateway": gateway,
            "parent_tools": self.tools,
        }

    def on_run_end(self, result: AgentRunResult) -> None:
        """Optional hook fired after ``run`` returns successfully. Default: no-op."""
        return None

    def on_run_error(self, exc: BaseException) -> None:
        """Optional hook fired if ``run`` raises. Default: no-op."""
        return None


__exports__ = ("AgentPlugin",)
