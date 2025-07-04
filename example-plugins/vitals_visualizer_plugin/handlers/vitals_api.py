import json
from typing import Dict, List, Any

from canvas_sdk.effects.simple_api import JSONResponse, HTMLResponse
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
            # Get real vitals data for the patient
            vitals_data = self._get_vitals_data(patient_id)
            
            # Generate the HTML with embedded data
            html_content = self._generate_visualization_html(vitals_data)
            
            return [HTMLResponse(
                content=html_content
            )]
            
        except Exception as e:
            log.error(f"Error in VitalsVisualizerAPI: {str(e)}")
            return [JSONResponse({"error": str(e)}, status_code=500)]
    
    def _get_vitals_data(self, patient_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Get vitals data for the patient using Canvas vitals structure."""
        
        try:
            log.info(f"Starting vitals data collection for patient {patient_id}")
            
            # First, get all Vital Signs Panel observations for the patient
            # These are the parent observations that contain individual vitals
            vital_panels = Observation.objects.for_patient(patient_id).filter(
                category="vital-signs",
                name="Vital Signs Panel",
                deleted=False
            ).exclude(entered_in_error__isnull=False).order_by('effective_datetime')
            
            log.info(f"Found {vital_panels.count()} vital sign panels")
            
            # Log some example panels to understand structure
            for i, panel in enumerate(vital_panels[:3]):  # Log first 3 panels
                try:
                    panel_dict = panel.__dict__ if hasattr(panel, '__dict__') else str(panel)
                    log.info(f"Panel {i+1} structure: {panel_dict}")
                except Exception as e:
                    log.info(f"Panel {i+1} structure: Could not log panel structure - {e}")
                
                # Check for related observations/components
                if hasattr(panel, 'observationcomponent_set'):
                    components = panel.observationcomponent_set.all()
                    log.info(f"Panel {i+1} has {components.count()} components")
                    for j, comp in enumerate(components[:5]):  # Log first 5 components
                        try:
                            comp_dict = comp.__dict__ if hasattr(comp, '__dict__') else str(comp)
                            log.info(f"Panel {i+1} Component {j+1}: {comp_dict}")
                        except Exception as e:
                            log.info(f"Panel {i+1} Component {j+1}: Could not log component structure - {e}")
                        
                        if hasattr(comp, 'value_quantity') and comp.value_quantity:
                            log.info(f"Panel {i+1} Component {j+1} value_quantity: {comp.value_quantity}")
                        if hasattr(comp, 'value_quantity_unit') and comp.value_quantity_unit:
                            log.info(f"Panel {i+1} Component {j+1} value_quantity_unit: {comp.value_quantity_unit}")
            
            # Get individual vital observations that are members of these panels
            vital_observations = Observation.objects.for_patient(patient_id).filter(
                category="vital-signs",
                effective_datetime__isnull=False,
                deleted=False
            ).exclude(
                name="Vital Signs Panel"
            ).exclude(
                entered_in_error__isnull=False
            ).select_related("is_member_of").order_by('effective_datetime')
            
            log.info(f"Found {vital_observations.count()} individual vital observations")
            
            # Log some example observations to understand structure
            for i, obs in enumerate(vital_observations[:5]):  # Log first 5 observations
                try:
                    obs_dict = obs.__dict__ if hasattr(obs, '__dict__') else str(obs)
                    log.info(f"Observation {i+1} structure: {obs_dict}")
                except Exception as e:
                    log.info(f"Observation {i+1} structure: Could not log observation structure - {e}")
                
                # Check for related components
                if hasattr(obs, 'observationcomponent_set'):
                    components = obs.observationcomponent_set.all()
                    log.info(f"Observation {i+1} has {components.count()} components")
                    for j, comp in enumerate(components[:3]):  # Log first 3 components
                        try:
                            comp_dict = comp.__dict__ if hasattr(comp, '__dict__') else str(comp)
                            log.info(f"Observation {i+1} Component {j+1}: {comp_dict}")
                        except Exception as e:
                            log.info(f"Observation {i+1} Component {j+1}: Could not log component structure - {e}")
                        
                        if hasattr(comp, 'value_quantity') and comp.value_quantity:
                            log.info(f"Observation {i+1} Component {j+1} value_quantity: {comp.value_quantity}")
                        if hasattr(comp, 'value_quantity_unit') and comp.value_quantity_unit:
                            log.info(f"Observation {i+1} Component {j+1} value_quantity_unit: {comp.value_quantity_unit}")
            
            # Initialize vitals data structure
            vitals_data = {
                'weight': [],
                'body_temperature': [],
                'oxygen_saturation': []
            }
            
            # Value ranges for validation (similar to Canvas VitalsCommand)
            value_ranges = {
                'weight': (1, 1500),  # in lbs
                'body_temperature': (85, 107),  # in °F
                'oxygen_saturation': (60, 100)  # in %
            }
            
            # Process each vital observation
            for obs in vital_observations:
                log.info(f"Processing observation: name='{obs.name}', value='{obs.value}', units='{obs.units}'")
                
                if not obs.value or obs.name in ["note", "pulse_rhythm"]:
                    log.info(f"Skipping observation due to no value or excluded name: {obs.name}")
                    continue
                
                # Handle weight - convert from oz to lbs
                if obs.name == "weight":
                    try:
                        # Weight is stored in oz, convert to lbs
                        value_oz = float(obs.value)
                        value_lbs = value_oz / 16
                        
                        # Validate range
                        min_val, max_val = value_ranges['weight']
                        if min_val <= value_lbs <= max_val:
                            vitals_data['weight'].append({
                                'date': obs.effective_datetime.isoformat(),
                                'value': round(value_lbs, 1),
                                'units': 'lbs'
                            })
                            log.info(f"Added weight: {value_oz} oz → {round(value_lbs, 1)} lbs")
                        else:
                            log.info(f"Skipped weight out of range: {round(value_lbs, 1)} lbs")
                    except (ValueError, TypeError):
                        log.error(f"Failed to parse weight value: {obs.value}")
                        continue
                
                # Handle body temperature
                elif obs.name == "body_temperature":
                    try:
                        value = float(obs.value)
                        
                        # Validate range
                        min_val, max_val = value_ranges['body_temperature']
                        if min_val <= value <= max_val:
                            vitals_data['body_temperature'].append({
                                'date': obs.effective_datetime.isoformat(),
                                'value': value,
                                'units': obs.units or '°F'
                            })
                            log.info(f"Added body temperature: {value} {obs.units or '°F'}")
                        else:
                            log.info(f"Skipped temperature out of range: {value}")
                    except (ValueError, TypeError):
                        log.error(f"Failed to parse temperature value: {obs.value}")
                        continue
                
                # Handle oxygen saturation
                elif obs.name == "oxygen_saturation":
                    try:
                        value = float(obs.value)
                        
                        # Validate range
                        min_val, max_val = value_ranges['oxygen_saturation']
                        if min_val <= value <= max_val:
                            vitals_data['oxygen_saturation'].append({
                                'date': obs.effective_datetime.isoformat(),
                                'value': value,
                                'units': obs.units or '%'
                            })
                            log.info(f"Added oxygen saturation: {value} {obs.units or '%'}")
                        else:
                            log.info(f"Skipped oxygen saturation out of range: {value}")
                    except (ValueError, TypeError):
                        log.error(f"Failed to parse oxygen saturation value: {obs.value}")
                        continue
                
                # Log other vital types found (for debugging)
                else:
                    log.info(f"Found other vital type: {obs.name} = {obs.value}")
            
            log.info(f"Final vitals data collected: {len(vitals_data['weight'])} weight, {len(vitals_data['body_temperature'])} temperature, {len(vitals_data['oxygen_saturation'])} oxygen saturation measurements")
            
            return vitals_data
            
        except Exception as e:
            log.error(f"Error in _get_vitals_data: {str(e)}")
            # Return empty data if there's an error
            return {
                'weight': [],
                'body_temperature': [],
                'oxygen_saturation': []
            }
    
    def _generate_visualization_html(self, vitals_data: Dict[str, List[Dict[str, Any]]]) -> str:
        """Generate the HTML for the vitals visualization using template."""
        
        context = {
            "vitals_data": json.dumps(vitals_data)
        }
        
        return render_to_string("templates/vitals_visualization.html", context)