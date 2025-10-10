"""
Base Component.

Base class for all UI components with safe template rendering.
"""

from abc import ABC
from typing import Any

from canvas_sdk.templates import render_to_string
from logger import log


class BaseComponent(ABC):
    """Base component with safe template rendering."""

    def _render_template(
        self, template_path: str, context: dict[str, Any], component_name: str | None = None
    ) -> str | None:
        """
        Safely render template with error handling.

        Args:
            template_path: Path to template file
            context: Template context dictionary
            component_name: Name of component for error logging (defaults to class name)

        Returns:
            Rendered HTML string or None if rendering fails
        """
        component_name = component_name or self.__class__.__name__
        try:
            return render_to_string(template_path, context)
        except Exception as e:
            log.error(f"{component_name}: Error rendering template {template_path}: {e}")
            return None

