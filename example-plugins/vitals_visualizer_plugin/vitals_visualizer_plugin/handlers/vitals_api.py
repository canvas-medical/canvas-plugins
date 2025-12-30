import json
from typing import Any

from canvas_sdk.effects.simple_api import HTMLResponse, JSONResponse
from canvas_sdk.handlers.simple_api import SimpleAPIRoute, StaffSessionAuthMixin
from canvas_sdk.templates import render_to_string
from canvas_sdk.v1.data import Observation
from logger import log


class VitalsVisualizerAPI(StaffSessionAuthMixin, SimpleAPIRoute):
    """API endpoint that serves vitals visualization data and UI."""

    PATH = "/visualize"

    def get(self) -> list[HTMLResponse | JSONResponse]:
        """Return the vitals visualization UI and data."""
        patient_id = self.request.query_params.get("patient_id")

        if not patient_id:
            return [JSONResponse({"error": "Patient ID is required"}, status_code=400)]

        try:
            vitals_data = self._get_vitals_data(patient_id)
            html_content = self._generate_visualization_html(vitals_data)
            return [HTMLResponse(content=html_content)]

        except Exception as e:
            log.error(f"Error in VitalsVisualizerAPI: {str(e)}")
            return [JSONResponse({"error": str(e)}, status_code=500)]

    def _get_vitals_data(self, patient_id: str) -> dict[str, list[dict[str, Any]]]:
        """Get vitals data for the patient using Canvas vitals structure."""
        try:
            # Get individual vital observations from vital signs panels
            vital_observations = (
                Observation.objects.for_patient(patient_id)
                .filter(
                    category="vital-signs",
                    effective_datetime__isnull=False,
                )
                .exclude(name="Vital Signs Panel")
                .exclude(entered_in_error__isnull=False)
                .select_related("is_member_of")
                .order_by("effective_datetime")
            )

            vitals_data: dict[str, list[dict[str, object]]] = {
                "weight": [],
                "body_temperature": [],
                "oxygen_saturation": [],
            }

            for obs in vital_observations:
                if not obs.value or obs.name in ["note", "pulse_rhythm"]:
                    continue

                if obs.name == "weight":
                    try:
                        value_oz = float(obs.value)
                        value_lbs = value_oz / 16
                        vitals_data["weight"].append(
                            {
                                "date": obs.effective_datetime.isoformat(),
                                "value": round(value_lbs, 1),
                                "units": "lbs",
                            }
                        )
                    except (ValueError, TypeError):
                        continue

                elif obs.name == "body_temperature":
                    try:
                        value = float(obs.value)
                        vitals_data["body_temperature"].append(
                            {
                                "date": obs.effective_datetime.isoformat(),
                                "value": value,
                                "units": obs.units or "°F",
                            }
                        )
                    except (ValueError, TypeError):
                        continue

                elif obs.name == "oxygen_saturation":
                    try:
                        value = float(obs.value)
                        vitals_data["oxygen_saturation"].append(
                            {
                                "date": obs.effective_datetime.isoformat(),
                                "value": value,
                                "units": obs.units or "%",
                            }
                        )
                    except (ValueError, TypeError):
                        continue

            return vitals_data

        except Exception as e:
            log.error(f"Error collecting vitals data: {str(e)}")
            return {"weight": [], "body_temperature": [], "oxygen_saturation": []}

    def _generate_visualization_html(self, vitals_data: dict[str, list[dict[str, Any]]]) -> str:
        """Generate the HTML for the vitals visualization using template."""
        context = {"vitals_data": json.dumps(vitals_data)}
        return render_to_string("templates/vitals_visualization.html", context)
