"""
Assessment Status Component

Displays the status of structured assessment creation.
"""

from typing import Dict, Any, Optional
from logger import log


class AssessmentStatusComponent:
    """Component for displaying assessment status."""

    def create_component(self, result: Dict[str, Any]) -> Optional[str]:
        """
        Create assessment status component.

        Args:
            result: PDMP request result data

        Returns:
            HTML string for assessment status, or None if not applicable
        """
        if not result.get("assessment_created") and not result.get("assessment_error"):
            return None

        log.info("AssessmentStatusComponent: Creating assessment status component")

        if result.get("assessment_created"):
            return self._create_success_status()
        elif result.get("assessment_error"):
            return self._create_error_status(result["assessment_error"])

        return None

    def _create_success_status(self) -> str:
        """Create success status HTML."""
        return """
        <div style="background-color: #e3f2fd; padding: 15px; border-radius: 4px; margin: 15px 0; border: 1px solid #bbdefb;">
            <h4 style="color: #1976d2; margin-top: 0;"> Documentation Created</h4>
            <p style="margin: 5px 0; color: #666;">✅ Structured assessment added to note documenting PDMP check was performed</p>
        </div>
        """

    def _create_error_status(self, error_message: str) -> str:
        """Create error status HTML."""
        return f"""
        <div style="background-color: #fff3cd; padding: 15px; border-radius: 4px; margin: 15px 0; border: 1px solid #ffeaa7;">
            <h4 style="color: #f57c00; margin-top: 0;">⚠️ Documentation Warning</h4>
            <p style="margin: 5px 0; color: #8b4513;">Could not create structured assessment: {error_message}</p>
        </div>
        """