from canvas_sdk.effects._config_crud import ConfigCrudEffect


class CodingEffect(ConfigCrudEffect):
    """Shared fields for the configurable coding catalogs."""

    _entity_label: str = "coding"
    _create_required: tuple[str, ...] = ("system", "display")

    system: str | None = None
    version: str | None = None
    code: str | None = None
    display: str | None = None
    user_selected: bool | None = None


__exports__ = ()
