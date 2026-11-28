"""Confine the plugin runner's network to an allowlist of hosts.

When `PLUGIN_RUNNER_EGRESS_ALLOWLIST` is set, `python -m plugin_runner.egress -- COMMAND`
runs the runner in its own user, network, and mount namespaces, whose only interface is
loopback. Everything the runner reaches crosses the namespace boundary through a relay over
a Unix socket:

- HTTP and HTTPS go through tinyproxy outside, which allows the listed hosts plus the ones
  the runner itself needs (plugin packages, logs, errors, Canvas services) and refuses the
  rest. Inside, `HTTPS_PROXY` and `HTTP_PROXY` point at its relay.
- Postgres, Redis, and statsd each get their own relay. Inside, their hostnames resolve to
  those relays, so clients keep their configured names and TLS verification.
- home-app reaches the runner over gRPC on `PLUGIN_RUNNER_GRPC_SOCKET`.

There is no DNS inside and no route out, so a client that ignores the proxy settings
cannot connect anywhere. The runner runs without capabilities.

Modules: `config` (what may be reached), `supervisor` (outside), `confine` (inside),
`relay` (the relays), `process` (running a child), `linux` (the system calls).
"""
