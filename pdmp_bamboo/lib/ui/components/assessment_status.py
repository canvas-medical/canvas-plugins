"""
Assessment Status Component.

Displays the status of structured assessment creation.
"""

from typing import Any

from logger import log
from pdmp_bamboo.lib.ui.components.base_component import BaseComponent


class AssessmentStatusComponent(BaseComponent):
    """Component for displaying assessment status."""

    def create_component(self, result: dict[str, Any]) -> str | None:
        """
        Create assessment status component.

        Args:
            result: PDMP request result data

        Returns:
            HTML string for assessment status, or None if not applicable
        """
        log.info(f"AssessmentStatusComponent: Result: {result}")

        if not result.get("assessment_created") and not result.get("assessment_error"):
            return None

        log.info("AssessmentStatusComponent: Creating assessment status component")

        return self._render_template(
            "templates/components/assessment_status.html",
            {
                "assessment_created": result.get("assessment_created"),
                "assessment_error": result.get("assessment_error"),
            },
        )
