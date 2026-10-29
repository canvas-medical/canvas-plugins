"""ChartChatApplication — patient-chart embedded chat UI.

Opens a right-pane modal backed by three SimpleAPI endpoints:

- ``GET /chart-chat-ui?patient={id}`` — serves the chat HTML.
- ``GET /chart-chat-history?patient={id}`` — returns existing conversation
  messages as JSON for the UI to render on load and to poll while a
  response is in flight.
- ``POST /chart-chat-message`` — accepts ``{patient_id, message}``,
  emits a :class:`RunAgentEffect` for :class:`ChartChatAgent`, and
  returns ``202 Accepted`` immediately. The agent runs asynchronously
  on the plugin-runner (Celery → ``RunAgent`` RPC, same path as
  triggered agents); the UI polls ``/chart-chat-history`` until the
  assistant turn lands.

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

from agent_runner_poc.agents.chart_chat import load_conversation_messages
from canvas_sdk.effects import Effect
from canvas_sdk.effects.agent import RunAgentEffect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.effects.simple_api import HTMLResponse, JSONResponse, Response
from canvas_sdk.handlers.application import Application
from canvas_sdk.handlers.simple_api import SimpleAPI, StaffSessionAuthMixin, api
from canvas_sdk.templates import render_to_string

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
                {"messages": _ui_messages(messages)},
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

        return [
            JSONResponse(
                {"status": "queued"},
                status_code=HTTPStatus.ACCEPTED,
            ),
            RunAgentEffect(
                agent_id=CHART_CHAT_AGENT_ID,
                scope=RunAgentEffect.Scope.PATIENT_AND_STAFF,
                patient_id=body["patient_id"],
                trigger_payload={"user_message": body["message"]},
            ).apply(),
        ]


def _ui_messages(stored: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Flatten the persisted message history into ``{role, text}`` pairs for the UI.

    Persisted messages can carry Anthropic block lists in their ``content``
    field (the assistant turns include ToolUseBlocks etc.); the UI only
    needs the human-readable text bits. Tool calls and tool results are
    elided — clinicians see the conversation, not the agent's plumbing.
    """
    out: list[dict[str, str]] = []
    for message in stored:
        role = message.get("role")
        content = message.get("content")
        if isinstance(content, str):
            if role in {"user", "assistant"} and content.strip():
                out.append({"role": role, "text": content})
            continue
        if isinstance(content, list):
            text_parts: list[str] = []
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    text_parts.append(str(block.get("text", "")))
            joined = "\n".join(part for part in text_parts if part).strip()
            if joined and role in {"user", "assistant"}:
                out.append({"role": role, "text": joined})
    return out
