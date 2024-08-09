from canvas_sdk.data import DataModel


class Team(DataModel):
    class Meta(DataModel.Meta):
        create_required_fields = ("name",)

    id: str | None = None
    name: str | None = None
