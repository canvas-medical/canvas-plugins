import json
from typing import Dict, List, Any

from canvas_sdk.effects.simple_api import JSONResponse, HTMLResponse
from canvas_sdk.handlers.simple_api import SimpleAPIRoute, StaffSessionAuthMixin
from canvas_sdk.v1.data import Observation


class VitalsVisualizerAPI(StaffSessionAuthMixin, SimpleAPIRoute):
    """API endpoint that serves vitals visualization data and UI."""
    
    PATH = "/visualize"
    
    def get(self) -> list[HTMLResponse | JSONResponse]:
        """Return the vitals visualization UI and data."""
        patient_id = self.request.query_params.get("patient_id")
        demo_mode = self.request.query_params.get("demo") == "true"
        debug_mode = self.request.query_params.get("debug") == "true"
        
        if not patient_id and not demo_mode:
            return [JSONResponse({"error": "Patient ID is required"}, status_code=400)]
        
        try:
            if demo_mode:
                # Generate demo data for testing
                vitals_data = self._get_demo_vitals_data()
                debug_info = None
            else:
                # Get real vitals data for the patient
                vitals_data, debug_info = self._get_vitals_data(patient_id, debug_mode)
            
            # Generate the HTML with embedded data
            html_content = self._generate_visualization_html(vitals_data, debug_info)
            
            return [HTMLResponse(
                content=html_content
            )]
            
        except Exception as e:
            return [JSONResponse({"error": str(e)}, status_code=500)]
    
    def _get_vitals_data(self, patient_id: str, debug_mode: bool = False) -> tuple[Dict[str, List[Dict[str, Any]]], Dict[str, Any] | None]:
        """Get vitals data for the patient using Canvas vitals structure."""
        debug_info = None
        if debug_mode:
            debug_info = {
                'total_panels': 0,
                'total_vitals': 0,
                'panels_found': [],
                'vitals_found': [],
                'processing_log': []
            }
        
        try:
            # First, get all Vital Signs Panel observations for the patient
            # These are the parent observations that contain individual vitals
            vital_panels = Observation.objects.filter(
                patient_id=patient_id,
                category="vital-signs",
                name="Vital Signs Panel",
                deleted=False
            ).exclude(entered_in_error__isnull=False).order_by('effective_datetime')
            
            if debug_mode:
                debug_info['total_panels'] = vital_panels.count()
                debug_info['processing_log'].append(f"Found {vital_panels.count()} vital sign panels")
            
            # Get individual vital observations that are members of these panels
            vital_observations = Observation.objects.filter(
                patient_id=patient_id,
                category="vital-signs",
                effective_datetime__isnull=False,
                deleted=False
            ).exclude(
                name="Vital Signs Panel"
            ).exclude(
                entered_in_error__isnull=False
            ).select_related("is_member_of").order_by('effective_datetime')
            
            if debug_mode:
                debug_info['total_vitals'] = vital_observations.count()
                debug_info['processing_log'].append(f"Found {vital_observations.count()} individual vital observations")
            
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
                if not obs.value or obs.name in ["note", "pulse_rhythm"]:
                    continue
                
                if debug_mode:
                    obs_info = {
                        'name': obs.name,
                        'value': obs.value,
                        'units': obs.units,
                        'effective_datetime': obs.effective_datetime.isoformat() if obs.effective_datetime else None,
                        'is_member_of': str(obs.is_member_of.id) if obs.is_member_of else None
                    }
                    debug_info['vitals_found'].append(obs_info)
                
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
                            if debug_mode:
                                debug_info['processing_log'].append(f"Added weight: {value_oz} oz → {round(value_lbs, 1)} lbs")
                        else:
                            if debug_mode:
                                debug_info['processing_log'].append(f"Skipped weight out of range: {round(value_lbs, 1)} lbs")
                    except (ValueError, TypeError):
                        if debug_mode:
                            debug_info['processing_log'].append(f"Failed to parse weight value: {obs.value}")
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
                            if debug_mode:
                                debug_info['processing_log'].append(f"Added body temperature: {value} {obs.units or '°F'}")
                        else:
                            if debug_mode:
                                debug_info['processing_log'].append(f"Skipped temperature out of range: {value}")
                    except (ValueError, TypeError):
                        if debug_mode:
                            debug_info['processing_log'].append(f"Failed to parse temperature value: {obs.value}")
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
                            if debug_mode:
                                debug_info['processing_log'].append(f"Added oxygen saturation: {value} {obs.units or '%'}")
                        else:
                            if debug_mode:
                                debug_info['processing_log'].append(f"Skipped oxygen saturation out of range: {value}")
                    except (ValueError, TypeError):
                        if debug_mode:
                            debug_info['processing_log'].append(f"Failed to parse oxygen saturation value: {obs.value}")
                        continue
                
                # Log other vital types found (for debugging)
                else:
                    if debug_mode:
                        debug_info['processing_log'].append(f"Found other vital type: {obs.name} = {obs.value}")
            
            # Store panel information for debug
            if debug_mode:
                for panel in vital_panels:
                    panel_info = {
                        'id': str(panel.id),
                        'effective_datetime': panel.effective_datetime.isoformat() if panel.effective_datetime else None,
                        'value': panel.value
                    }
                    debug_info['panels_found'].append(panel_info)
            
            return vitals_data, debug_info
            
        except Exception as e:
            # Return empty data if there's an error
            if debug_mode:
                debug_info['error'] = str(e)
                debug_info['processing_log'].append(f"Error occurred: {str(e)}")
            return {
                'weight': [],
                'body_temperature': [],
                'oxygen_saturation': []
            }, debug_info
    
    def _get_demo_vitals_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Generate demo vitals data for testing."""
        from datetime import datetime, timedelta
        import random
        
        base_date = datetime.now() - timedelta(days=365)
        demo_data = {
            'weight': [],
            'body_temperature': [],
            'oxygen_saturation': []
        }
        
        # Generate demo weight data (150-180 lbs range)
        for i in range(12):
            date = base_date + timedelta(days=i*30)
            weight = 160 + random.uniform(-10, 10)
            demo_data['weight'].append({
                'date': date.isoformat(),
                'value': round(weight, 1),
                'units': 'lbs'
            })
        
        # Generate demo temperature data (97-100°F range)
        for i in range(8):
            date = base_date + timedelta(days=i*45)
            temp = 98.6 + random.uniform(-1.5, 1.5)
            demo_data['body_temperature'].append({
                'date': date.isoformat(),
                'value': round(temp, 1),
                'units': '°F'
            })
        
        # Generate demo oxygen saturation data (95-100% range)
        for i in range(10):
            date = base_date + timedelta(days=i*36)
            o2 = 97 + random.uniform(0, 3)
            demo_data['oxygen_saturation'].append({
                'date': date.isoformat(),
                'value': round(o2),
                'units': '%'
            })
        
        return demo_data
    
    def _generate_visualization_html(self, vitals_data: Dict[str, List[Dict[str, Any]]], debug_info: Dict[str, Any] = None) -> str:
        """Generate the HTML for the vitals visualization."""
        
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vitals Visualization</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 20px;
            background-color: #f8f9fa;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .selector {{
            margin-bottom: 20px;
        }}
        .selector label {{
            font-weight: 600;
            margin-right: 10px;
        }}
        .selector select {{
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }}
        .chart-container {{
            position: relative;
            height: 400px;
            margin-bottom: 30px;
        }}
        .table-container {{
            overflow-x: auto;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f1f3f4;
            font-weight: 600;
        }}
        .no-data {{
            text-align: center;
            padding: 40px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>Patient Vital Signs Visualization</h2>
        </div>
        
        <div class="selector">
            <label for="vitalSelect">Select Vital Sign:</label>
            <select id="vitalSelect" onchange="updateVisualization()">
                <option value="weight">Weight</option>
                <option value="body_temperature">Body Temperature</option>
                <option value="oxygen_saturation">Oxygen Saturation</option>
            </select>
        </div>
        
        <div class="chart-container">
            <canvas id="vitalsChart"></canvas>
        </div>
        
        <div class="table-container">
            <table id="vitalsTable">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Value</th>
                        <th>Units</th>
                    </tr>
                </thead>
                <tbody id="vitalsTableBody">
                </tbody>
            </table>
        </div>
        {f'''
        <div class="debug-container" style="margin-top: 30px; background: #f0f0f0; padding: 15px; border-radius: 4px;">
            <h3>Debug Information</h3>
            <p><strong>Total vital sign panels found:</strong> {debug_info.get('total_panels', 0)}</p>
            <p><strong>Total individual vitals found:</strong> {debug_info.get('total_vitals', 0)}</p>
            <p><strong>Processing log:</strong></p>
            <ul>
                {''.join([f'<li>{log_entry}</li>' for log_entry in debug_info.get('processing_log', [])])}
            </ul>
            <details>
                <summary>Vital sign panels (click to expand)</summary>
                <pre style="max-height: 200px; overflow-y: auto; font-size: 12px;">
{json.dumps(debug_info.get('panels_found', []), indent=2) if debug_info and debug_info.get('panels_found') else 'No panels found'}
                </pre>
            </details>
            <details>
                <summary>Individual vitals (click to expand)</summary>
                <pre style="max-height: 300px; overflow-y: auto; font-size: 12px;">
{json.dumps(debug_info.get('vitals_found', []), indent=2) if debug_info and debug_info.get('vitals_found') else 'No individual vitals found'}
                </pre>
            </details>
        </div>
        ''' if debug_info else ''}
    </div>

    <script>
        const vitalsData = {json.dumps(vitals_data)};
        let chart = null;
        
        function updateVisualization() {{
            const selectedVital = document.getElementById('vitalSelect').value;
            const data = vitalsData[selectedVital] || [];
            
            // Update chart
            updateChart(selectedVital, data);
            
            // Update table
            updateTable(data);
        }}
        
        function updateChart(vitalType, data) {{
            const chartContainer = document.querySelector('.chart-container');
            
            if (chart) {{
                chart.destroy();
            }}
            
            if (data.length === 0) {{
                chartContainer.innerHTML = 
                    '<div class="no-data">No data available for this vital sign</div>';
                return;
            }}
            
            // Restore canvas if it was replaced
            if (!document.getElementById('vitalsChart')) {{
                chartContainer.innerHTML = '<canvas id="vitalsChart"></canvas>';
            }}
            
            const ctx = document.getElementById('vitalsChart').getContext('2d');
            
            const labels = data.map(d => new Date(d.date).toLocaleDateString());
            const values = data.map(d => parseFloat(d.value) || 0);
            const units = data.length > 0 ? data[0].units : '';
            
            const vitalLabels = {{
                'weight': 'Weight',
                'body_temperature': 'Body Temperature', 
                'oxygen_saturation': 'Oxygen Saturation'
            }};
            
            const colors = {{
                'weight': 'rgba(54, 162, 235, 0.8)',
                'body_temperature': 'rgba(255, 99, 132, 0.8)',
                'oxygen_saturation': 'rgba(75, 192, 192, 0.8)'
            }};
            
            chart = new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: labels,
                    datasets: [{{
                        label: vitalLabels[vitalType],
                        data: values,
                        backgroundColor: colors[vitalType],
                        borderColor: colors[vitalType].replace('0.8', '1'),
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    return context.dataset.label + ': ' + context.parsed.y + ' ' + units;
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: false,
                            title: {{
                                display: true,
                                text: vitalLabels[vitalType] + ' (' + units + ')'
                            }}
                        }},
                        x: {{
                            title: {{
                                display: true,
                                text: 'Date'
                            }}
                        }}
                    }}
                }}
            }});
        }}
        
        function updateTable(data) {{
            const tbody = document.getElementById('vitalsTableBody');
            tbody.innerHTML = '';
            
            if (data.length === 0) {{
                tbody.innerHTML = '<tr><td colspan="3" class="no-data">No data available</td></tr>';
                return;
            }}
            
            data.forEach(item => {{
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${{new Date(item.date).toLocaleDateString()}}</td>
                    <td>${{item.value}}</td>
                    <td>${{item.units}}</td>
                `;
                tbody.appendChild(row);
            }});
        }}
        
        // Initialize with weight data or show message if no data
        document.addEventListener('DOMContentLoaded', function() {{
            updateVisualization();
            
            // Show a message if no data is available at all
            const hasData = Object.values(vitalsData).some(arr => arr.length > 0);
            if (!hasData) {{
                document.querySelector('.container').innerHTML += 
                    '<div class="no-data" style="margin-top: 20px; font-size: 16px;">' +
                    'No vital signs data found for this patient. Vital signs will appear here once they are recorded.' +
                    '</div>';
            }}
        }});
    </script>
</body>
</html>
        """