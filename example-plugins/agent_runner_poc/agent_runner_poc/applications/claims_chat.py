"""ClaimsChatApplication — a claims chat for billing staff, opened from the app launcher.

A global application, so it opens on any page, the revenue pages included. It starts
in queue mode; a claim id in the agent's reply links to that claim's own conversation
(``?claim=<id>``), and the page links back to the queue conversation.

Backed by four SimpleAPI endpoints, in the chart chat's shape:

- ``GET /claims-chat-ui[?claim={id}]`` serves the chat HTML.
- ``GET /claims-chat-history[?claim={id}]`` returns the logged-in staff member's
  conversation.
- ``POST /claims-chat-message`` takes ``{claim_id?, message}``, emits a
  :class:`RunAgentEffect` for :class:`ClaimsChatAgent`, and returns ``202`` with the
  run's id. With a claim the run is ``Scope.CLAIM``, which the platform refuses unless
  the claim exists and the staff member has the revenue capability; without one it is
  ``Scope.STAFF``.
- ``GET /claims-chat-run?run_id={id}`` returns where the run stands, with the
  platform's reason when it refused the run.

The plugin reads no claim data itself: every claim the staff member sees comes through
the agent's tools, which the platform gates on the revenue capability.
"""

from http import HTTPStatus

from agent_runner_poc.agents.claims_chat import load_claims_conversation
from agent_runner_poc.applications.chart_chat import _ui_messages
from canvas_sdk.effects import Effect
from canvas_sdk.effects.agent import RunAgentEffect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.effects.simple_api import HTMLResponse, JSONResponse, Response
from canvas_sdk.handlers.application import Application
from canvas_sdk.handlers.simple_api import SimpleAPI, StaffSessionAuthMixin, api
from canvas_sdk.templates import render_to_string
from canvas_sdk.v1.data import AgentRun

CLAIMS_CHAT_AGENT_ID = "agent_runner_poc.agents.claims_chat:ClaimsChatAgent"


class ClaimsChatApplication(Application):
    """The claims chat, launched from anywhere in Canvas."""

    def on_open(self) -> Effect:
        """Open the chat in queue mode."""
        return LaunchModalEffect(
            url="/plugin-io/api/agent_runner_poc/claims-chat-ui",
            target=LaunchModalEffect.TargetType.DEFAULT_MODAL,
            title="Claims chat",
        ).apply()


class ClaimsChatAPI(StaffSessionAuthMixin, SimpleAPI):
    """HTTP surface for the claims chat UI."""

    def _claim_id(self) -> str:
        return self.request.query_params.get("claim", "")

    @api.get("/claims-chat-ui")
    def claims_chat_ui(self) -> list[Response | Effect]:
        """Render the chat page for the queues, or for the claim in the query string."""
        return [
            HTMLResponse(
                render_to_string("templates/claims_chat.html", {"claim_id": self._claim_id()}),
                status_code=HTTPStatus.OK,
            )
        ]

    @api.get("/claims-chat-history")
    def claims_chat_history(self) -> list[Response | Effect]:
        """Return the logged-in staff member's conversation for the claim, or the queues."""
        staff_id = self.request.headers["canvas-logged-in-user-id"]
        messages = load_claims_conversation(staff_id, self._claim_id() or None)
        return [JSONResponse({"messages": _ui_messages(messages)}, status_code=HTTPStatus.OK)]

    @api.post("/claims-chat-message")
    def claims_chat_message(self) -> list[Response | Effect]:
        """Enqueue the agent run in claim or queue mode; return 202 and the run's id."""
        body = self.request.json()
        claim_id = body.get("claim_id") or None
        trigger_payload = {"user_message": body["message"]}
        if claim_id:
            run = RunAgentEffect(
                agent_id=CLAIMS_CHAT_AGENT_ID,
                scope=RunAgentEffect.Scope.CLAIM,
                claim_id=claim_id,
                trigger_payload=trigger_payload,
            )
        else:
            run = RunAgentEffect(
                agent_id=CLAIMS_CHAT_AGENT_ID,
                scope=RunAgentEffect.Scope.STAFF,
                trigger_payload=trigger_payload,
            )
        return [
            JSONResponse(
                {"status": "queued", "run_id": str(run.run_id)},
                status_code=HTTPStatus.ACCEPTED,
            ),
            run.apply(),
        ]

    @api.get("/claims-chat-run")
    def claims_chat_run(self) -> list[Response | Effect]:
        """Return where one of the logged-in staff member's runs stands.

        A refused run carries the platform's reason, such as a missing revenue
        capability, which the UI shows as is.
        """
        staff_id = self.request.headers["canvas-logged-in-user-id"]
        run = AgentRun.objects.filter(
            id=self.request.query_params["run_id"],
            plugin_name="agent_runner_poc",
            agent_id=CLAIMS_CHAT_AGENT_ID,
            staff__id=staff_id,
        ).first()
        if run is None:
            return [JSONResponse({"status": "queued", "error_kind": "", "error": ""})]
        return [
            JSONResponse(
                {
                    "status": run.status,
                    "error_kind": run.error_kind,
                    "error": run.error if run.status == "refused" else "",
                }
            )
        ]
