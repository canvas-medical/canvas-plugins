"""
Report Button Component

Creates the PDMP report button with Canvas context.
"""

from typing import Dict, Any, Optional
from logger import log


class ReportButtonComponent:
    """Component for creating the PDMP report button."""
    
    def create_component(self, 
                        parsed_data: Dict[str, Any],
                        use_test_env: bool = False,
                        patient_id: Optional[str] = None,
                        practitioner_id: Optional[str] = None,
                        organization_id: Optional[str] = None) -> Optional[str]:
        """
        Create report button component.
        
        Args:
            parsed_data: Parsed PDMP response data
            use_test_env: Whether this is a test environment
            patient_id: Patient ID for context
            practitioner_id: Practitioner ID for context
            organization_id: Organization ID for context
            
        Returns:
            HTML string for report button, or None if no report URL
        """
        if not parsed_data.get("parsed") or not parsed_data.get("report_url"):
            return None
        
        report_url = parsed_data["report_url"]
        expiration_date = parsed_data.get("report_expiration", "Unknown")
        
        log.info("ReportButtonComponent: Creating report button component")
        log.info(f"ReportButtonComponent: Report URL: {report_url}")
        log.info(f"ReportButtonComponent: Environment: {'test' if use_test_env else 'prod'}")
        
        return self._build_report_button_html(
            report_url, expiration_date, use_test_env,
            patient_id, practitioner_id, organization_id
        )
    
    def _build_report_button_html(self, 
                                 report_url: str,
                                 expiration_date: str,
                                 use_test_env: bool,
                                 patient_id: Optional[str],
                                 practitioner_id: Optional[str],
                                 organization_id: Optional[str]) -> str:
        """Build the complete report button HTML."""
        env = "test" if use_test_env else "prod"
        
        return f"""
        <div style="margin: 10px 0; text-align: center;">
            <button 
                id="reportUrlBtn" 
                onclick="openPDMPReport('{report_url}', '{env}', '{patient_id or ''}', '{practitioner_id or ''}', '{organization_id or ''}')"
                style="
                    background-color: #2196F3; 
                    color: white; 
                    border: none; 
                    padding: 10px 20px; 
                    border-radius: 5px; 
                    cursor: pointer;
                    font-size: 14px;
                    font-weight: bold;
                "
            >
                📊 Full PDMP Report
            </button>
            <div style="font-size: 12px; color: #666; margin-top: 5px;">
                Expires: {expiration_date}
            </div>
        </div>
        
        <script>
            function openPDMPReport(reportUrl, env, patientId, practitionerId, organizationId) {{
                var btn = document.getElementById('reportUrlBtn');
                
                // Extract report ID from the end of the URL
                var reportId = reportUrl.split('/').pop();
                var apiUrl = `/plugin-io/api/pdmp_bamboo_simple/report?report_id=${{reportId}}&env=${{env}}&patient_id=${{patientId}}&practitioner_id=${{practitionerId}}&organization_id=${{organizationId}}`;
                
                btn.disabled = true;
                btn.innerHTML = '⏳ Opening Report...';
                btn.style.backgroundColor = '#f57c00';
                btn.style.cursor = 'not-allowed';
                
                window.open(apiUrl, '_blank');
                
                // Update button state after opening
                setTimeout(function() {{
                    btn.innerHTML = '✅ Report Opened';
                    btn.style.backgroundColor = '#4caf50';
                }}, 1000);
            }}
        </script>
        """
