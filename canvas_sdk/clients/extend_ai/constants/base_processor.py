from enum import Enum


class BaseProcessor(Enum):
    """Base processor types available in Extend AI.

    Each processor type has performance and light variants, where performance
    provides better accuracy at the cost of higher resource usage, and light
    provides faster processing with reduced resource consumption.
    """

    CLASSIFICATION_PERFORMANCE = "classification_performance"
    CLASSIFICATION_LIGHT = "classification_light"
    EXTRACTION_PERFORMANCE = "extraction_performance"
    EXTRACTION_LIGHT = "extraction_light"
    SPLITTING_PERFORMANCE = "splitting_performance"
    SPLITTING_LIGHT = "splitting_light"


__exports__ = ()
