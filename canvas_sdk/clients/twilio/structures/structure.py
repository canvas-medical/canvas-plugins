from abc import ABC, abstractmethod
from typing import Self


class Structure(ABC):
    """Abstract base class for data structures in the Twilio client.

    All data structures that represent API entities must inherit from this class
    and implement methods for serialization and deserialization.
    """

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict) -> Self:
        """Create an instance from a dictionary representation.

        Args:
            data: A dictionary containing the data for this structure.

        Returns:
            An instance of the structure.
        """
        ...

    @abstractmethod
    def to_dict(self) -> dict:
        """Convert this instance to a dictionary representation.

        Returns:
            A dictionary representation of this structure.
        """
        ...


__exports__ = ()
