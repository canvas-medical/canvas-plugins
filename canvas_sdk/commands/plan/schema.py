from canvas_sdk.commands.base import _BaseCommandSchema

PlanCommandSchema = _BaseCommandSchema | {"narrative": type(str | None)}
