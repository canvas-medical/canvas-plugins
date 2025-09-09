"""
PDMP Response Parser Utilities

This module provides functionality to parse XML responses from BambooHealth PMP Gateway
and extract clinical data, scores, messages, and report URLs using string parsing.
"""

import re
from typing import Dict, Any, List
from logger import log


def parse_pdmp_response(xml_content: str) -> Dict[str, Any]:
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
        log.info("PDMP-Parser: Starting XML response parsing using string methods")

        # Extract basic info using regex
        request_id = _extract_tag_content(xml_content, "RequestId") or "N/A"
        licensee_request_id = _extract_tag_content(xml_content, "LicenseeRequestId") or "N/A"
        report_expiration = _extract_tag_content(xml_content, "ReportExpiration") or "N/A"
        disclaimer = _extract_tag_content(xml_content, "Disclaimer") or ""

        # Extract NarxScores
        scores = _extract_narx_scores_string(xml_content)
        log.info(f"PDMP-Parser: Extracted {len(scores)} NarxCare scores")

        # Extract NarxMessages
        messages = _extract_narx_messages_string(xml_content)
        log.info(f"PDMP-Parser: Extracted {len(messages)} clinical messages")

        # Extract Report URL
        report_url = _extract_report_url_string(xml_content)
        log.info(f"PDMP-Parser: Report URL extracted: {'Yes' if report_url else 'No'}")

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

        log.info("PDMP-Parser: XML parsing completed successfully")
        return result

    except Exception as e:
        error_msg = f"Unexpected error during parsing: {str(e)}"
        log.error(f"PDMP-Parser: {error_msg}")
        return {"parsed": False, "error": error_msg}


def _extract_tag_content(xml_content: str, tag_name: str) -> str:
    """Extract content from a single XML tag using regex."""
    pattern = f"<{tag_name}[^>]*>(.*?)</{tag_name}>"
    match = re.search(pattern, xml_content, re.DOTALL)
    return match.group(1).strip() if match else None


def _extract_narx_scores_string(xml_content: str) -> List[Dict[str, Any]]:
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
                        "risk_level": _get_risk_level(score_value),
                        "risk_color": _get_risk_color(score_value),
                    }
                )
            except (ValueError, TypeError) as e:
                log.warning(f"PDMP-Parser: Invalid score value '{score_value_match.group(1)}': {e}")
                continue

    return scores


def _extract_narx_messages_string(xml_content: str) -> List[Dict[str, Any]]:
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
                    "severity_color": _get_severity_color(severity),
                }
            )

    return messages


def _extract_report_url_string(xml_content: str) -> str:
    """Extract the viewable report URL from XML response using string parsing."""
    # Look for ViewableReport tag content
    match = re.search(r"<ViewableReport[^>]*>(.*?)</ViewableReport>", xml_content)
    return match.group(1).strip() if match else None


def _get_risk_level(score_value: int) -> str:
    """Determine risk level based on NarxCare score value."""
    if score_value >= 700:
        return "High Risk"
    elif score_value >= 400:
        return "Medium Risk"
    else:
        return "Low Risk"


def _get_risk_color(score_value: int) -> str:
    """Get color code for risk level visualization."""
    if score_value >= 700:
        return "#d32f2f"  # Red for high risk
    elif score_value >= 400:
        return "#f57c00"  # Orange for medium risk
    else:
        return "#2e7d32"  # Green for low risk


def _get_severity_color(severity: str) -> str:
    """Get color code for message severity."""
    severity_colors = {
        "High": "#d32f2f",  # Red
        "Medium": "#f57c00",  # Orange
        "Low": "#2e7d32",  # Green
    }
    return severity_colors.get(severity, "#666666")  # Default gray


def generate_scores_html(scores: List[Dict[str, Any]]) -> str:
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


def generate_messages_html(messages: List[Dict[str, Any]]) -> str:
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


def generate_report_button_html(report_url: str, expiration_date: str, env: str = "prod") -> str:
    """Generate HTML for the clickable report button that calls the API endpoint."""
    if not report_url:
        return ""

    return f"""
        <div style="background-color: #e3f2fd; padding: 15px; border-radius: 4px; margin: 15px 0; border: 1px solid #bbdefb;">
            <h4 style="margin-top: 0; color: #1976d2;">📄 Full PDMP Report</h4>
            <p style="margin: 10px 0; color: #666;">Click to view the complete PDMP report in a new window:</p>
            <button 
                id="reportUrlBtn" 
                onclick="openPDMPReport('{report_url}', '{env}')"
                style="background-color: #1976d2; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; font-size: 14px; font-weight: bold;"
                onmouseover="this.style.backgroundColor='#1565c0'"
                onmouseout="this.style.backgroundColor='#1976d2'"
            >
                🔗 Open PDMP Report
            </button>
            <p style="margin: 10px 0 0 0; font-size: 0.85em; color: #666;">
                <em>Note: Report expires on {expiration_date}</em>
            </p>
        </div>
        
        <script>
        function openPDMPReport(reportUrl, env) {{
            var btn = document.getElementById('reportUrlBtn');
            
            // Extract report ID from the end of the URL
            var reportId = reportUrl.split('/').pop();
            var apiUrl = `/plugin-io/api/pdmp_bamboo/report?report_id=${{reportId}}&env=${{env}}`;
            
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
