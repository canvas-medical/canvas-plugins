"""
Response Parser Service.

Service for parsing PDMP API responses and extracting clinical data, scores, messages, and report URLs.
"""

import re
from typing import Any

from logger import log


class RiskThresholds:
    """
    PDMP risk score thresholds for NarxCare risk assessment.
    
    These thresholds define risk levels based on NarxCare score values.
    Scores range from 0-999+, with higher scores indicating higher risk.
    """

    # NarxCare score thresholds
    NARX_LOW = 0
    NARX_MODERATE = 200
    NARX_HIGH = 500
    NARX_CRITICAL = 700

    # Risk level names
    RISK_LOW = "Low Risk"
    RISK_MEDIUM = "Medium Risk"
    RISK_HIGH = "High Risk"

    # Risk colors for UI display
    COLOR_LOW = "#2e7d32"  # Green
    COLOR_MEDIUM = "#f57c00"  # Orange
    COLOR_HIGH = "#d32f2f"  # Red


class ResponseParserService:
    """Service for parsing PDMP API responses."""

    def __init__(self):
        """Initialize the response parser service."""
        log.info("ResponseParserService: Initializing response parser service")

    def parse_pdmp_response(self, xml_content: str) -> dict[str, Any]:
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
            licensee_request_id = (
                self._extract_tag_content(xml_content, "LicenseeRequestId") or "N/A"
            )
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
            log.info(
                f"ResponseParserService: Report URL extracted: {'Yes' if report_url else 'No'}"
            )

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

    def _extract_narx_scores_string(self, xml_content: str) -> list[dict[str, Any]]:
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
                    log.warning(
                        f"ResponseParserService: Invalid score value '{score_value_match.group(1)}': {e}"
                    )
                    continue

        return scores

    def _extract_narx_messages_string(self, xml_content: str) -> list[dict[str, Any]]:
        """Extract clinical alert messages from XML response using string parsing."""
        messages = []

        # Find all Message blocks within NarxMessages
        message_blocks = re.findall(r"<Message>(.*?)</Message>", xml_content, re.DOTALL)

        for message_block in message_blocks:
            msg_type_match = re.search(r"<MessageType>(.*?)</MessageType>", message_block)
            msg_text_match = re.search(r"<MessageText>(.*?)</MessageText>", message_block)
            msg_severity_match = re.search(
                r"<MessageSeverity>(.*?)</MessageSeverity>", message_block
            )

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
        """
        Determine risk level based on NarxCare score value.
        
        Uses RiskThresholds constants for consistent threshold values.
        
        Args:
            score_value: NarxCare score value (0-999+)
            
        Returns:
            Risk level description string
        """
        if score_value >= RiskThresholds.NARX_CRITICAL:
            return RiskThresholds.RISK_HIGH
        elif score_value >= RiskThresholds.NARX_HIGH:
            return RiskThresholds.RISK_MEDIUM
        else:
            return RiskThresholds.RISK_LOW

    def _get_risk_color(self, score_value: int) -> str:
        """
        Get color code for risk level visualization.
        
        Uses RiskThresholds constants for consistent colors.
        
        Args:
            score_value: NarxCare score value (0-999+)
            
        Returns:
            Hex color code for UI display
        """
        if score_value >= RiskThresholds.NARX_CRITICAL:
            return RiskThresholds.COLOR_HIGH
        elif score_value >= RiskThresholds.NARX_HIGH:
            return RiskThresholds.COLOR_MEDIUM
        else:
            return RiskThresholds.COLOR_LOW

    def _get_severity_color(self, severity: str) -> str:
        """
        Get color code for message severity.
        
        Args:
            severity: Severity level string (High, Medium, Low)
            
        Returns:
            Hex color code for UI display
        """
        severity_colors = {
            "High": RiskThresholds.COLOR_HIGH,
            "Medium": RiskThresholds.COLOR_MEDIUM,
            "Low": RiskThresholds.COLOR_LOW,
        }
        return severity_colors.get(severity, "#666666")  # Default gray
