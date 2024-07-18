from datetime import datetime
from typing import Self

from canvas_sdk.data import DataModel

from . import data_access_layer_client as dal_client


class Patient(DataModel):
    """Patient model."""

    id: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    birth_date: datetime | None = None

    @classmethod
    def get(cls, id: str) -> Self:
        """Given an ID, get the Patient from the Data Access Layer."""
        patient = dal_client.get_patient(id)
        return cls(  # type: ignore[call-arg]
            id=patient.id,
            first_name=patient.first_name,
            last_name=patient.last_name,
            birth_date=patient.birth_date,
        )
