from datetime import date
from typing import Self

from canvas_sdk.data import DataModel

from .data_access_layer_client import DAL_CLIENT


class Patient(DataModel):
    """Patient model."""

    id: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    birth_date: date | None = None

    @classmethod
    def get(cls, id: str) -> Self:
        """Given an ID, get the Patient from the Data Access Layer."""
        patient = DAL_CLIENT.get_patient(id)
        return cls(
            id=patient.id,
            first_name=patient.first_name or None,
            last_name=patient.last_name or None,
            birth_date=date.fromisoformat(patient.birth_date) if patient.birth_date else None,
        )
