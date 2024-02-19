import json
import os
from pathlib import Path

import pytest
import typer

from canvas_cli.utils.context import CLIContext


class CLIContextTestHelper(CLIContext):
    """CLIContext subclass that defines some properties we can test."""

    _persistent_mock_property: str | None = None
    _transient_mock_property: bool = False

    @property
    def persistent_mock_property(self) -> str | None:
        """Mock persistent property."""
        return self._persistent_mock_property

    @persistent_mock_property.setter
    @CLIContext.persistent
    def persistent_mock_property(self, new_persistent_mock_property: str | None) -> None:
        self._persistent_mock_property = new_persistent_mock_property

    @property
    def transient_mock_property(self) -> bool:
        """Mock transient property."""
        return self._transient_mock_property

    @transient_mock_property.setter
    def transient_mock_property(self, new_transient_mock_property: bool) -> None:
        self._transient_mock_property = new_transient_mock_property


@pytest.fixture
def config_file(tmp_path: Path) -> Path:
    """Fixture that yields an empty config file and cleans up after itself."""
    config_file = tmp_path / "mock_config.json"
    yield config_file
    os.remove(config_file)


@pytest.fixture
def valid_mock_config_file(config_file: Path) -> Path:
    """Fixture that yields a valid mock config file."""
    mock_config = {
        "persistent_mock_property": "mock-value",
    }
    with open(config_file, "w") as f:
        json.dump(mock_config, f)

    yield config_file


@pytest.fixture
def invalid_json_mock_config_file(config_file: Path) -> Path:
    """Fixture that yields an invalid config file."""
    config_file.write_text("Absolutely invalid JSON")

    yield config_file


@pytest.fixture
def invalid_properties_mock_config_file(config_file: Path) -> Path:
    """Fixture that yields a valid mock config file."""
    mock_config = {
        "unknown-property": "mock-value",
    }
    with open(config_file, "w") as f:
        json.dump(mock_config, f)

    yield config_file


def test_valid_load_from_file(valid_mock_config_file: Path) -> None:
    """Test loading a valid config file."""
    context = CLIContextTestHelper()
    context.load_from_file(valid_mock_config_file)

    assert context.persistent_mock_property == "mock-value"


def test_invalid_load_from_file(invalid_json_mock_config_file: Path) -> None:
    """Test loading an invalid config file aborts the execution."""
    context = CLIContextTestHelper()

    with pytest.raises(typer.Abort):
        context.load_from_file(invalid_json_mock_config_file)


def test_load_invalid_property(invalid_properties_mock_config_file: Path) -> None:
    """Since we dynamically load the properties, this test ensures that unknown properties don't throw exceptions."""
    context = CLIContextTestHelper()

    context.load_from_file(invalid_properties_mock_config_file)


def test_config_persistence(valid_mock_config_file: Path) -> None:
    """Test marking a property with @persistent stores the value in the config file."""
    context = CLIContextTestHelper()
    context.load_from_file(valid_mock_config_file)

    assert context.persistent_mock_property == "mock-value"

    context.persistent_mock_property = "new-value"

    # This won't ever happen but since the values are in memory, we need to create a new context instance,
    # as if mimicking a new program launch
    context_b = CLIContextTestHelper()
    context_b.load_from_file(valid_mock_config_file)

    assert context_b.persistent_mock_property == "new-value"


def test_config_transience(valid_mock_config_file: Path) -> None:
    """Test the properties transient default."""
    context = CLIContextTestHelper()
    context.load_from_file(valid_mock_config_file)

    assert context.transient_mock_property is False
    context.transient_mock_property = True

    # This won't ever happen but since the values are in memory, we need to create a new context instance,
    # as if mimicking a new program launch
    context_b = CLIContextTestHelper()
    context_b.load_from_file(valid_mock_config_file)

    assert context_b.transient_mock_property is False
