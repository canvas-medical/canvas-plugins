from canvas_sdk.data import DataModel

from .data_access_layer_client import DAL_CLIENT


class Staff(DataModel):
    id: str | None = None
    # TODO - populate with first name, last name, additional attributes, etc.

    @property
    def assigned_tasks(self):
        # TODO - fix circular import
        from canvas_sdk.data.task import Task
        staff_assigned_tasks = DAL_CLIENT.get_staff_assigned_tasks(id=self.id)
        task_list = []
        for task in staff_assigned_tasks.tasks:
            task_list.append(Task.from_grpc(task))
        return task_list
