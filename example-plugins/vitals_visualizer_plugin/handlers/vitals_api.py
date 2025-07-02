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
        
        if not patient_id and not demo_mode:
            return [JSONResponse({"error": "Patient ID is required"}, status_code=400)]
        
        try:
            if demo_mode:
                # Generate demo data for testing
                vitals_data = self._get_demo_vitals_data()
            else:
                # Get real vitals data for the patient
                vitals_data = self._get_vitals_data(patient_id)
            
            # Generate the HTML with embedded data
            html_content = self._generate_visualization_html(vitals_data)
            
            return [HTMLResponse(
                content=html_content
            )]
            
        except Exception as e:
            return [JSONResponse({"error": str(e)}, status_code=500)]
    
    def _get_vitals_data(self, patient_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Get vitals data for the patient."""
        try:
            # Get all observations for the patient
            observations = Observation.objects.filter(
                patient_id=patient_id,
                deleted=False
            ).order_by('effective_datetime')
            
            vitals_data = {
                'weight': [],
                'body_temperature': [],
                'oxygen_saturation': []
            }
            
            # Common vital signs identifiers
            weight_keywords = ['weight', 'body weight', 'weight measured']
            temp_keywords = ['temperature', 'body temperature', 'temp', 'fever']
            o2_keywords = ['oxygen saturation', 'o2 saturation', 'spo2', 'pulse oximetry', 'oxygen sat']
            
            for obs in observations:
                if not obs.name or not obs.value:
                    continue
                    
                obs_name_lower = obs.name.lower()
                
                # Check for weight
                if any(keyword in obs_name_lower for keyword in weight_keywords):
                    try:
                        value = float(obs.value)
                        vitals_data['weight'].append({
                            'date': obs.effective_datetime.isoformat(),
                            'value': value,
                            'units': obs.units or 'lbs'
                        })
                    except (ValueError, TypeError):
                        continue
                
                # Check for body temperature
                elif any(keyword in obs_name_lower for keyword in temp_keywords):
                    try:
                        value = float(obs.value)
                        vitals_data['body_temperature'].append({
                            'date': obs.effective_datetime.isoformat(),
                            'value': value,
                            'units': obs.units or '°F'
                        })
                    except (ValueError, TypeError):
                        continue
                
                # Check for oxygen saturation
                elif any(keyword in obs_name_lower for keyword in o2_keywords):
                    try:
                        value = float(obs.value)
                        vitals_data['oxygen_saturation'].append({
                            'date': obs.effective_datetime.isoformat(),
                            'value': value,
                            'units': obs.units or '%'
                        })
                    except (ValueError, TypeError):
                        continue
            
            return vitals_data
            
        except Exception as e:
            # Return empty data if there's an error
            return {
                'weight': [],
                'body_temperature': [],
                'oxygen_saturation': []
            }
    
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
    
    def _generate_visualization_html(self, vitals_data: Dict[str, List[Dict[str, Any]]]) -> str:
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