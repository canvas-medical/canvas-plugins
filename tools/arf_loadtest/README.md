# arf_loadtest

Load tests the Agent Runner Framework: how many runs an instance drains and how wide, whether interactive chat turns jump a batch backlog, and whether scope leases hold under contention. Model calls go to a fake inference gateway, so a run costs no tokens and its timing is whatever the test sets.

- `arf_loadtest/gateway.py`: the fake gateway. It answers `POST /v1/messages` (streaming included) from a script in the request's system prompt, and takes latency and fault settings on `POST /control`; `GET /stats` reports calls served and the most in flight at once.
- `canvas__arf_loadtest/`: the plugin under test. Its probe agents run the scripted tool loop and record what they saw in Custom Data; its API starts runs and reads them back.
- `arf_loadtest/driver.py`: the scenario driver (`arf-loadtest --help`).

## Scenarios

| Scenario | What it starts | What it checks |
| --- | --- | --- |
| `throughput` | `--runs` (1000) batch runs, each on its own key | every run succeeds; reports runs/s, queue wait, and most at once |
| `priority` | the same backlog, plus `--chats` chat turns every `--chat-every` seconds | chat turns' p95 queue wait is under the batch runs' median |
| `chat-order` | `--chats` turns of one conversation, sent at once | each turn saw the turn before it; one ran at a time |
| `contention` | `--contention-runs` batch runs on one shared key | runs never overlapped, and the key's counter equals the run count |
| `extended` | `--extended-runs` runs of an agent declaring `run_seconds` 1800 | at most `--max-extended` ran at once |
| `faults` | `--fault-runs` batch runs with 5% 429s, 5% 500s, 2% 401s | every run reached a final status; reports retries and error kinds |

Batch runs come from the API-key endpoint, so they run as Canvas Bot at batch priority. Chat turns come from a staff session, so they queue as interactive.

## Running it

Against a local instance (`../canvas/home-app` with this repo mounted):

```sh
cd tools/arf_loadtest
uv sync
uv run uvicorn arf_loadtest.gateway:app --host 0.0.0.0 --port 8765 --workers 1
```

1. Point the instance at the gateway: set `INFERENCE_GATEWAY_URL=http://host.docker.internal:8765` in the plugin runner's environment, which builds every agent's gateway client from it, and restart it. A hosted instance needs the gateway at a URL it can reach.
2. Install the plugin, from the repo root: `uv run canvas install tools/arf_loadtest/canvas__arf_loadtest/canvas__arf_loadtest --host <instance>`.
3. Set its secrets: `simpleapi-api-key` to any string (the driver's `--api-key`), and `INFERENCE_GATEWAY_KEY` to any string (the fake gateway accepts every key).
4. For `priority` and `chat-order`, log in to the instance as a staff member, copy the session's `Cookie` header, and pick a patient id.
5. Run the scenarios:

```sh
uv run arf-loadtest all \
  --instance http://localhost:8000 --api-key <key> \
  --session-cookie 'sessionid=...' --patient-id <patient id> \
  --json report.json
```

The driver exits 1 when any check fails. Each invocation tags its scenarios with a timestamp, so runs from earlier invocations do not mix into the results.

Run on a development or load test instance only: the plugin starts agent runs on demand, and a 1000-run scenario fills the instance's agent queue for its duration.

## Tests

```sh
uv run pytest                                     # gateway, analysis, driver
cd canvas__arf_loadtest && uv run pytest          # the plugin
uv run canvas validate tools/arf_loadtest/canvas__arf_loadtest/canvas__arf_loadtest   # from the repo root
```
