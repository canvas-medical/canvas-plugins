"""The driver's way in: start probe runs, and read back what they did.

``LoadTestAPI`` authenticates with the plugin's ``simpleapi-api-key`` secret, so its
runs are Canvas Bot's and queue at batch priority. ``LoadTestChatAPI`` takes a staff
session, so its runs are a staff member's and queue as interactive.
"""

from http import HTTPStatus
from typing import Any

from canvas__arf_loadtest.models import Counter, ProbeRecord
from canvas_sdk.effects import Effect
from canvas_sdk.effects.agent import RunAgentEffect
from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.handlers.simple_api import APIKeyAuthMixin, SimpleAPI, StaffSessionAuthMixin, api
from canvas_sdk.v1.data import AgentRun

PLUGIN_NAME = "canvas__arf_loadtest"
PROBE_AGENT = f"{PLUGIN_NAME}.agents.probe:ProbeAgent"
EXTENDED_AGENT = f"{PLUGIN_NAME}.agents.probe:ExtendedProbeAgent"
CHAT_AGENT = f"{PLUGIN_NAME}.agents.probe:ChatProbeAgent"

# The most runs one fanout request starts: every effect a handler returns is applied in
# one batch, and the driver makes as many requests as a scenario needs.
MAX_FANOUT = 100
# The most runs one /runs request reads back.
MAX_READ = 1000


def scope_id(scenario: str, index: int, shared: bool) -> str:
    """The key a probe run serializes on: its own, or the scenario's one shared key."""
    return f"loadtest:{scenario}:shared" if shared else f"loadtest:{scenario}:{index}"


def _body(api: SimpleAPI) -> dict[str, Any]:
    """The request's JSON object, or an empty one."""
    body = api.request.json()
    return dict(body) if isinstance(body, dict) else {}


def _whole_number(body: dict[str, Any], name: str) -> int | None:
    """``body[name]`` as an int, 0 when it is missing, or None when it is not a whole number."""
    value = body.get(name)
    if value is None:
        return 0
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    return None


def _bad_request(message: str) -> list[Response | Effect]:
    return [JSONResponse({"error": message}, status_code=HTTPStatus.BAD_REQUEST)]


def _run_row(run: AgentRun) -> dict[str, Any]:
    return {
        "run_id": str(run.id),
        "agent_id": run.agent_id,
        "scope_key": run.scope_key,
        "status": run.status,
        "error_kind": run.error_kind,
        "attempts": run.attempts,
        "model_calls": run.model_calls,
        "queued_at": run.queued_at.isoformat() if run.queued_at else None,
        "started_at": run.started_at.isoformat() if run.started_at else None,
        "finished_at": run.finished_at.isoformat() if run.finished_at else None,
    }


def _record_row(record: ProbeRecord) -> dict[str, Any]:
    return {
        "run_id": record.run_id,
        "kind": record.kind,
        "scope_key": record.scope_key,
        "seq": record.seq,
        "saw": record.saw,
        "started_at": record.started_at.isoformat(),
        "finished_at": record.finished_at.isoformat(),
    }


class LoadTestAPI(APIKeyAuthMixin, SimpleAPI):
    """Starts batch probe runs and reports runs, probe records, and counters."""

    @api.post("/fanout")
    def fanout(self) -> list[Response | Effect]:
        """Start ``count`` probe runs for a scenario, numbered from ``start``.

        Body: ``scenario``, ``count`` (at most 100), ``start`` (default 0), ``shared``
        (every run on one key), ``extended`` (the extended probe), ``script`` (the fake
        gateway's script).
        """
        body = _body(self)
        scenario = str(body.get("scenario") or "")
        count = _whole_number(body, "count")
        start = _whole_number(body, "start")
        if not scenario or count is None or not 0 < count <= MAX_FANOUT:
            return _bad_request(f"scenario is required and count must be 1 to {MAX_FANOUT}")
        if start is None or start < 0:
            return _bad_request("start must be a whole number, 0 or more")
        shared = bool(body.get("shared"))
        agent_id = EXTENDED_AGENT if body.get("extended") else PROBE_AGENT
        runs = [
            RunAgentEffect(
                agent_id=agent_id,
                scope=RunAgentEffect.Scope.KEY,
                scope_id=scope_id(scenario, start + index, shared),
                trigger_payload={
                    "scenario": scenario,
                    "seq": start + index,
                    "script": body.get("script") or {},
                },
            )
            for index in range(count)
        ]
        return [
            JSONResponse(
                {"run_ids": [str(run.run_id) for run in runs]}, status_code=HTTPStatus.ACCEPTED
            ),
            *(run.apply() for run in runs),
        ]

    @api.post("/runs")
    def runs(self) -> list[Response | Effect]:
        """The platform's record and the probe's record of each run in ``run_ids``."""
        run_ids = [str(run_id) for run_id in _body(self).get("run_ids") or []]
        if len(run_ids) > MAX_READ:
            return _bad_request(f"at most {MAX_READ} run_ids per request")
        runs = AgentRun.objects.filter(plugin_name=PLUGIN_NAME, id__in=run_ids)
        records = ProbeRecord.objects.filter(run_id__in=run_ids)
        return [
            JSONResponse(
                {
                    "runs": [_run_row(run) for run in runs],
                    "records": [_record_row(record) for record in records],
                }
            )
        ]

    @api.get("/counter")
    def counter(self) -> list[Response | Effect]:
        """A scope key's counter: runs completed, or a conversation's last message."""
        key = self.request.query_params.get("key", "")
        found = Counter.objects.filter(key=key).first()
        return [JSONResponse({"key": key, "value": found.value if found else 0})]

    @api.post("/clear")
    def clear(self) -> list[Response | Effect]:
        """Delete a scenario's probe records and counters, so it can run again."""
        scenario = str(_body(self).get("scenario") or "")
        if not scenario:
            return _bad_request("scenario is required")
        records = ProbeRecord.objects.filter(scenario=scenario)
        scope_keys = set(records.values_list("scope_key", flat=True))
        Counter.objects.filter(key__in=scope_keys).delete()
        deleted, _ = records.delete()
        return [JSONResponse({"deleted": deleted})]


class LoadTestChatAPI(StaffSessionAuthMixin, SimpleAPI):
    """Starts one chat turn as the logged-in staff member, so it queues as interactive."""

    @api.post("/chat")
    def chat(self) -> list[Response | Effect]:
        """Start the chat probe for message ``seq`` of the staff member's chat on a patient.

        Body: ``scenario``, ``seq``, ``patient_id``, ``script``.
        """
        body = _body(self)
        scenario = str(body.get("scenario") or "")
        patient_id = str(body.get("patient_id") or "")
        if not scenario or not patient_id:
            return _bad_request("scenario and patient_id are required")
        seq = _whole_number(body, "seq")
        if seq is None:
            return _bad_request("seq must be a whole number")
        run = RunAgentEffect(
            agent_id=CHAT_AGENT,
            scope=RunAgentEffect.Scope.PATIENT_AND_STAFF,
            patient_id=patient_id,
            trigger_payload={
                "scenario": scenario,
                "seq": seq,
                "script": body.get("script") or {},
            },
        )
        return [
            JSONResponse({"run_id": str(run.run_id)}, status_code=HTTPStatus.ACCEPTED),
            run.apply(),
        ]
