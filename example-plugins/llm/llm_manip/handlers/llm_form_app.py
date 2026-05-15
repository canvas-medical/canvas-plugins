from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.handlers.application import Application
from canvas_sdk.templates import render_to_string


class LlmFormApp(Application):
    """Application handler for launching the LLM interaction form interface."""

    PLUGIN_API_BASE_ROUTE = "/plugin-io/api/llm_manip"

    def on_open(self) -> Effect:
        """Render and launch the LLM interaction modal form.

        Returns:
            Effect to launch the modal with the LLM interaction interface.
        """
        content = render_to_string(
            "templates/llm_form.html",
            {
                "animalsCountURL": f"{self.PLUGIN_API_BASE_ROUTE}/animals_count",
                "chatURL": f"{self.PLUGIN_API_BASE_ROUTE}/chat",
                "fileURL": f"{self.PLUGIN_API_BASE_ROUTE}/file",
            },
        )

        return LaunchModalEffect(
            content=content,
            target=LaunchModalEffect.TargetType.RIGHT_CHART_PANE,
        ).apply()
