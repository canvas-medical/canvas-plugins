import os
import socketserver

SERVER_ADDRESS = (
    "localhost",
    os.getenv(
        "PLUGIN_RUNNER_LOG_PORT",
        6521,
    ),
)


class PluginLoggingHandler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        msg = self.rfile.readline().strip()
        print(msg)


def main() -> None:
    tcp_server = socketserver.ThreadingTCPServer(SERVER_ADDRESS, PluginLoggingHandler)
    tcp_server.serve_forever()


if __name__ == "__main__":
    main()
