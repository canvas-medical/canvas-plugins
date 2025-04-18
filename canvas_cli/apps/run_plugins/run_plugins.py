from plugin_runner.plugin_runner import main as run_server


def run_plugin(plugin_directory: str) -> None:
    """
    Run the specified plugin for local development.
    """
    return run_plugins([plugin_directory])


def run_plugins(plugin_directories: list[str]) -> None:
    """
    Run the specified plugins for local development.
    """
    run_server(plugin_directories)
    return
