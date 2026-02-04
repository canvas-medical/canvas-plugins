from abc import abstractmethod
from dataclasses import dataclass

from canvas_sdk.clients.extend_ai.constants.processor_type import ProcessorType
from canvas_sdk.clients.extend_ai.structures.structure import Structure


@dataclass(frozen=True)
class ConfigBase(Structure):
    """Abstract base class for processor configurations.

    All processor configurations must inherit from this class and implement
    the processor_type method to specify their processor type.
    """

    @classmethod
    @abstractmethod
    def processor_type(cls) -> ProcessorType:
        """Get the processor type for this configuration.

        Returns:
            The ProcessorType enum value for this configuration.
        """
        ...


__exports__ = ()
