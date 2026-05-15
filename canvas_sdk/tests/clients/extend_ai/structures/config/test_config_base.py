from canvas_sdk.clients.extend_ai.structures.config.config_base import ConfigBase
from canvas_sdk.clients.extend_ai.structures.structure import Structure


def test_class() -> None:
    """Test that ConfigBase is a subclass of Structure."""
    tested = ConfigBase
    assert issubclass(tested, Structure)


def test_processor_type() -> None:
    """Test that calling abstract processor_type method directly returns None."""
    result = ConfigBase.processor_type()
    expected = None
    assert result == expected
