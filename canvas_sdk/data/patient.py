from datetime import datetime
from typing import Self

from pydantic import BaseModel as Model

from . import data_access_layer_client as dal_client


# TODO: Sync this model with Joe's PR
class Patient(Model):
    """Patient model."""

    id: str | None
    first_name: str
    last_name: str
    birth_date: datetime

    @classmethod
    def get(cls, id: str) -> Self:
        """Given an ID, get the Patient from the Data Access Layer."""
        patient = dal_client.get_patient(id)
        return cls(
            id=patient.id,
            first_name=patient.first_name,
            last_name=patient.last_name,
            birth_date=patient.birth_date,
        )
