from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.handlers.application import Application


class MyApplication(Application):
    """Launches the clipboard regression test iframe."""

    def on_open(self) -> Effect:
        return LaunchModalEffect(
            url="/plugin-io/api/clipboard_regression_test/app/clipboard-demo",
            target=LaunchModalEffect.TargetType.PAGE,
        ).apply()
