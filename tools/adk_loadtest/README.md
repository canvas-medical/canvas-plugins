# adk_loadtest

Load tests the Agent Development Kit: how many runs an instance drains and how wide, whether interactive chat turns jump a batch backlog, and whether scope leases hold under contention. Model calls go to a fake inference gateway, so a run costs no tokens and its timing is whatever the test sets.

- `adk_loadtest/gateway.py`: the fake gateway. It answers `POST /v1/messages` (streaming included) from a script in the request's system prompt, and takes latency and fault settings on `POST /control`; `GET /stats` reports calls served and the most in flight at once.
- `canvas__adk_loadtest/`: the plugin under test. Its probe agents run the scripted tool loop and record what they saw in Custom Data; its API starts runs and reads them back.
- `adk_loadtest/driver.py`: the scenario driver (`adk-loadtest --help`).

## Scenarios

| Scenario | What it starts | What it checks |
| --- | --- | --- |
| `throughput` | `--runs` (1000) batch runs, each on its own key | every run succeeds; reports runs/s, queue wait, and most at once |
| `priority` | the same backlog, plus `--chats` chat turns every `--chat-every` seconds | chat turns' p95 queue wait is under the batch runs' median |
| `chat-order` | `--chats` turns of one conversation, sent at once | each turn saw the turn before it; one ran at a time |
| `contention` | `--contention-runs` batch runs on one shared key | runs never overlapped, and the key's counter equals the run count |
| `extended` | `--extended-runs` runs of an agent declaring `run_seconds` 1800 | at most `--max-extended` ran at once |
| `faults` | `--fault-runs` batch runs with 5% 429s, 5% 500s, 2% 401s | every run reached a final status, the gateway served every run's calls, and some runs succeeded; reports retries and error kinds |

Batch runs come from the API-key endpoint, so they run as Canvas Bot at batch priority. Chat turns come from a staff session, so they queue as interactive.

## Running it

Against a local instance (`../canvas/home-app` with this repo mounted):

```sh
cd tools/adk_loadtest
uv sync
uv run uvicorn adk_loadtest.gateway:app --host 0.0.0.0 --port 8765 --workers 1
```

1. Point the instance at the gateway: set `INFERENCE_GATEWAY_URL=http://host.docker.internal:8765` in the plugin runner's environment, which builds every agent's gateway client from it, and restart it. A hosted instance needs the gateway at a URL it can reach.
2. Install the plugin, from the repo root: `uv run canvas install tools/adk_loadtest/canvas__adk_loadtest/canvas__adk_loadtest --host <instance>`.
3. Set its secrets: `simpleapi-api-key` to any string, and `INFERENCE_GATEWAY_KEY` to any string (the fake gateway accepts every key).
4. For `priority` and `chat-order`, log in to the instance as a staff member, copy the session's `Cookie` header, and pick a patient id.
5. Run the scenarios, with the API key and the session in the environment rather than on the command line:

```sh
export ADK_LOADTEST_API_KEY=<simpleapi-api-key>
export ADK_LOADTEST_SESSION_COOKIE='sessionid=...'
uv run adk-loadtest all \
  --instance http://localhost:8000 --patient-id <patient id> \
  --json report.json
```

The driver first starts one canary run and stops, exiting 2, unless it succeeds with model calls this fake gateway served. It exits 1 when any scenario's check fails. Each invocation tags its scenarios with a timestamp, so runs from earlier invocations do not mix into the results, and deletes each scenario's probe records and counters once it is read back. The platform's `AgentRun` rows stay.

Run on a development or load test instance only: the plugin starts agent runs on demand, and a 1000-run scenario fills the instance's agent queue for its duration. An instance other than localhost needs `--allow-remote-instance`.

## Tests

```sh
uv run pytest                                     # gateway, analysis, driver
cd canvas__adk_loadtest && uv run pytest          # the plugin
uv run canvas validate tools/adk_loadtest/canvas__adk_loadtest/canvas__adk_loadtest   # from the repo root
```
