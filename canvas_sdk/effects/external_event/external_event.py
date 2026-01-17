import json
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_generated.messages.effects_pb2 import Effect
from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.v1.data.external_event import ExternalEvent as ExternalEventModel


class ExternalEvent(TrackableFieldsModel):
    """
    Effect to create or update an External Event in Canvas.

    External events represent clinical events from external data sources (ADT feeds, etc.)
    such as admissions, discharges, and transfers.

    Example (create):
        effect = ExternalEvent(
            patient_id="patient-uuid",
            visit_identifier="visit-123",
            message_control_id="msg-456",
            event_type="ADT^A01",
        )
        return effect.create()

    Example (update):
        effect = ExternalEvent(
            external_event_id="existing-event-uuid",
            event_cancelation_datetime=datetime.now(),
        )
        return effect.update()
    """

    class Meta:
        effect_type = "EXTERNAL_EVENT"

    external_event_id: str | UUID | None = None  # For updates
    patient_id: str | None = None
    visit_identifier: str | None = None
    message_control_id: str | None = None
    event_type: str | None = None
    event_datetime: datetime | None = None
    event_cancelation_datetime: datetime | None = None
    message_datetime: datetime | None = None
    information_source: str | None = None
    facility_name: str | None = None
    raw_message: str | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """Validate the external event data."""
        errors = super()._get_error_details(method)

        if method == "create":
            if self.external_event_id:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "External event ID should not be set when creating a new external event.",
                        self.external_event_id,
                    )
                )
            if not self.patient_id:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "Field 'patient_id' is required to create an external event.",
                        self.patient_id,
                    )
                )
            if not self.visit_identifier:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "Field 'visit_identifier' is required to create an external event.",
                        self.visit_identifier,
                    )
                )
            if not self.message_control_id:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "Field 'message_control_id' is required to create an external event.",
                        self.message_control_id,
                    )
                )
            if not self.event_type:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "Field 'event_type' is required to create an external event.",
                        self.event_type,
                    )
                )

        if method == "update":
            if not self.external_event_id:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "Field 'external_event_id' is required to update an external event.",
                        self.external_event_id,
                    )
                )
            elif not ExternalEventModel.objects.filter(id=self.external_event_id).exists():
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"External event with ID {self.external_event_id} does not exist.",
                        self.external_event_id,
                    )
                )

        return errors

    def create(self) -> Effect:
        """Create a new External Event."""
        self._validate_before_effect("create")

        payload = {"data": self.values}

        return Effect(
            type=f"CREATE_{self.Meta.effect_type}",
            payload=json.dumps(payload),
        )

    def update(self) -> Effect:
        """Update an existing External Event."""
        self._validate_before_effect("update")

        payload = {"data": self.values}

        return Effect(
            type=f"UPDATE_{self.Meta.effect_type}",
            payload=json.dumps(payload),
        )


__exports__ = ("ExternalEvent",)
