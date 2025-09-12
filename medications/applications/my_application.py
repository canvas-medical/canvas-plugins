from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.handlers.application import Application
import json
from canvas_sdk.v1.data import Patient, MedicationStatement, StopMedicationEvent


class MyApplication(Application):
    """An embeddable application that can be registered to Canvas."""

    def on_open(self) -> Effect:
        data = {}
        patient = Patient.objects.get(id=self.event.context["patient"]["id"])
        med_stmts = MedicationStatement.objects.filter(patient=patient)
        for med_stmt in med_stmts:
            key = f"med_stmt{med_stmt.dbid}"
            data[key] = {
                "id": str(med_stmt.dbid),
                "created": str(med_stmt.created),
                "modified": str(med_stmt.modified),
                "originator": {
                    "dbid": med_stmt.originator.dbid,
                    "email": med_stmt.originator.email,
                },
                "committer": (
                    {
                        "dbid": med_stmt.committer.dbid,
                        "email": med_stmt.committer.email,
                    }
                    if med_stmt.committer
                    else {}
                ),
                "entered_in_error": (
                    {
                        "dbid": med_stmt.entered_in_error.dbid,
                        "email": med_stmt.entered_in_error.email,
                    }
                    if med_stmt.entered_in_error
                    else {}
                ),
                "patient": {
                    "id": str(med_stmt.patient.id),
                    "dbid": med_stmt.patient.dbid,
                    "first_name": med_stmt.patient.first_name,
                },
                "note": {
                    "id": str(med_stmt.note.id),
                    "datetime": str(med_stmt.note.datetime_of_service),
                },
                "medication": {
                    "id": str(med_stmt.medication.id),
                    "clinical_quantity_description": med_stmt.medication.clinical_quantity_description,
                    "coding_display": med_stmt.medication.codings.first().display,
                },
                "indications": [
                    {
                        "dbid": indication.dbid,
                        "narrative": indication.narrative,
                        "condition_id": str(indication.condition.id),
                        "condition_coding_display": indication.condition.codings.first().display,
                    }
                    for indication in med_stmt.indications.all()
                ],
                "start_date_original_input": med_stmt.start_date_original_input,
                "start_date": str(med_stmt.start_date),
                "end_date_original_input": med_stmt.end_date_original_input,
                "end_date": str(med_stmt.end_date),
                "dose_quantity": med_stmt.dose_quantity,
                "dose_form": med_stmt.dose_form,
                "dose_route": med_stmt.dose_route,
                "dose_frequency": med_stmt.dose_frequency,
                "dose_frequency_interval": med_stmt.dose_frequency_interval,
                "sig_original_input": med_stmt.sig_original_input,
            }
        data["patient_med_stmts"] = [
            f"med_stmt{str(med_stmt.dbid)}" for med_stmt in patient.medication_statements.all()
        ]
        patient_assessments = patient.assessments.all()
        data["indication_med_stmts"] = {
            f"indication{assessment.dbid}": [
                f"med_stmt{str(med_stmt.dbid)}" for med_stmt in assessment.treatments_stated.all()
            ]
            for assessment in patient_assessments
        }

        stop_med_evts = StopMedicationEvent.objects.filter(patient=patient)
        for stop_med_evt in stop_med_evts:
            key = f"stop_med_evt{stop_med_evt.dbid}"
            data[key] = {
                "id": str(stop_med_evt.dbid),
                "created": str(stop_med_evt.created),
                "modified": str(stop_med_evt.modified),
                "originator": {
                    "dbid": stop_med_evt.originator.dbid,
                    "email": stop_med_evt.originator.email,
                },
                "committer": (
                    {
                        "dbid": stop_med_evt.committer.dbid,
                        "email": stop_med_evt.committer.email,
                    }
                    if stop_med_evt.committer
                    else {}
                ),
                "entered_in_error": (
                    {
                        "dbid": stop_med_evt.entered_in_error.dbid,
                        "email": stop_med_evt.entered_in_error.email,
                    }
                    if stop_med_evt.entered_in_error
                    else {}
                ),
                "patient": {
                    "id": str(stop_med_evt.patient.id),
                    "dbid": stop_med_evt.patient.dbid,
                    "first_name": stop_med_evt.patient.first_name,
                },
                "note": {
                    "id": str(stop_med_evt.note.id),
                    "datetime": str(stop_med_evt.note.datetime_of_service),
                },
                "medication": {
                    "dbid": stop_med_evt.medication.dbid,
                    "clinical_quantity_description": stop_med_evt.medication.clinical_quantity_description,
                    "coding_display": stop_med_evt.medication.codings.first().display,
                },
                "rationale": stop_med_evt.rationale,
            }
        data["patient_stop_med_evts"] = [
            f"stop_med_evt{str(stop_med_evt.dbid)}"
            for stop_med_evt in patient.stopped_medications.all()
        ]

        patient_meds = patient.medications.all()
        data["medication_stop_med_events"] = {
            f"med{med.dbid}": [
                f"stop_med_evt{str(stop_med_evt.dbid)}"
                for stop_med_evt in med.stopmedicationevent_set.all()
            ]
            for med in patient_meds
        }

        return LaunchModalEffect(
            content=f"""<pre id="json-output">{json.dumps(data, indent=4)}</pre>""",
            target=LaunchModalEffect.TargetType.RIGHT_CHART_PANE_LARGE,
        ).apply()
