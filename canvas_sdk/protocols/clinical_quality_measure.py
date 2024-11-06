from typing import Any

import arrow

from canvas_sdk.protocols.base import BaseProtocol
from canvas_sdk.protocols.timeframe import Timeframe


class ClinicalQualityMeasure(BaseProtocol):
    """
    The class that ClinicalQualityMeasure protocols inherit from.
    """

    class Meta:
        title: str = ""
        identifiers: list[str] = []
        description: str = ""
        information: str = ""
        references: list[str] = []
        source_attributes: dict[str, str]
        types: list[str] = []
        authors: list[str] = []
        show_in_chart: bool = True
        show_in_population: bool = True
        can_be_snoozed: bool = True
        is_abstract: bool = False
        is_predictive: bool = False

    @classmethod
    def _meta(cls) -> dict[str, Any]:
        """
        Meta properties of the protocol in dictionary form.
        """
        base_meta = {
            k: v for k, v in ClinicalQualityMeasure.Meta.__dict__.items() if not k.startswith("__")
        }
        class_meta = {k: v for k, v in cls.Meta.__dict__.items() if not k.startswith("__")}

        return base_meta | class_meta

    @classmethod
    def protocol_key(cls) -> str:
        """
        External key used to identify the protocol.
        """
        return cls.__name__

    @property
    def timeframe(self) -> Timeframe:
        """The default Timeframe (self.timeframe) for all protocols.
        This defaults to have a start of 1 year ago and an end time of the current time.
        Plugin authors can override this if a different timeframe is desired.
        """
        end = self.now
        return Timeframe(start=end.shift(years=-1), end=end)

    @property
    def now(self) -> arrow.Arrow:
        """A convenience method for returning the current datetime."""
        return arrow.utcnow()
