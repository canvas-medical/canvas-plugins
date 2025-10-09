"""
Base Modal Component.

Provides base functionality for all modal components.
"""

from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from logger import log


class BaseModal:
    """Base class for all modal components."""

    def __init__(self):
        pass

    def create_modal(
        self, title: str, content: str, target_type: str = "RIGHT_CHART_PANE_LARGE"
    ) -> Effect:
        """
        Create a modal effect with the given title and content.

        Args:
            title: Modal title
            content: Modal content HTML
            target_type: Target type for the modal

        Returns:
            LaunchModalEffect
        """
        log.info(f"BaseModal: Creating modal with title: {title}")

        target_enum = getattr(
            LaunchModalEffect.TargetType,
            target_type,
            LaunchModalEffect.TargetType.RIGHT_CHART_PANE_LARGE,
        )

        # Wrap content with CSS variables using template
        from canvas_sdk.templates import render_to_string

        full_content = render_to_string("templates/modals/base_modal_wrapper.html", {
            "css_variables": self._get_css_variables(),
            "content": content
        })
        return LaunchModalEffect(content=full_content, target=target_enum, title=title).apply()

    def _get_css_variables(self) -> str:
        """Get CSS variables for consistent styling from template."""
        from canvas_sdk.templates import render_to_string
        return render_to_string("templates/base_styles.html", {})

    def create_section(self, content: str, style_type: str = "neutral") -> str:
        """Create a styled section using template."""
        from canvas_sdk.templates import render_to_string
        return render_to_string("templates/components/modal_section.html", {
            "content": content,
            "style_type": style_type,
        })

    def create_title(self, text: str, level: int = 3, color: str = "var(--text)") -> str:
        """Create a styled title using template."""
        from canvas_sdk.templates import render_to_string
        return render_to_string("templates/components/modal_title.html", {
            "text": text,
            "level": level,
            "color": color,
        })

    def create_info_box(self, title: str, items: list[str], icon: str = "ℹ️") -> str:
        """Create an information box using template."""
        from canvas_sdk.templates import render_to_string
        return render_to_string("templates/components/info_box.html", {
            "title": title,
            "items": items,
            "icon": icon,
        })

    def create_error_box(self, title: str, errors: list[str], icon: str = "❌") -> str:
        """Create an error box using template."""
        from canvas_sdk.templates import render_to_string
        return render_to_string("templates/components/error_box.html", {
            "title": title,
            "errors": errors,
            "icon": icon,
        })
