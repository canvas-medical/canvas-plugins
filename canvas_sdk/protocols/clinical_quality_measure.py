from typing import Any

from canvas_sdk.protocols.base import BaseProtocol


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
