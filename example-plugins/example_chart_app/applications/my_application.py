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


class MyChartApplication(Application):
    def on_open(self) -> Effect:
        patient_id = self.context['patient']['id']
        return LaunchModalEffect(
            url=f"/plugin-io/api/example_chart_app/custom-ui?patient={patient_id}",
            target=LaunchModalEffect.TargetType.RIGHT_CHART_PANE,
        ).apply()


class MyApi(StaffSessionAuthMixin, SimpleAPI):
    @api.get("/custom-ui")
    def ical_links(self) -> list[Response | Effect]:
        logged_in_staff = Staff.objects.get(id=self.request.headers["canvas-logged-in-user-id"])

        context = {
            "logged_in_staff": logged_in_staff,
            "patient_id": self.request.query_params["patient"],
        }
        return [
            HTMLResponse(
                render_to_string("templates/custom-ui.html", context),
                status_code=HTTPStatus.OK,
            )
        ]

    @api.post("/add-task")
    def add_task(self) -> list[Response | Effect]:
        add_task = AddTask(
            title="This came from the custom patient ui.",
            patient_id=self.request.json()["patient_id"],
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
