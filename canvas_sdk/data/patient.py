from datetime import date, datetime
from typing import Self, TYPE_CHECKING

from pydantic import computed_field

from canvas_sdk.data import DataModel
from canvas_sdk.data.staff import Staff
from canvas_sdk.data.team import Team

from .data_access_layer_client import DAL_CLIENT

if TYPE_CHECKING:
    from canvas_sdk.data.task import Task


class Patient(DataModel):
    """Patient model."""

    id: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    birth_date: date | None = None


    # @computed_field
    @property
    def tasks(self) -> list["Task"]:
        # TODO - fix circular imports
        from canvas_sdk.data.task import Task
        task_list = []
        patient_tasks = DAL_CLIENT.get_patient_tasks(self.id)
        for task in patient_tasks.tasks:
            task_instance = Task(
                id=task.id,
                title=task.title,
                status=Task.Status(task.status),
                assignee=Staff(id=task.assignee.id),
                patient=Patient(id=task.patient.id),
                due=datetime.fromisoformat(task.due),
                created=datetime.fromisoformat(task.created),
                modified=datetime.fromisoformat(task.modified),
                team=Team(id=task.team.id),
                task_type=task.task_type,
                creator=Staff(id=task.creator.id)
            )
            task_list.append(task_instance)
        return task_list

    @classmethod
    def get(cls, id: str) -> Self:
        """Given an ID, get the Patient from the Data Access Layer."""
        patient = DAL_CLIENT.get_patient(id)
        return cls(
            id=id,
            first_name=patient.first_name or None,
            last_name=patient.last_name or None,
            birth_date=date.fromisoformat(patient.birth_date) if patient.birth_date else None,
        )
