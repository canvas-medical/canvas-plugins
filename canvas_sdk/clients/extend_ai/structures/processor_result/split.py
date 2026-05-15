from dataclasses import dataclass
from typing import Self

from canvas_sdk.clients.extend_ai.structures.structure import Structure


@dataclass(frozen=True)
class Split(Structure):
    """A document split identified by a splitter processor.

    Attributes:
        type: The type or category of this split.
        observation: Observations about this split.
        identifier: A unique identifier for this split.
        startPage: The starting page number of this split.
        endPage: The ending page number of this split.
        classificationId: The ID of the classification associated with this split.
        id: The unique ID for this split.
        fileId: The ID of the file this split belongs to.
        name: The name of this split.
    """

    type: str
    observation: str
    identifier: str
    startPage: int
    endPage: int
    classificationId: str
    id: str
    fileId: str
    name: str

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create a Split instance from a dictionary.

        Args:
            data: Dictionary containing split data from the API.

        Returns:
            A new Split instance.
        """
        return cls(
            type=data["type"],
            observation=data["observation"],
            identifier=data["identifier"],
            startPage=int(data["startPage"]),
            endPage=int(data["endPage"]),
            classificationId=data["classificationId"],
            id=data["id"],
            fileId=data["fileId"],
            name=data.get("name") or "",
        )

    def to_dict(self) -> dict:
        """Convert this Split to a dictionary.

        Returns:
            Dictionary representation suitable for API requests.
        """
        return {
            "type": self.type,
            "observation": self.observation,
            "identifier": self.identifier,
            "startPage": self.startPage,
            "endPage": self.endPage,
            "classificationId": self.classificationId,
            "id": self.id,
            "fileId": self.fileId,
            "name": self.name,
        }


__exports__ = ()
