import arrow

from http import HTTPStatus

from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.effects.simple_api import Response, JSONResponse, HTMLResponse
from canvas_sdk.effects.task import AddTask, TaskStatus

from canvas_sdk.handlers.application import Application
from canvas_sdk.handlers.simple_api import StaffSessionAuthMixin, SimpleAPI, api

from canvas_sdk.templates import render_to_string

from canvas_sdk.v1.data.staff import Staff


class MyGlobalApplication(Application):
    def on_open(self) -> Effect:
        return LaunchModalEffect(
            url="/plugin-io/api/plugins_smoke_test/global",
            target=LaunchModalEffect.TargetType.DEFAULT_MODAL,
        ).apply()


class SmokeTestApi(StaffSessionAuthMixin, SimpleAPI):
    @api.get("/global")
    def smoke_test_ui(self) -> list[Response | Effect]:
        logged_in_staff = Staff.objects.get(id=self.request.headers["canvas-logged-in-user-id"])

        context = {
            "logged_in_staff": logged_in_staff,
        }
        return [
            HTMLResponse(
                render_to_string("templates/global-smoke-test.html", context),
                status_code=HTTPStatus.OK,
            )
        ]

    @api.post("/add-task")
    def add_task(self) -> list[Response | Effect]:
        add_task = AddTask(
            title="This came from the smoke test.",
            due=arrow.utcnow().shift(days=5).datetime,
            status=TaskStatus.OPEN,
        )
        return [
            add_task.apply(),
            JSONResponse(
                {"message": "Task will be created"},
                status_code=HTTPStatus.ACCEPTED
            )
        ]
