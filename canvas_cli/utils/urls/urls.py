from urllib.parse import urljoin


class EndpointBuilderMixin:
    """Class that adds a url builder method."""

    _base_url: str = "core/api/v1"

    def __init__(self, value: str) -> None:
        self.value = value

    def build(self, host: str, *paths: str) -> str:
        """Builds a url from a host and a sequence of paths.
        Assumes this is injected into an enum subclass.
        """
        join = "/".join([self._base_url, self.value, "/".join(paths or [])])
        join = join if join.endswith("/") else join + "/"
        return urljoin(host, join)


class CoreEndpoint:
    """Class that defines and is able to build endpoints for the /core/ path."""

    _base_url: str = "core/api/v1"

    PLUGIN = EndpointBuilderMixin("plugins")
    LOG = EndpointBuilderMixin("logging")
