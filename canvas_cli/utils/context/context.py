import functools
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar, cast

import typer

from canvas_cli.utils.print import print

F = TypeVar("F", bound=Callable)


class CLIContext:
    """Class that handles configuration across the CLI.

    Includes methods for:
    * Loading a JSON file with configuration keys into memory.
    * Making a property transient (default, value is not persisted) or persistent (via decorators)

    Loading from a file is dynamic. I.e., you only need to create a new property,
    and mark its setter as persistent if needed.
    """

    # Path to the config file
    _config_file_path: Path

    # Dict with the config file values
    _config_file: dict[str, Any]

    # Base dir for the paths inside the project, not configurable
    _base_dir = Path(__file__).parent / ".." / ".."

    # Base dir for every template used, not configurable
    _base_template_dir: Path = _base_dir / "templates"

    # Dir where the plugin templates are located
    _plugin_template_dir: Path = _base_template_dir / "plugins"

    # Default plugin template name
    _default_plugin_template_name: str = "default"

    # The default host to use for requests
    _default_host: str | None = None

    # When the most recently requested api_token will expire
    _token_expiration_date: str | None = None

    @staticmethod
    def persistent(fn: F | None = None, **options: Any) -> Callable[[F], F] | F:
        """A decorator to store a config value in the file everytime it's changed."""

        def _decorator(fn: F) -> F:
            @functools.wraps(fn)
            def wrapper(self: "CLIContext", *args: Any, **kwargs: Any) -> Any:
                fn(self, *args, **kwargs)
                value = args[0]

                print(f"Storing {fn.__name__}={value} in the config file")

                self._config_file[fn.__name__] = value
                with open(self._config_file_path, "w") as f:
                    json.dump(self._config_file, f)

            return cast(F, wrapper)

        return _decorator(fn) if fn else _decorator

    @property
    def plugin_template_dir(self) -> Path:
        """Default Path to use for Plugin templates."""
        return self._plugin_template_dir

    @plugin_template_dir.setter
    @persistent
    def plugin_template_dir(self, new_plugin_template_dir: Path) -> None:
        self._plugin_template_dir = new_plugin_template_dir

    @property
    def default_plugin_template_name(self) -> str:
        """Default template to be used when creating a Plugin."""
        return self._default_plugin_template_name

    @default_plugin_template_name.setter
    @persistent
    def default_plugin_template_name(self, new_default_plugin_template_name: str) -> None:
        self._default_plugin_template_name = new_default_plugin_template_name

    @property
    def default_host(self) -> str | None:
        """Default host to be used when connecting to instances."""
        return self._default_host

    @default_host.setter
    @persistent
    def default_host(self, new_default_host: str | None) -> None:
        self._default_host = new_default_host

    @property
    def token_expiration_date(self) -> str | None:
        """When the most recently requested api_token will expire."""
        return self._token_expiration_date

    @token_expiration_date.setter
    @persistent
    def token_expiration_date(self, new_token_expiration_date: str) -> None:
        self._token_expiration_date = new_token_expiration_date

    def load_from_file(self, file: Path) -> None:
        """Load the given config file into a dict. Aborts execution if it can't decode the file.

        Args:
            file: Path to the JSON config file
        """
        try:
            self._config_file = json.load(file.open("rb"))
        except json.JSONDecodeError:
            print.json(
                "There was a problem loading the config file, please ensure it's valid JSON",
                success=False,
                path=str(file),
            )
            raise typer.Abort() from None

        self._config_file_path = file

        # Get all properties from the class that start with a single underscore,
        # and initialize it with the corresponding key from the config dictionary.
        # This generator assumes the config-file key and property will have the same name (minus the `_`)
        properties = [
            property
            for property in dir(self)
            if property not in ("_config_file", "_config_file_path")
            and not callable(getattr(self, property))
            and not property.startswith("__")
            and property.startswith("_")
        ]

        for property in properties:
            json_var = property[1:]
            if config_value := self._config_file.get(json_var):
                setattr(self, property, config_value)

    def print_config(self) -> None:
        """Print the currently loaded configuration."""
        print.json(message=None, config_file=self._config_file, path=str(self._config_file_path))


# CLIContext pseudo-singleton instance
context: CLIContext = CLIContext()
