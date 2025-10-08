"""
Response Parser Service

Service for parsing PDMP API responses and extracting clinical data, scores, messages, and report URLs.
"""

import re
from typing import Dict, Any, List
from logger import log


class ResponseParserService:
    """Service for parsing PDMP API responses."""

    def __init__(self):
        """Initialize the response parser service."""

    def parse_pdmp_response(self, xml_content: str) -> Dict[str, Any]:
        """
        Parse PDMP XML response to extract clinical data using string parsing.

        Args:
            xml_content: Raw XML response content from PMP Gateway

        Returns:
            Dictionary with parsed PDMP data including:
            - parsed: Boolean indicating if parsing was successful
            - request_id: Gateway request ID
            - licensee_request_id: Client-provided request ID
            - report_expiration: When the report expires
            - disclaimer: Legal disclaimer text
            - narx_scores: List of NarxCare risk scores
            - narx_messages: List of clinical alert messages
            - report_url: URL to view full HTML report
            - error: Error message if parsing failed
        """
        try:
            log.info("ResponseParserService: Starting XML response parsing using string methods")

            # Extract basic info using regex
            request_id = self._extract_tag_content(xml_content, "RequestId") or "N/A"
            licensee_request_id = self._extract_tag_content(xml_content, "LicenseeRequestId") or "N/A"
            report_expiration = self._extract_tag_content(xml_content, "ReportExpiration") or "N/A"
            disclaimer = self._extract_tag_content(xml_content, "Disclaimer") or ""

            # Extract NarxScores
            scores = self._extract_narx_scores_string(xml_content)
            log.info(f"ResponseParserService: Extracted {len(scores)} NarxCare scores")

            # Extract NarxMessages
            messages = self._extract_narx_messages_string(xml_content)
            log.info(f"ResponseParserService: Extracted {len(messages)} clinical messages")

            # Extract Report URL
            report_url = self._extract_report_url_string(xml_content)
            log.info(f"ResponseParserService: Report URL extracted: {'Yes' if report_url else 'No'}")

            result = {
                "parsed": True,
                "request_id": request_id,
                "licensee_request_id": licensee_request_id,
                "report_expiration": report_expiration,
                "disclaimer": disclaimer,
                "narx_scores": scores,
                "narx_messages": messages,
                "report_url": report_url,
            }

            log.info("ResponseParserService: XML parsing completed successfully")
            return result

        except Exception as e:
            error_msg = f"Unexpected error during parsing: {str(e)}"
            log.error(f"ResponseParserService: {error_msg}")
            return {"parsed": False, "error": error_msg}

    def _extract_tag_content(self, xml_content: str, tag_name: str) -> str:
        """Extract content from a single XML tag using regex."""
        pattern = f"<{tag_name}[^>]*>(.*?)</{tag_name}>"
        match = re.search(pattern, xml_content, re.DOTALL)
        return match.group(1).strip() if match else None

    def _extract_narx_scores_string(self, xml_content: str) -> List[Dict[str, Any]]:
        """Extract NarxCare risk scores from XML response using string parsing."""
        scores = []

        # Find all Score blocks within NarxScores
        score_blocks = re.findall(r"<Score>(.*?)</Score>", xml_content, re.DOTALL)

        for score_block in score_blocks:
            score_type_match = re.search(r"<ScoreType>(.*?)</ScoreType>", score_block)
            score_value_match = re.search(r"<ScoreValue>(.*?)</ScoreValue>", score_block)

            if score_type_match and score_value_match:
                try:
                    score_value = int(score_value_match.group(1))
                    scores.append(
                        {
                            "type": score_type_match.group(1).strip(),
                            "value": score_value,
                            "risk_level": self._get_risk_level(score_value),
                            "risk_color": self._get_risk_color(score_value),
                        }
                    )
                except (ValueError, TypeError) as e:
                    log.warning(f"ResponseParserService: Invalid score value '{score_value_match.group(1)}': {e}")
                    continue

        return scores

    def _extract_narx_messages_string(self, xml_content: str) -> List[Dict[str, Any]]:
        """Extract clinical alert messages from XML response using string parsing."""
        messages = []

        # Find all Message blocks within NarxMessages
        message_blocks = re.findall(r"<Message>(.*?)</Message>", xml_content, re.DOTALL)

        for message_block in message_blocks:
            msg_type_match = re.search(r"<MessageType>(.*?)</MessageType>", message_block)
            msg_text_match = re.search(r"<MessageText>(.*?)</MessageText>", message_block)
            msg_severity_match = re.search(r"<MessageSeverity>(.*?)</MessageSeverity>", message_block)

            if msg_type_match and msg_text_match and msg_severity_match:
                severity = msg_severity_match.group(1).strip()
                messages.append(
                    {
                        "type": msg_type_match.group(1).strip(),
                        "text": msg_text_match.group(1).strip(),
                        "severity": severity,
                        "severity_color": self._get_severity_color(severity),
                    }
                )

        return messages

    def _extract_report_url_string(self, xml_content: str) -> str:
        """Extract the viewable report URL from XML response using string parsing."""
        # Look for ViewableReport tag content
        match = re.search(r"<ViewableReport[^>]*>(.*?)</ViewableReport>", xml_content)
        return match.group(1).strip() if match else None

    def _get_risk_level(self, score_value: int) -> str:
        """Determine risk level based on NarxCare score value."""
        if score_value >= 700:
            return "High Risk"
        elif score_value >= 400:
            return "Medium Risk"
        else:
            return "Low Risk"

    def _get_risk_color(self, score_value: int) -> str:
        """Get color code for risk level visualization."""
        if score_value >= 700:
            return "#d32f2f"  # Red for high risk
        elif score_value >= 400:
            return "#f57c00"  # Orange for medium risk
        else:
            return "#2e7d32"  # Green for low risk

    def _get_severity_color(self, severity: str) -> str:
        """Get color code for message severity."""
        severity_colors = {
            "High": "#d32f2f",  # Red
            "Medium": "#f57c00",  # Orange
            "Low": "#2e7d32",  # Green
        }
        return severity_colors.get(severity, "#666666")  # Default gray

    def generate_scores_html(self, scores: List[Dict[str, Any]]) -> str:
        """Generate HTML for displaying NarxCare scores."""
        if not scores:
            return '<p style="color: #666;">No risk scores available</p>'

        scores_html = ""
        for score in scores:
            scores_html += f"""
                <div style="background-color: #f8f9fa; border-left: 4px solid {score["risk_color"]}; padding: 10px; margin: 5px 0; border-radius: 4px;">
                    <strong>{score["type"]} Score:</strong> 
                    <span style="color: {score["risk_color"]}; font-weight: bold;">{score["value"]}</span>
                    <span style="color: #666; font-size: 0.9em;">({score["risk_level"]})</span>
                </div>
            """

        return scores_html

    def generate_messages_html(self, messages: List[Dict[str, Any]]) -> str:
        """Generate HTML for displaying clinical alert messages."""
        if not messages:
            return '<p style="color: #666;">No clinical alerts</p>'

        messages_html = ""
        for msg in messages:
            messages_html += f"""
                <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 8px; margin: 3px 0; border-radius: 4px;">
                    <span style="color: {msg["severity_color"]}; font-weight: bold;">{msg["severity"]} Alert:</span> {msg["text"]}
                </div>
            """

        return messages_html

    def generate_report_button_html(self, report_url: str, expiration_date: str, env: str = "prod",
                                    patient_id: str = None, practitioner_id: str = None,
                                    organization_id: str = None) -> str:
        """
        Generate HTML for the PDMP report button with Canvas context IDs.
        """
        log.info("ResponseParserService: Generating report button HTML")
        log.info(f"ResponseParserService: Report URL: {report_url}")
        log.info(f"ResponseParserService: Environment: {env}")
        log.info(f"ResponseParserService: Canvas Context IDs:")
        log.info(f"  - Patient ID: {patient_id}")
        log.info(f"  - Practitioner ID: {practitioner_id}")
        log.info(f"  - Organization ID: {organization_id}")

        if not report_url:
            log.warning("ResponseParserService: No report URL provided, skipping button generation")
            return ""

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
                var apiUrl = `/plugin-io/api/pdmp_bamboo/report?report_id=${{reportId}}&env=${{env}}&patient_id=${{patientId}}&practitioner_id=${{practitionerId}}&organization_id=${{organizationId}}`;

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