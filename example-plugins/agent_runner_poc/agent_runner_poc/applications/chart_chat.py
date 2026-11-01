"""ChartChatApplication — patient-chart embedded chat UI.

Opens a right-pane modal backed by four SimpleAPI endpoints:

- ``GET /chart-chat-ui?patient={id}`` — serves the chat HTML.
- ``GET /chart-chat-history?patient={id}`` — returns existing conversation
  messages as JSON for the UI to render on load and once a run succeeds.
- ``POST /chart-chat-message`` — accepts ``{patient_id, message}``,
  emits a :class:`RunAgentEffect` for :class:`ChartChatAgent`, and
  returns ``202 Accepted`` with the run's ``run_id`` immediately. The
  agent runs asynchronously on the plugin-runner (Celery → ``RunAgent``
  RPC, same path as triggered agents).
- ``GET /chart-chat-run?run_id={id}`` — returns the run's status from the
  platform's :class:`AgentRun` record, which the UI polls until the run
  finishes.

Going through the standard ``RunAgentEffect`` path means the agent's
``load_state`` → ``run`` → ``save_state`` lifecycle runs one at a time
per patient and clinician — one clinician's concurrent messages
serialize naturally, the read-modify-write
of the conversation snapshot stays atomic, and the SimpleAPI request
thread is freed immediately (no long-lived plugin-runner worker held
for the LLM round-trip).
"""

from http import HTTPStatus
from typing import Any

from agent_runner_poc.agents.chart_chat import is_decisions_note, load_conversation_messages
from agent_runner_poc.agents.chart_chat_tools import tools as chart_chat_tools
from agent_runner_poc.agents.suggestions import split_suggestions
from canvas_sdk.agents import ToolRegistry
from canvas_sdk.agents.citations import Sources, cite
from canvas_sdk.effects import Effect
from canvas_sdk.effects.agent import DecideAgentProposal, RunAgentEffect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.effects.simple_api import HTMLResponse, JSONResponse, Response
from canvas_sdk.handlers.application import Application
from canvas_sdk.handlers.simple_api import SimpleAPI, StaffSessionAuthMixin, api
from canvas_sdk.templates import render_to_string
from canvas_sdk.v1.data import AgentRun, AgentRunProposal

CHART_CHAT_AGENT_ID = "agent_runner_poc.agents.chart_chat:ChartChatAgent"


class ChartChatApplication(Application):
    """Right-pane chat UI on the patient chart."""

    def on_open(self) -> Effect:
        """Launch the chat modal pointing at the GET endpoint that serves the UI."""
        patient_id = self.context["patient"]["id"]
        return LaunchModalEffect(
            url=f"/plugin-io/api/agent_runner_poc/chart-chat-ui?patient={patient_id}",
            target=LaunchModalEffect.TargetType.RIGHT_CHART_PANE,
            title="Chart chat",
        ).apply()


class ChartChatAPI(StaffSessionAuthMixin, SimpleAPI):
    """HTTP surface for the chat UI: serves HTML, returns history, accepts messages."""

    @api.get("/chart-chat-ui")
    def chart_chat_ui(self) -> list[Response | Effect]:
        """Render the chat UI HTML. Patient ID is read from the query string."""
        context = {"patient_id": self.request.query_params["patient"]}
        return [
            HTMLResponse(
                render_to_string("templates/chart_chat.html", context),
                status_code=HTTPStatus.OK,
            )
        ]

    @api.get("/chart-chat-history")
    def chart_chat_history(self) -> list[Response | Effect]:
        """Return the logged-in clinician's conversation so the UI can render and poll."""
        patient_id = self.request.query_params["patient"]
        staff_id = self.request.headers["canvas-logged-in-user-id"]
        messages = load_conversation_messages(patient_id, staff_id)
        return [
            JSONResponse(
                {"messages": _ui_messages(messages, chart_chat_tools)},
                status_code=HTTPStatus.OK,
            )
        ]

    @api.post("/chart-chat-message")
    def chart_chat_message(self) -> list[Response | Effect]:
        """Enqueue the agent run; return 202 and let the UI poll for the reply.

        Dispatch goes through the same ``RunAgentEffect`` →
        ``RunAgentEffectInterpreter`` → Celery → plugin-runner ``RunAgent``
        path as triggered agents. ``user_message`` rides on
        ``trigger_payload``; the agent appends it to the conversation
        snapshot while runs on the conversation's scope are serialized, so
        the read-modify-write stays atomic with any concurrent run.

        The platform takes the clinician from the session behind this request
        and scopes the run to the patient and that clinician, so each clinician
        has their own conversation and the agent attributes drafts to them.
        """
        body = self.request.json()
        run = RunAgentEffect(
            agent_id=CHART_CHAT_AGENT_ID,
            scope=RunAgentEffect.Scope.PATIENT_AND_STAFF,
            patient_id=body["patient_id"],
            trigger_payload={"user_message": body["message"]},
        )

        return [
            JSONResponse(
                {"status": "queued", "run_id": str(run.run_id)},
                status_code=HTTPStatus.ACCEPTED,
            ),
            run.apply(),
        ]

    @api.get("/chart-chat-run")
    def chart_chat_run(self) -> list[Response | Effect]:
        """Return where one of the logged-in clinician's runs stands, from the platform's record.

        A run the record does not show yet reads as queued: the interpreter writes
        the record as it enqueues the run.
        """
        staff_id = self.request.headers["canvas-logged-in-user-id"]
        run = AgentRun.objects.filter(
            id=self.request.query_params["run_id"],
            plugin_name="agent_runner_poc",
            staff__id=staff_id,
        ).first()
        if run is None:
            return [JSONResponse({"status": "queued", "error_kind": ""})]
        return [JSONResponse({"status": run.status, "error_kind": run.error_kind})]

    @api.get("/chart-chat-proposals")
    def chart_chat_proposals(self) -> list[Response | Effect]:
        """Return the changes one of the logged-in clinician's runs proposed, for approval cards."""
        staff_id = self.request.headers["canvas-logged-in-user-id"]
        proposals = AgentRunProposal.objects.filter(
            run__id=self.request.query_params["run_id"],
            plugin_name="agent_runner_poc",
            staff__id=staff_id,
        ).order_by("created_at")
        return [
            JSONResponse(
                {
                    "proposals": [
                        {
                            "id": str(proposal.id),
                            "tool": proposal.tool,
                            "arguments": proposal.arguments,
                            "status": proposal.status,
                            "reason": proposal.reason,
                            "expires_at": proposal.expires_at.isoformat(),
                        }
                        for proposal in proposals
                    ]
                }
            )
        ]

    @api.post("/chart-chat-decide")
    def chart_chat_decide(self) -> list[Response | Effect]:
        """Approve or deny a proposed change; the platform checks the decision is the clinician's.

        The platform accepts it only from this clinician, the one the agent acted for,
        while the proposal is pending, and applies exactly the proposed change. The agent
        records the outcome in the conversation at the start of its next run.
        """
        body = self.request.json()
        decision = DecideAgentProposal(
            proposal_id=body["proposal_id"],
            decision=body["decision"],
            reason=body.get("reason") or "",
        )
        return [
            JSONResponse({"status": "decided"}, status_code=HTTPStatus.ACCEPTED),
            decision.apply(),
        ]


def _ui_messages(stored: list[dict[str, Any]], tools: ToolRegistry) -> list[dict[str, Any]]:
    """Flatten the persisted message history into ``{role, text}`` pairs for the UI.

    Persisted messages can carry Anthropic block lists in their ``content``
    field (the assistant turns include ToolUseBlocks etc.); the UI only
    needs the human-readable text bits. Tool calls and tool results are
    elided — clinicians see the conversation, not the agent's plumbing — and so
    is the note of proposal decisions, which the approval cards already show.
    An assistant reply's suggested next steps come out of its text as ``chips``, and
    its citations become numbered references with a card for each in ``citations``,
    described from the rows ``tools`` returned earlier in the conversation; a citation
    of a record no tool returned is dropped.
    """
    out: list[dict[str, Any]] = []
    sources = Sources(tools)
    for message in stored:
        if is_decisions_note(message):
            continue
        role = message.get("role")
        if role not in {"user", "assistant"}:
            continue
        content = message.get("content")
        if isinstance(content, str):
            text = content.strip()
        elif isinstance(content, list):
            text = "\n".join(
                str(block.get("text", ""))
                for block in content
                if isinstance(block, dict) and block.get("type") == "text" and block.get("text")
            ).strip()
        else:
            continue
        if role == "assistant":
            text, chips = split_suggestions(text)
            text, citations = cite(text, sources)
            if text or chips:
                out.append(
                    {
                        "role": role,
                        "text": text,
                        "chips": chips,
                        "citations": [citation.to_dict() for citation in citations],
                    }
                )
        elif text:
            out.append({"role": role, "text": text})
        # A reply cites rows from earlier tool results, so a message's own calls and
        # results count only after its text.
        sources.add(message)
    return out
