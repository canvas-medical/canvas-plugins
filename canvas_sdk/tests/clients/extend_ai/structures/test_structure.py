from dataclasses import dataclass
from typing import Self

from canvas_sdk.clients.extend_ai.structures.structure import Structure


@dataclass
class ConcreteStructure(Structure):
    """Concrete implementation of Structure for testing abstract methods."""

    id: int
    name: str

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create a ConcreteStructure instance from a dictionary for testing."""
        return cls(id=data["id"], name=data["name"])

    def to_dict(self) -> dict:
        """Convert this ConcreteStructure to a dictionary for testing."""
        return {"id": self.id, "name": self.name}


def test_abstract_from_dict_body() -> None:
    """Test that calling abstract from_dict directly returns None."""
    result = Structure.from_dict({})
    expected = None
    assert result == expected


def test_abstract_to_dict_body() -> None:
    """Test that calling abstract to_dict directly returns None."""
    tested = ConcreteStructure(id=1, name="test")
    result = Structure.to_dict(tested)
    expected = None
    assert result == expected
