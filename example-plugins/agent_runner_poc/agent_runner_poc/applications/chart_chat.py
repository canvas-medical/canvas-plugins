"""ChartChatApplication — patient-chart embedded chat UI.

Opens a right-pane modal that talks to two SimpleAPI endpoints:

- ``GET /chart-chat-ui?patient={id}`` — serves the chat HTML.
- ``GET /chart-chat-history?patient={id}`` — returns existing conversation
  messages as JSON for the UI to render on load.
- ``POST /chart-chat-message`` — accepts ``{patient_id, message}``,
  synchronously invokes :class:`ChartChatAgent`, and returns the agent's
  response text. Inline-synchronous (no Celery hop) so the UI gets a
  response within the request's HTTP lifecycle.

Like the triggered invocation path, this handler reads the Anthropic
key from the plugin's own secrets via :meth:`LLMGateway.from_plugin_secrets`
— declared as ``ANTHROPIC_API_KEY`` in the manifest's ``variables`` list
and configured per-customer in the home-app admin. The lock primitive
(:func:`canvas_sdk.agents.agent_lock`) is acquired in-process here just
as it would be on the plugin-runner during a triggered run; contention
returns HTTP 409.
"""

from http import HTTPStatus
from typing import Any

from agent_runner_poc.agents.chart_chat import ChartChatAgent
from agent_runner_poc.models.conversation import Conversation
from canvas_sdk.agents import (
    AgentLocked,
    LLMGateway,
    LLMGatewayConfigurationError,
    agent_lock,
)
from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.effects.simple_api import HTMLResponse, JSONResponse, Response
from canvas_sdk.handlers.application import Application
from canvas_sdk.handlers.simple_api import SimpleAPI, StaffSessionAuthMixin, api
from canvas_sdk.templates import render_to_string


def _scope_key(patient_id: str) -> str:
    """Scope-key shape for the chat agent — patient-keyed, plugin-prefixed."""
    return f"agent_runner_poc:chart_chat:patient:{patient_id}"


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
        """Return existing conversation messages so the UI can render on load."""
        patient_id = self.request.query_params["patient"]
        conversation = Conversation.objects.filter(patient__id=patient_id).first()
        messages = list(conversation.messages or []) if conversation else []
        return [
            JSONResponse(
                {"messages": _ui_messages(messages)},
                status_code=HTTPStatus.OK,
            )
        ]

    @api.post("/chart-chat-message")
    def chart_chat_message(self) -> list[Response | Effect]:
        """Invoke the agent synchronously and return the assistant's response."""
        body = self.request.json()
        patient_id: str = body["patient_id"]
        user_message: str = body["message"]

        try:
            gateway = LLMGateway.from_plugin_secrets(self.secrets)
        except LLMGatewayConfigurationError as exc:
            return [
                JSONResponse(
                    {"error": str(exc)},
                    status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                )
            ]

        # Inline invocation — load_state, run, save_state run in this HTTP
        # request rather than via the run_agent Celery task. Different
        # invocation path, same AgentPlugin contract.
        #
        # agent_lock prevents two parallel messages on the same scope_key
        # (same patient's chat) from racing on the snapshot state — without
        # it, two concurrent POSTs would both load the same baseline and
        # the last save_state would clobber the other's turn. On contention
        # we return 409; the UI can surface "the previous message is still
        # being answered" rather than silently dropping a turn.
        scope_key = _scope_key(patient_id)
        try:
            with agent_lock(scope_key):
                agent = ChartChatAgent()
                state = agent.load_state(scope_key)
                result = agent.run(
                    state,
                    gateway,
                    {"patient_id": patient_id, "user_message": user_message},
                )
                agent.save_state(scope_key, result.state)
        except AgentLocked:
            return [
                JSONResponse(
                    {"error": "The agent is still responding to a previous message."},
                    status_code=HTTPStatus.CONFLICT,
                )
            ]

        return [
            JSONResponse(
                {"response": result.state.data.get("last_response", "")},
                status_code=HTTPStatus.OK,
            )
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
