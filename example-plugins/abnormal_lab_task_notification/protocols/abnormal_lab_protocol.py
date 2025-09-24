from canvas_sdk.effects import Effect
from canvas_sdk.effects.task import AddTask, TaskStatus
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from canvas_sdk.v1.data.lab import LabReport
from logger import log


class AbnormalLabProtocol(BaseProtocol):
    """
    A protocol that monitors lab reports and creates task notifications
    for abnormal lab values to ensure prompt review.
    
    Triggers on: LAB_REPORT_CREATED events
    Effects: Creates tasks for abnormal lab values
    """

    RESPONDS_TO = EventType.Name(EventType.LAB_REPORT_CREATED)

    def compute(self) -> list[Effect]:
        """
        This method gets called when a LAB_REPORT_CREATED event is fired.
        It checks for abnormal lab values and creates tasks for them.
        """
        # Get the lab report ID from the event target
        lab_report_id = self.event.target.id
        
        try:
            # Get the lab report instance
            lab_report = LabReport.objects.get(id=lab_report_id)
            
            # Check if the report is valid and not for test only
            if lab_report.for_test_only or lab_report.junked:
                return []
            
            # Get patient ID using the foreign key relationship
            if not lab_report.patient:
                log.warning(f"Lab report {lab_report_id} has no associated patient")
                return []
            
            patient_id = lab_report.patient.id
            
            # Check all lab values for abnormal flags
            abnormal_values = []
            for lab_value in lab_report.values.all():
                # Check if the lab value has an abnormal flag (handle None case)
                abnormal_flag = getattr(lab_value, 'abnormal_flag', None) or ""
                if abnormal_flag.strip():
                    abnormal_values.append(lab_value)
            
            if not abnormal_values:
                return []
            
            # Create a task for the abnormal lab values
            abnormal_count = len(abnormal_values)
            task_title = f"Review Abnormal Lab Values ({abnormal_count} abnormal)"
            
            # Create the task
            task = AddTask(
                patient_id=patient_id,
                title=task_title,
                status=TaskStatus.OPEN,
                labels=["abnormal-lab", "urgent-review"]
            )
            
            applied_task = task.apply()
            log.info(f"Created task for {abnormal_count} abnormal lab value(s) in report {lab_report_id}")
            return [applied_task]
            
        except LabReport.DoesNotExist:
            log.error(f"Lab report {lab_report_id} not found")
            return []
        except Exception as e:
            log.error(f"Error processing lab report {lab_report_id}: {str(e)}")
            return []