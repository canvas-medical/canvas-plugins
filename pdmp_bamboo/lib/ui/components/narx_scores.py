from typing import Any

from canvas_sdk.templates import render_to_string
from logger import log


class NarxScoresComponent:
    """Component for displaying NarxCare risk scores."""

    def create_component(self, parsed_data: dict[str, Any]) -> str | None:
        """
        Create NarxCare scores component.

        Args:
            parsed_data: Parsed PDMP response data

        Returns:
            HTML string for scores display, or None if no scores
        """
        if not parsed_data.get("parsed") or not parsed_data.get("narx_scores"):
            return None

        scores = parsed_data["narx_scores"]
        return self._build_scores_html(scores)

    def _build_scores_html(self, scores: list[dict[str, Any]]) -> str:
        """Build scores HTML using template."""
        valid_scores = [
            score
            for score in scores
            if score.get("value") is not None and score.get("value") != "N/A"
        ]

        if not valid_scores:
            return None

        # Prepare score data for template
        display_names = {
            "narcotics": "Narcotics",
            "stimulants": "Stimulants",
            "sedatives": "Sedatives",
            "overdose": "Overdose",
            "misuse": "Misuse",
        }

        template_scores = []
        for score in valid_scores:
            score_type = score.get("type", "Unknown")
            score_value = score.get("value", "N/A")
            display_name = display_names.get(score_type.lower(), score_type)

            try:
                numeric_value = int(score_value) if score_value != "N/A" else 0
            except (ValueError, TypeError):
                numeric_value = 0

            clamped_value = max(0, min(999, numeric_value))
            percentage = (clamped_value / 999) * 100

            template_scores.append({
                "type": score_type.lower(),
                "value": score_value,
                "display_name": display_name,
                "numeric_value": numeric_value,
                "percentage": percentage,
            })

        try:
            return render_to_string("templates/components/narx_scores.html", {
                "scores": template_scores
            })
        except Exception as e:
            log.error(f"NarxScoresComponent: Error rendering template: {e}")
            return None
