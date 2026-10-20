import pytest

from canvas_sdk.test_utils.factories import CommandTypeSettingFactory
from canvas_sdk.v1.data import CommandTypeSetting


@pytest.mark.django_db
def test_active_schema_keys_leave_out_inactive_command_types() -> None:
    """A plugin can read which command types are turned on by filtering on active."""
    CommandTypeSettingFactory.create(schema_key="followUp", active=True)
    CommandTypeSettingFactory.create(schema_key="refer", active=False)

    active = set(
        CommandTypeSetting.objects.filter(active=True).values_list("schema_key", flat=True)
    )

    assert active == {"followUp"}


def test_reads_the_command_type_settings_view() -> None:
    """The model is backed by the versioned view over home-app's command type settings."""
    assert CommandTypeSetting._meta.db_table == "canvas_sdk_data_api_commandtypesettings_001"
    assert str(CommandTypeSetting(schema_key="refer", active=True)) == "refer"
