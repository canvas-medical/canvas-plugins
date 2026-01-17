from enum import Enum


class ProcessorType(Enum):
    """Types of processors available in Extend AI.

    EXTRACT: Extracts structured data from documents based on a schema.
    CLASSIFY: Classifies documents into predefined categories.
    SPLITTER: Splits documents into separate sections or parts.
    """

    EXTRACT = "EXTRACT"
    CLASSIFY = "CLASSIFY"
    SPLITTER = "SPLITTER"


__exports__ = ()
