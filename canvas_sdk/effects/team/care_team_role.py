from canvas_sdk.effects._config_crud import ConfigCrudEffect


class CareTeamRole(ConfigCrudEffect):
    """Create, update, or delete a care team role. ``id`` is the role's ``dbid``."""

    class Meta:
        effect_type = "CARE_TEAM_ROLE"

    _entity_label: str = "care team role"
    _create_required: tuple[str, ...] = ("system", "display")

    system: str | None = None
    version: str | None = None
    code: str | None = None
    display: str | None = None
    user_selected: bool | None = None
    active: bool | None = None


__exports__ = ("CareTeamRole",)
