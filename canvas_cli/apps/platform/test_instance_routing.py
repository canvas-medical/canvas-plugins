"""Tests for the commands that route through Canvas Platform per target.

`canvas list`, `canvas namespace *` and `canvas logs` route per instance (a managed instance goes
through Platform, any other through credentials.ini). `canvas enable`, `canvas disable` and
`canvas config list` route per plugin. HTTP is mocked with requests-mock, with the bodies the
Platform and home-app contracts document.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any
from unittest.mock import Mock, patch

import pytest
import requests_mock as requests_mock_module
from typer.testing import CliRunner

from canvas_cli.apps.platform import auth
from canvas_cli.apps.platform.commands import managed_instance
from canvas_cli.main import app

runner = CliRunner(mix_stderr=False)
PLATFORM = "https://platform.example"
API = f"{PLATFORM}/api/v1"
NAME = "acme__thing"
HOST = "https://acme.canvasmedical.com"
NS = "acme__data"
NS_URL = f"{API}/instances/acme/namespaces/{NS}"
INSTANCE_TOKEN = "canvas_cli.apps.plugin.plugin.get_or_request_api_token"
NAMESPACE_TOKEN = "canvas_cli.apps.namespace.namespace.get_or_request_api_token"


def _instance(slug: str, *capabilities: str, managed: bool = True) -> dict[str, Any]:
    return {
        "slug": slug,
        "organization": "acme",
        "stage": "staging",
        "production": False,
        "managed": managed,
        "capabilities": list(capabilities),
    }


def _calls(mock: requests_mock_module.Mocker, method: str, url: str) -> list[Any]:
    return [r for r in mock.request_history if r.method == method and r.url.startswith(url)]


@pytest.fixture(autouse=True)
def platform_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Point the CLI at the test platform."""
    monkeypatch.setenv(auth.PLATFORM_URL_ENV, PLATFORM)


@pytest.fixture
def signed_in() -> None:
    """A stored session with the test platform."""
    auth.save_tokens(
        PLATFORM,
        {"access_token": "cnvs_ua_1", "refresh_token": "cnvs_rt_1", "expires_in": 3600},
        make_default=True,
    )


@pytest.fixture
def instances(requests_mock: requests_mock_module.Mocker, signed_in: None) -> None:
    """`acme` is managed and `legacy` is not."""
    requests_mock.get(
        f"{API}/instances",
        json={
            "instances": [
                _instance("acme", "view_instance", "deploy_plugin"),
                _instance("legacy", managed=False),
            ]
        },
    )


@pytest.fixture
def ini_token() -> Iterator[Mock]:
    """The credentials.ini token lookup for the plugin and namespace commands."""
    with (
        patch(INSTANCE_TOKEN, return_value="ini-tok") as plugin_mock,
        patch(NAMESPACE_TOKEN, return_value="ini-tok"),
    ):
        yield plugin_mock


@pytest.fixture
def managed_plugin(requests_mock: requests_mock_module.Mocker, signed_in: None) -> None:
    """A plugin Platform manages, installed on acme only."""
    requests_mock.get(
        f"{API}/plugins/{NAME}",
        json={
            "name": NAME,
            "publisher": "acme",
            "installs": [{"instance": "acme", "sha": "3f2a", "enabled": True}],
        },
    )
    requests_mock.get(f"{API}/instances", json={"instances": [_instance("acme", "deploy_plugin")]})


def _deployment(action: str) -> dict[str, Any]:
    return {
        "id": "6f1c",
        "action": action,
        "status": "succeeded",
        "organization": "acme",
        "targets": [
            {
                "plugin": NAME,
                "instance": "acme",
                "status": "succeeded",
                "error": "",
                "undeclared_values": [],
            }
        ],
        "consent_requests": [],
    }


# -- managed_instance --------------------------------------------------------


def test_managed_instance_is_none_when_signed_out(
    requests_mock: requests_mock_module.Mocker,
) -> None:
    """Without a Platform session there is nothing to ask, so credentials.ini serves."""
    assert managed_instance(HOST) is None
    assert not requests_mock.called


def test_managed_instance_is_none_for_localhost(
    requests_mock: requests_mock_module.Mocker, signed_in: None
) -> None:
    """A host outside canvasmedical.com has no slug, so Platform cannot manage it."""
    assert managed_instance("http://localhost:8000") is None
    assert not requests_mock.called


def test_managed_instance_returns_client_and_slug(instances: None) -> None:
    """A managed instance in the person's list yields the client and its slug."""
    found = managed_instance(HOST)

    assert found is not None
    assert found[1] == "acme"


def test_managed_instance_is_none_for_an_unmanaged_instance(instances: None) -> None:
    """An instance Platform lists as unmanaged is reached with credentials.ini."""
    assert managed_instance("https://legacy.canvasmedical.com") is None


def test_a_failed_instance_lookup_raises_instead_of_reading_as_unmanaged(
    requests_mock: requests_mock_module.Mocker, signed_in: None, ini_token: Mock
) -> None:
    """A Platform 500 on /instances stops the command: reading it as unmanaged would send a
    managed instance's request to credentials.ini.
    """
    requests_mock.get(f"{API}/instances", status_code=500, json={"error": "Platform is down."})

    result = runner.invoke(app, ["list", "--host", "acme"])

    assert result.exit_code != 0
    assert "Platform is down." in result.output + result.stderr
    ini_token.assert_not_called()


# -- list --------------------------------------------------------------------


def test_list_reads_platform_inventory_for_a_managed_instance(
    requests_mock: requests_mock_module.Mocker, instances: None, ini_token: Mock
) -> None:
    """A managed instance's plugins come from Platform, stamped with when they were collected."""
    requests_mock.get(
        f"{API}/instances/acme/plugins",
        json={
            "instance": "acme",
            "collected_at": "2026-10-30T09:00:00Z",
            "plugins": [
                {
                    "name": "canvas_medical__scribe",
                    "version": "1.2.0",
                    "package_checksum": "abc",
                    "enabled": True,
                    "collected_at": "2026-10-30T09:00:00Z",
                }
            ],
        },
    )

    result = runner.invoke(app, ["list", "--host", "acme"])

    assert result.exit_code == 0, result.output
    assert result.stdout.splitlines() == ["canvas_medical__scribe@1.2.0\tenabled"]
    assert "As of 2026-10-30T09:00:00Z (Canvas Platform inventory)" in result.stderr
    ini_token.assert_not_called()


def test_list_reports_an_empty_platform_inventory(
    requests_mock: requests_mock_module.Mocker, instances: None
) -> None:
    """An instance with no plugins says so, as the credentials path does."""
    requests_mock.get(
        f"{API}/instances/acme/plugins",
        json={"instance": "acme", "collected_at": "2026-10-30T09:00:00Z", "plugins": []},
    )

    result = runner.invoke(app, ["list", "--host", "acme"])

    assert result.exit_code == 0, result.output
    assert f"No plugins are currently installed on {HOST}" in result.stdout


def test_list_of_an_inventory_platform_never_read_says_so(
    requests_mock: requests_mock_module.Mocker, instances: None, ini_token: Mock
) -> None:
    """A null collected_at means Platform has not read the instance, so its empty list says
    nothing about what is installed and the command does not claim the instance runs nothing.
    Platform's next read of a new instance can be hours away, so the sentence points at
    credentials.ini rather than promising a wait.
    """
    requests_mock.get(
        f"{API}/instances/acme/plugins",
        json={"instance": "acme", "collected_at": None, "plugins": []},
    )

    result = runner.invoke(app, ["list", "--host", "acme"])

    said = result.output + result.stderr
    assert result.exit_code == 1
    assert "Canvas Platform has not read the plugins on acme yet" in said
    assert "canvas logout" in said
    assert "credentials.ini" in said
    assert "shortly" not in said
    assert "No plugins are currently installed" not in result.stdout
    assert "None" not in said
    ini_token.assert_not_called()


def test_list_shows_platforms_not_found_sentence(
    requests_mock: requests_mock_module.Mocker, instances: None, ini_token: Mock
) -> None:
    """A coded 404 is Platform's refusal, not a Platform without the route."""
    requests_mock.get(
        f"{API}/instances/acme/plugins",
        status_code=404,
        json={"error": "No such instance.", "code": "not_found"},
    )

    result = runner.invoke(app, ["list", "--host", "acme"])

    assert result.exit_code == 1
    assert "No such instance." in result.output + result.stderr
    assert "does not list plugins yet" not in result.output + result.stderr
    ini_token.assert_not_called()


def test_list_of_an_unmanaged_instance_uses_credentials_ini(
    requests_mock: requests_mock_module.Mocker, instances: None, ini_token: Mock
) -> None:
    """An unmanaged instance is listed from the instance, and Platform's plugin route is not used."""
    requests_mock.get(
        "https://legacy.canvasmedical.com/plugin-io/plugins/",
        json={"results": [{"name": "old", "version": "0.1", "is_enabled": False}]},
    )

    result = runner.invoke(app, ["list", "--host", "legacy"])

    assert result.exit_code == 0, result.output
    assert result.stdout.splitlines() == ["old@0.1\tdisabled"]
    assert not _calls(requests_mock, "GET", f"{API}/instances/legacy/plugins")


def test_list_before_platform_serves_the_route_says_how_to_use_credentials_ini(
    requests_mock: requests_mock_module.Mocker, instances: None, ini_token: Mock
) -> None:
    """A bare 404 means this Platform lacks the route; it is not an unmanaged instance, so the
    command explains the way off Platform rather than quietly reading the instance.
    """
    requests_mock.get(f"{API}/instances/acme/plugins", status_code=404, text="Not Found")

    result = runner.invoke(app, ["list", "--host", "acme"])

    assert result.exit_code == 1
    assert "Canvas Platform does not list plugins yet" in result.output + result.stderr
    assert "canvas logout" in result.output + result.stderr
    ini_token.assert_not_called()


def test_list_shows_platform_refusal_sentence(
    requests_mock: requests_mock_module.Mocker, instances: None, ini_token: Mock
) -> None:
    """A coded refusal is shown as Platform wrote it and never retried on credentials.ini."""
    requests_mock.get(
        f"{API}/instances/acme/plugins",
        status_code=403,
        json={"error": "That needs view_instance in Acme.", "code": "forbidden"},
    )

    result = runner.invoke(app, ["list", "--host", "acme"])

    assert result.exit_code == 1
    assert "That needs view_instance in Acme." in result.output + result.stderr
    ini_token.assert_not_called()


# -- enable / disable --------------------------------------------------------


@pytest.mark.parametrize("verb", ["enable", "disable"])
def test_enable_and_disable_dispatch_a_deployment_for_a_managed_plugin(
    verb: str, requests_mock: requests_mock_module.Mocker, managed_plugin: None
) -> None:
    """The deployment's action names the direction, so disable cannot read as enable."""
    requests_mock.post(f"{API}/deployments", status_code=202, json=_deployment(verb))

    result = runner.invoke(app, [verb, NAME, "--instance", "acme"])

    assert result.exit_code == 0, result.output
    assert _calls(requests_mock, "POST", f"{API}/deployments")[0].json() == {
        "action": verb,
        "plugins": [{"name": NAME}],
        "instances": ["acme"],
    }


def test_enable_without_instance_targets_the_only_installed_instance(
    requests_mock: requests_mock_module.Mocker, managed_plugin: None
) -> None:
    """With one instance holding the plugin, no --instance is needed."""
    requests_mock.post(f"{API}/deployments", status_code=202, json=_deployment("enable"))

    result = runner.invoke(app, ["enable", NAME])

    assert result.exit_code == 0, result.output
    assert _calls(requests_mock, "POST", f"{API}/deployments")[0].json()["instances"] == ["acme"]


def test_enable_refuses_host_for_a_managed_plugin(
    requests_mock: requests_mock_module.Mocker, managed_plugin: None
) -> None:
    """--host would bypass Platform, so a managed plugin is named by --instance only."""
    result = runner.invoke(app, ["enable", NAME, "--host", "acme"])

    assert result.exit_code == 2
    assert "--instance" in result.output + result.stderr
    assert not _calls(requests_mock, "POST", f"{API}/deployments")


@pytest.mark.parametrize("verb", ["enable", "disable"])
def test_enable_and_disable_of_an_unmanaged_plugin_go_to_the_instance(
    verb: str, requests_mock: requests_mock_module.Mocker, signed_in: None
) -> None:
    """A plugin Platform does not have is switched on the instance directly."""
    requests_mock.get(f"{API}/plugins/{NAME}", status_code=404, json={"error": "Not found."})

    with patch(f"canvas_cli.apps.platform.commands.instance_plugin.{verb}") as mock:
        result = runner.invoke(app, [verb, NAME, "--host", "https://x.example"])

    assert result.exit_code == 0, result.output
    mock.assert_called_once_with(name=NAME, host="https://x.example")
    assert not _calls(requests_mock, "POST", f"{API}/deployments")


# -- config list -------------------------------------------------------------


def test_config_list_prints_set_state_and_never_the_value(
    requests_mock: requests_mock_module.Mocker, managed_plugin: None
) -> None:
    """Variable values are write-only in the CLI: only the key and whether it is set print."""
    requests_mock.get(
        f"{API}/instances/acme/plugins/{NAME}/variables",
        json={
            "variables": [
                {
                    "key": "ApiKey",
                    "sensitive": True,
                    "declared": True,
                    "set": True,
                    "value": "hunter2",
                    "default": None,
                },
                {
                    "key": "Region",
                    "sensitive": False,
                    "declared": True,
                    "set": False,
                    "value": None,
                    "default": "us",
                },
            ]
        },
    )

    result = runner.invoke(app, ["config", "list", NAME])

    assert result.exit_code == 0, result.output
    assert "  ApiKey = [set]  (sensitive)" in result.stdout
    assert "  Region = [not set]" in result.stdout
    assert "hunter2" not in result.stdout + result.stderr


def test_config_list_with_no_variables(
    requests_mock: requests_mock_module.Mocker, managed_plugin: None
) -> None:
    """An empty list prints the same sentence as the credentials path."""
    requests_mock.get(f"{API}/instances/acme/plugins/{NAME}/variables", json={"variables": []})

    result = runner.invoke(app, ["config", "list", NAME])

    assert result.exit_code == 0, result.output
    assert "No variables configured." in result.stdout


def test_config_list_with_several_installs_names_them(
    requests_mock: requests_mock_module.Mocker, signed_in: None
) -> None:
    """Without --instance and several installs, the command asks which one rather than guessing."""
    requests_mock.get(
        f"{API}/plugins/{NAME}",
        json={
            "name": NAME,
            "publisher": "acme",
            "installs": [
                {"instance": "acme", "sha": "1", "enabled": True},
                {"instance": "acme-prod", "sha": "1", "enabled": True},
            ],
        },
    )

    result = runner.invoke(app, ["config", "list", NAME])

    assert result.exit_code == 2
    assert "acme, acme-prod" in result.output + result.stderr


def test_config_list_with_several_instances_heads_each(
    requests_mock: requests_mock_module.Mocker, signed_in: None
) -> None:
    """Each named instance is read once, under its own heading."""
    requests_mock.get(
        f"{API}/plugins/{NAME}",
        json={"name": NAME, "publisher": "acme", "installs": []},
    )
    for slug, is_set in (("acme", True), ("acme-prod", False)):
        requests_mock.get(
            f"{API}/instances/{slug}/plugins/{NAME}/variables",
            json={"variables": [{"key": "Region", "sensitive": False, "set": is_set}]},
        )

    result = runner.invoke(
        app, ["config", "list", NAME, "--instance", "acme", "--instance", "acme-prod"]
    )

    assert result.exit_code == 0, result.output
    assert result.stdout.splitlines() == [
        "acme:",
        "  Region = [set]",
        "acme-prod:",
        "  Region = [not set]",
    ]


def test_config_list_of_an_unmanaged_plugin_goes_to_the_instance(
    requests_mock: requests_mock_module.Mocker, signed_in: None
) -> None:
    """A plugin Platform does not have is read from the instance."""
    requests_mock.get(f"{API}/plugins/{NAME}", status_code=404, json={"error": "Not found."})

    with patch("canvas_cli.apps.platform.commands.instance_plugin.list_secrets") as mock:
        result = runner.invoke(app, ["config", "list", NAME, "--host", "https://x.example"])

    assert result.exit_code == 0, result.output
    mock.assert_called_once_with(plugin=NAME, host="https://x.example")


# -- namespace ---------------------------------------------------------------


def test_namespace_list_goes_through_platform_for_a_managed_instance(
    requests_mock: requests_mock_module.Mocker, instances: None, ini_token: Mock
) -> None:
    """A managed instance's namespaces come from Platform's pass-through of home-app's body."""
    requests_mock.get(
        f"{API}/instances/acme/namespaces",
        json={"namespaces": [{"name": NS, "table_count": 4, "custom_table_count": 1}]},
    )

    result = runner.invoke(app, ["namespace", "list", "--host", "acme"])

    assert result.exit_code == 0, result.output
    assert f"{NS}\ttables: 4\tcustom: 1" in result.stdout
    ini_token.assert_not_called()


def test_namespace_list_shows_platforms_not_found_sentence(
    requests_mock: requests_mock_module.Mocker, instances: None, ini_token: Mock
) -> None:
    """A coded 404 on the list route is Platform's refusal, not a Platform without the route."""
    requests_mock.get(
        f"{API}/instances/acme/namespaces",
        status_code=404,
        json={"error": "No such instance.", "code": "not_found"},
    )

    result = runner.invoke(app, ["namespace", "list", "--host", "acme"])

    assert result.exit_code == 1
    assert "No such instance." in result.output + result.stderr
    assert "does not manage namespaces yet" not in result.output + result.stderr
    ini_token.assert_not_called()


def test_namespace_inspect_prints_tables(
    requests_mock: requests_mock_module.Mocker, instances: None
) -> None:
    """Inspect prints the same layout as the credentials path."""
    requests_mock.get(
        NS_URL,
        json={
            "namespace": NS,
            "system_tables": [{"name": "keys", "approx_rows": 2}],
            "custom_tables": [
                {
                    "name": "notes",
                    "approx_rows": 5,
                    "columns": [{"name": "id", "type": "integer", "nullable": False}],
                }
            ],
        },
    )

    result = runner.invoke(app, ["namespace", "inspect", NS, "--host", "acme"])

    assert result.exit_code == 0, result.output
    assert "  notes\t~5 rows" in result.stdout
    assert "    id\tinteger\tnot null" in result.stdout


def test_namespace_inspect_missing_namespace(
    requests_mock: requests_mock_module.Mocker, instances: None
) -> None:
    """A not_found refusal prints the same line as the credentials path."""
    requests_mock.get(
        NS_URL, status_code=404, json={"error": "No such namespace.", "code": "not_found"}
    )

    result = runner.invoke(app, ["namespace", "inspect", NS, "--host", "acme"])

    assert result.exit_code == 1
    assert f"Namespace '{NS}' does not exist." in result.stdout + result.stderr


@pytest.mark.parametrize(
    ("status", "code", "sentence"),
    [
        (403, "forbidden", "That needs uninstall_plugin in Acme."),
        (409, "instance_outdated", "acme runs a release without namespace routes."),
        (409, "consent_pending", "A consent request names this namespace."),
    ],
)
def test_namespace_refusals_show_platforms_sentence_and_skip_credentials_ini(
    status: int,
    code: str,
    sentence: str,
    requests_mock: requests_mock_module.Mocker,
    instances: None,
    ini_token: Mock,
) -> None:
    """A refusal on a managed instance is shown as written; retrying on credentials.ini would
    act on the instance outside Platform's access and audit rules.
    """
    requests_mock.get(NS_URL, status_code=status, json={"error": sentence, "code": code})

    result = runner.invoke(app, ["namespace", "inspect", NS, "--host", "acme"])

    assert result.exit_code == 1
    assert sentence in result.stdout + result.stderr
    ini_token.assert_not_called()


def test_namespace_reset_dry_run_previews(
    requests_mock: requests_mock_module.Mocker, instances: None
) -> None:
    """Without --execute only the dry-run call is made."""
    requests_mock.post(
        f"{NS_URL}/reset?dry_run=true",
        json={
            "dry_run": True,
            "namespace": NS,
            "tables_to_drop": [{"name": "notes", "approx_rows": 5}],
            "tables_to_truncate": [{"name": "keys", "approx_rows": 2}],
        },
    )

    result = runner.invoke(app, ["namespace", "reset", NS, "--host", "acme"])

    assert result.exit_code == 0, result.output
    assert "  notes\t~5 rows" in result.stdout
    assert "This is a dry run" in result.stdout
    assert len(_calls(requests_mock, "POST", f"{NS_URL}/reset")) == 1


def test_namespace_reset_execute_with_typed_name(
    requests_mock: requests_mock_module.Mocker, instances: None
) -> None:
    """--execute previews, confirms the typed name, then makes the real call."""
    requests_mock.post(
        f"{NS_URL}/reset?dry_run=true",
        json={"dry_run": True, "namespace": NS, "tables_to_drop": [], "tables_to_truncate": []},
    )
    requests_mock.post(
        f"{NS_URL}/reset?dry_run=false",
        json={
            "dry_run": False,
            "namespace": NS,
            "tables_dropped": ["notes"],
            "tables_truncated": ["keys"],
        },
    )

    result = runner.invoke(
        app, ["namespace", "reset", NS, "--host", "acme", "--execute"], input=f"{NS}\n"
    )

    assert result.exit_code == 0, result.output
    assert f"Namespace '{NS}' has been reset." in result.stdout
    assert "Dropped tables: notes" in result.stdout
    assert [r.qs for r in _calls(requests_mock, "POST", f"{NS_URL}/reset")] == [
        {"dry_run": ["true"]},
        {"dry_run": ["false"]},
    ]


def test_namespace_reset_with_wrong_typed_name_makes_no_real_call(
    requests_mock: requests_mock_module.Mocker, instances: None
) -> None:
    """A mistyped confirmation aborts before the destructive call: the typed name is the
    person's last check that they are resetting the namespace they meant.
    """
    requests_mock.post(
        f"{NS_URL}/reset?dry_run=true",
        json={"dry_run": True, "namespace": NS, "tables_to_drop": [], "tables_to_truncate": []},
    )

    result = runner.invoke(
        app, ["namespace", "reset", NS, "--host", "acme", "--execute"], input="nope\n"
    )

    assert result.exit_code == 1
    assert [r.qs for r in _calls(requests_mock, "POST", f"{NS_URL}/reset")] == [
        {"dry_run": ["true"]}
    ]


def test_namespace_drop_execute_with_typed_name(
    requests_mock: requests_mock_module.Mocker, instances: None
) -> None:
    """A confirmed drop makes the real call and reports it."""
    requests_mock.post(
        f"{NS_URL}/drop?dry_run=true",
        json={"dry_run": True, "namespace": NS, "tables": [{"name": "notes", "approx_rows": 5}]},
    )
    requests_mock.post(
        f"{NS_URL}/drop?dry_run=false",
        json={"dry_run": False, "namespace": NS, "dropped": True},
    )

    result = runner.invoke(
        app, ["namespace", "drop", NS, "--host", "acme", "--execute"], input=f"{NS}\n"
    )

    assert result.exit_code == 0, result.output
    assert f"Namespace '{NS}' has been dropped." in result.stdout


def test_namespace_drop_refused_for_pending_consent(
    requests_mock: requests_mock_module.Mocker, instances: None, ini_token: Mock
) -> None:
    """A real drop refused with consent_pending is shown and not retried on credentials.ini."""
    requests_mock.post(
        f"{NS_URL}/drop?dry_run=true",
        json={"dry_run": True, "namespace": NS, "tables": []},
    )
    requests_mock.post(
        f"{NS_URL}/drop?dry_run=false",
        status_code=409,
        json={"error": "A consent request is pending.", "code": "consent_pending"},
    )

    result = runner.invoke(
        app, ["namespace", "drop", NS, "--host", "acme", "--execute"], input=f"{NS}\n"
    )

    assert result.exit_code == 1
    assert "A consent request is pending." in result.stdout + result.stderr
    ini_token.assert_not_called()


def test_namespace_of_an_unmanaged_instance_uses_credentials_ini(
    requests_mock: requests_mock_module.Mocker, instances: None, ini_token: Mock
) -> None:
    """An unmanaged instance's namespaces are read from the instance."""
    requests_mock.get(
        "https://legacy.canvasmedical.com/plugin-io/namespaces/",
        json={"namespaces": [{"name": NS, "table_count": 1, "custom_table_count": 0}]},
    )

    result = runner.invoke(app, ["namespace", "list", "--host", "legacy"])

    assert result.exit_code == 0, result.output
    assert NS in result.stdout
    assert not _calls(requests_mock, "GET", f"{API}/instances/legacy/namespaces")


# -- scenarios across Platform and the CLI -----------------------------------


@pytest.mark.parametrize("verb", ["enable", "disable"])
def test_a_managed_plugin_on_an_unmanaged_instance_shows_platforms_refusal(
    verb: str, requests_mock: requests_mock_module.Mocker, managed_plugin: None, ini_token: Mock
) -> None:
    """Platform refuses a managed plugin's switch on an instance it does not manage. The CLI shows
    that and never retries on credentials.ini, which would switch it outside Platform's audit (D1).
    """
    requests_mock.post(
        f"{API}/deployments",
        status_code=400,
        json={
            "error": "legacy trusts another platform to deploy to it, not this one.",
            "code": "unmanaged",
        },
    )

    with patch(f"canvas_cli.apps.platform.commands.instance_plugin.{verb}") as direct:
        result = runner.invoke(app, [verb, NAME, "--instance", "legacy"])

    assert result.exit_code == 1
    assert "legacy trusts another platform" in result.output + result.stderr
    direct.assert_not_called()
    ini_token.assert_not_called()


def test_namespace_drop_finishes_an_interrupted_drop(
    requests_mock: requests_mock_module.Mocker, instances: None
) -> None:
    """After a drop removed the schema but Platform kept its keys, Platform previews an empty
    drop and the confirmed real drop forgets them, so the CLI rerun clears the leftover state.
    """
    requests_mock.post(
        f"{NS_URL}/drop?dry_run=true", json={"dry_run": True, "namespace": NS, "tables": []}
    )
    requests_mock.post(
        f"{NS_URL}/drop?dry_run=false", json={"dry_run": False, "namespace": NS, "dropped": True}
    )

    result = runner.invoke(
        app, ["namespace", "drop", NS, "--host", "acme", "--execute"], input=f"{NS}\n"
    )

    assert result.exit_code == 0, result.output + result.stderr
    assert f"Namespace '{NS}' has been dropped." in result.stdout
    assert [r.qs for r in _calls(requests_mock, "POST", f"{NS_URL}/drop")] == [
        {"dry_run": ["true"]},
        {"dry_run": ["false"]},
    ]


@pytest.mark.parametrize(
    ("args", "method", "url"),
    [
        (["namespace", "list"], "GET", f"{API}/instances/acme/namespaces"),
        (["namespace", "inspect", NS], "GET", NS_URL),
        (["namespace", "reset", NS], "POST", f"{NS_URL}/reset?dry_run=true"),
        (["namespace", "drop", NS], "POST", f"{NS_URL}/drop?dry_run=true"),
    ],
    ids=["list", "inspect", "reset", "drop"],
)
def test_namespace_commands_before_platform_serves_them_say_how_to_use_credentials_ini(
    args: list[str],
    method: str,
    url: str,
    requests_mock: requests_mock_module.Mocker,
    instances: None,
    ini_token: Mock,
) -> None:
    """A CLI released before Platform has the namespace routes gets Django's bare 404. As with
    `canvas list`, that means the route is missing, so the command says how to reach the
    instance directly instead of printing only the status (Q1, option a).
    """
    requests_mock.register_uri(method, url, status_code=404, text="<h1>Not Found</h1>")

    result = runner.invoke(app, [*args, "--host", "acme"])

    assert result.exit_code == 1
    output = result.output + result.stderr
    assert "Canvas Platform does not" in output
    assert "canvas logout" in output
    assert "credentials.ini" in output
    ini_token.assert_not_called()
