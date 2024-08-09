from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from logger import log

from canvas_sdk.data.patient import Patient
from canvas_sdk.data.staff import Staff
from canvas_sdk.data.task import Task


class Protocol(BaseProtocol):
    RESPONDS_TO = EventType.Name(EventType.ASSESS_COMMAND__CONDITION_SELECTED)

    def compute(self):
        task = Task.get(id="e590e137-4d64-41c0-b97a-b10cfc3eb85f")
        log.info("\n\n")
        log.info(f"Task id {task.id}")
        log.info(f"       assignee id: {task.assignee.id}")
        log.info(f"       title: {task.title}")
        log.info(f"       patient id: {task.patient.id}")
        log.info(f"       due: {task.due}")
        log.info(f"       status: {task.status}")
        log.info(f"       created: {task.created}")
        log.info(f"       modified: {task.modified}")
        log.info(f"       team id: {task.team.id}")
        log.info(f"       task_type: {task.task_type}")
        log.info(f"       creator id: {task.creator.id}")

        log.info("\n")
        log.info(f"       labels: {task.labels}")

        log.info("\n")
        log.info(f"       comments: {task.comments}")

        log.info("\n\n")


        patient = Patient.get(id="eef3b60624bb44418dfe24875153dbd9")
        log.info("Patient Tasks: \n\n")
        log.info(patient.tasks)
        log.info("\n\n")

        staff = Staff(id="4150cd20de8a470aa570a852859ac87e")
        log.info("Staff Assigned Tasks: \n\n")
        log.info(staff.assigned_tasks)

        log.info("\n\n")
        return []
