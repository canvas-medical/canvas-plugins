from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import arrow

from canvas_sdk.events import EventType
from canvas_sdk.protocols.base import BaseProtocol
from canvas_sdk.protocols.timeframe import Timeframe
from canvas_sdk.v1.data import Patient
from canvas_sdk.v1.data.condition import Condition
from canvas_sdk.v1.data.lab import LabOrder, LabReport
from canvas_sdk.v1.data.medication import Medication
from canvas_sdk.v1.data.protocol_override import ProtocolOverride

if TYPE_CHECKING:
    from django.db.models import Model


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

    def __init__(self, *args: Any, **kwargs: Any):
        self._patient_id: str | None = None
        self.now = arrow.utcnow()
        super().__init__(*args, **kwargs)

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

    @staticmethod
    def relative_float(value: str) -> float:
        """Relative float method (better explanation needed here)."""
        try:
            sigma = 0.0
            if value[0] == "<" and value[1] != "=":
                sigma = -1e-6
            elif value[0] == ">" and value[1] != "=":
                sigma = +1e-6
            return float(value.strip("<≤=≥>")) + sigma
        except (ValueError, IndexError):
            return 0

    @property
    def timeframe(self) -> Timeframe:
        """The default Timeframe (self.timeframe) for all protocols.
        This defaults to have a start of 1 year ago and an end time of the current time.
        Plugin authors can override this if a different timeframe is desired.
        """
        end = self.now
        return Timeframe(start=end.shift(years=-1), end=end)

    # TODO: This approach should be considered against the alternative of just including the patient
    #  ID in the event context, given that so many events will be patient-centric.
    def patient_id_from_target(self) -> str:
        """
        Get and return the patient ID from an event target.

        This method will attempt to obtain the patient ID from the event target for supported event
        types. It stores the patient ID on a member variable so that it can be referenced without
        incurring more SQL queries.
        """

        def patient_id(model: type[Model]) -> str:
            if model == Patient:
                return self.event.target.id
            else:
                return cast(
                    str,
                    model._default_manager.select_related("patient")
                    .values_list("patient__id")
                    .get(id=self.event.target)[0],
                )

        models = {
            EventType.CONDITION_ASSESSED: Condition,
            EventType.CONDITION_CREATED: Condition,
            EventType.CONDITION_RESOLVED: Condition,
            EventType.CONDITION_UPDATED: Condition,
            EventType.LAB_ORDER_CREATED: LabOrder,
            EventType.LAB_ORDER_UPDATED: LabOrder,
            EventType.LAB_REPORT_CREATED: LabReport,
            EventType.LAB_REPORT_UPDATED: LabReport,
            EventType.MEDICATION_LIST_ITEM_CREATED: Medication,
            EventType.MEDICATION_LIST_ITEM_UPDATED: Medication,
            EventType.PATIENT_CREATED: Patient,
            EventType.PATIENT_UPDATED: Patient,
            EventType.PROTOCOL_OVERRIDE_CREATED: ProtocolOverride,
            EventType.PROTOCOL_OVERRIDE_DELETED: ProtocolOverride,
            EventType.PROTOCOL_OVERRIDE_UPDATED: ProtocolOverride,
        }

        if not self._patient_id:
            try:
                self._patient_id = patient_id(models[self.event.type])
            except KeyError as error:
                raise ValueError(
                    f"Event type {self.event.type} not supported by 'patient_id_from_event'"
                ) from error

        return self._patient_id


__exports__ = ("ClinicalQualityMeasure",)
