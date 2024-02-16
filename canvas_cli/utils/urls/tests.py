import pytest

from canvas_cli.utils.urls import CoreEndpoint


@pytest.mark.parametrize("path", ["a-path", "/a-path", "/a-path/", "a-path/"])
def test_endpoint_builder(path: str) -> None:
    """Test that the endpoint is always generated with a trailing `/`."""
    assert (
        CoreEndpoint.LOG.build("https://test-host.com", path)
        == "https://test-host.com/core/api/v1/logging/a-path/"
    )
