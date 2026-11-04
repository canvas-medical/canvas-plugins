# canvas__arf_loadtest

Probe agents for load testing the Agent Runner Framework. They run scripted tool loops against the fake inference gateway in `tools/arf_loadtest` and record what each run saw, so the driver can measure throughput and check ordering and locking. See `tools/arf_loadtest/README.md`.

Install only on a development or load test instance: its API starts agent runs on demand.
