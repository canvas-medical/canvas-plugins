"""Create the plugin's Custom Data tables in the test database.

The pytest-canvas release these tests install predates its own fixture for this, so
the fixture below does the same until a release ships it
(``test_pytest_canvas_still_lacks_the_custom_data_fixture`` fails once one does).
"""

from collections.abc import Iterator

import agent_runner_poc.models.conversation  # noqa: F401 - registers the plugin's models
import agent_runner_poc.models.run_log  # noqa: F401
import pytest
from django.apps import apps
from pytest_django.plugin import DjangoDbBlocker

from plugin_runner.ddl import (
    execute_create_table_sql,
    generate_create_table_sql,
    should_create_table,
)
from plugin_runner.installation import register_plugin_app_config

PLUGIN = "agent_runner_poc"


@pytest.fixture(scope="session", autouse=True)
def custom_data_tables(django_db_setup: None, django_db_blocker: DjangoDbBlocker) -> Iterator[None]:
    """Create a table for each of the plugin's CustomModels."""
    with django_db_blocker.unblock():
        for model_class in apps.all_models.get(PLUGIN, {}).values():
            if should_create_table(model_class, PLUGIN):
                execute_create_table_sql(generate_create_table_sql(PLUGIN, model_class))
        register_plugin_app_config(PLUGIN)
    yield
