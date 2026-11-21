"""Run the plugin runner, confined to its egress allowlist when one is set.

    python -m plugin_runner.egress -- python -m plugin_runner.plugin_runner

With no allowlist the command replaces this process, unconfined.
"""

import logging
import os
import sys

from plugin_runner.egress import config, supervisor


def main(argv: list[str]) -> int:
    """Run the command after `--`, confined when the allowlist is set."""
    if len(argv) < 2 or argv[0] != "--":
        raise SystemExit(__doc__)
    command = argv[1:]

    egress = config.load()
    if egress is None:
        os.execvp(command[0], command)

    logging.basicConfig(level=logging.INFO, format="plugin-runner egress: %(message)s")
    return supervisor.supervise(egress, command)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
