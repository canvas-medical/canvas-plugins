from canvas_sdk.effects import Effect
from canvas_sdk.effects.task import AddTask, TaskStatus
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from canvas_sdk.v1.data.lab import LabReport
from canvas_sdk.v1.data.patient import Patient
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
        
        log.info(f"Processing lab report {lab_report_id} for abnormal values")
        
        try:
            # Get the lab report instance
            lab_report = LabReport.objects.get(id=lab_report_id)
            
            # Check if the report is valid and not for test only
            if lab_report.for_test_only or lab_report.junked:
                log.info(f"Skipping lab report {lab_report_id} - test only or junked")
                return []
            
            # Get patient ID
            patient_dbid = lab_report.patient_id
            if not patient_dbid:
                log.warning(f"Lab report {lab_report_id} has no associated patient")
                return []
            
            # Convert patient dbid to Canvas patient ID
            try:
                patient = Patient.objects.get(dbid=patient_dbid)
                patient_id = patient.id
                log.info(f"Converted patient dbid {patient_dbid} to Canvas ID {patient_id}")
            except Patient.DoesNotExist:
                log.error(f"Patient with dbid {patient_dbid} not found")
                return []
            
            # Check all lab values for abnormal flags
            abnormal_values = []
            for lab_value in lab_report.values.all():
                # Check if the lab value has an abnormal flag (handle None case)
                abnormal_flag = getattr(lab_value, 'abnormal_flag', None) or ""
                if abnormal_flag.strip():
                    abnormal_values.append(lab_value)
                    log.info(f"Found abnormal lab value: {lab_value.id} with flag: {abnormal_flag}")
            
            if not abnormal_values:
                log.info(f"No abnormal values found in lab report {lab_report_id}")
                return []
            
            # Create a task for the abnormal lab values
            abnormal_count = len(abnormal_values)
            task_title = f"Review Abnormal Lab Values ({abnormal_count} abnormal)"
            
            # Create the task description with details about abnormal values
            value_details = []
            for value in abnormal_values:
                abnormal_flag = getattr(value, 'abnormal_flag', None) or ""
                detail = f"- {abnormal_flag}"
                if hasattr(value, 'value') and value.value:
                    detail += f": {value.value}"
                if hasattr(value, 'units') and value.units:
                    detail += f" {value.units}"
                if hasattr(value, 'reference_range') and value.reference_range:
                    detail += f" (ref: {value.reference_range})"
                value_details.append(detail)
            
            # Create the task
            log.info(f"Creating task with patient_id: {patient_id}, title: {task_title}")
            task = AddTask(
                patient_id=patient_id,
                title=task_title,
                status=TaskStatus.OPEN,
                labels=["abnormal-lab", "urgent-review"]
            )
            
            log.info(f"Task object created - patient_id: {task.patient_id}, title: {task.title}, status: {task.status.value}")
            try:
                applied_task = task.apply()
                log.info(f"Task applied successfully - Effect type: {applied_task.type}")
                log.info(f"Task Effect created for abnormal lab values in report {lab_report_id}")
                return [applied_task]
            except Exception as e:
                log.error(f"Error applying task: {str(e)}")
                log.error(f"Error type: {type(e)}")
                import traceback
                log.error(f"Traceback: {traceback.format_exc()}")
                return []
            
        except LabReport.DoesNotExist:
            log.error(f"Lab report {lab_report_id} not found")
            return []
        except Exception as e:
            log.error(f"Error processing lab report {lab_report_id}: {str(e)}")
            return []