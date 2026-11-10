"""Tests for the commands that route through Canvas Platform per target.

`canvas list`, `canvas namespace *` and `canvas logs` route per instance: signed in, a managed
instance goes through Platform and any other Canvas instance is refused; signed out, or for
localhost, credentials.ini serves. `canvas enable`, `canvas disable`, `canvas config *` and
`canvas uninstall` route per plugin the same way. HTTP is mocked with requests-mock, with the bodies the
Platform and home-app contracts document.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

import click
import pytest
import requests
import requests_mock as requests_mock_module
from typer.testing import CliRunner

from canvas_cli.apps.auth import utils as auth_utils
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


def _instance(
    slug: str,
    *capabilities: str,
    managed: bool = True,
    production: bool = False,
) -> dict[str, Any]:
    return {
        "slug": slug,
        "organization": "acme",
        "stage": "production" if production else "staging",
        "production": production,
        "managed": managed,
        "capabilities": list(capabilities),
    }


def _calls(mock: requests_mock_module.Mocker, method: str, url: str) -> list[Any]:
    return [r for r in mock.request_history if r.method == method and r.url.startswith(url)]


@pytest.fixture(autouse=True)
def platform_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Point the CLI at the test platform, with no credentials.ini."""
    monkeypatch.setenv(auth.PLATFORM_URL_ENV, PLATFORM)
    monkeypatch.setattr(auth_utils, "CONFIG_PATH", tmp_path / "missing-credentials.ini")


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
    assert managed_instance(HOST, "list") is None
    assert not requests_mock.called


def test_managed_instance_is_none_for_localhost(
    requests_mock: requests_mock_module.Mocker, signed_in: None
) -> None:
    """A host outside canvasmedical.com has no slug, so Platform cannot manage it."""
    assert managed_instance("http://localhost:8000", "list") is None
    assert not requests_mock.called


def test_managed_instance_returns_client_and_slug(instances: None) -> None:
    """A managed instance in the person's list yields the client and its slug."""
    found = managed_instance(HOST, "list")

    assert found is not None
    assert found.slug == "acme"
    assert found.production is False


@pytest.mark.parametrize(
    ("host", "cause"),
    [
        ("https://legacy.canvasmedical.com", "Canvas Platform does not manage legacy."),
        (
            "https://other.canvasmedical.com",
            "other is not one of your instances on Canvas Platform.",
        ),
    ],
    ids=["unmanaged", "not-listed"],
)
def test_managed_instance_refuses_what_platform_does_not_manage(
    host: str, cause: str, instances: None
) -> None:
    """Signed in, a Canvas instance Platform does not manage is refused, never left to credentials.ini."""
    with pytest.raises(click.ClickException) as raised:
        managed_instance(host, "list")

    assert cause in raised.value.message
    assert "sign out with `canvas logout`" in raised.value.message


def test_managed_instance_refusal_under_service_token_names_the_variable(
    requests_mock: requests_mock_module.Mocker, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``canvas logout`` leaves CANVAS_PLATFORM_TOKEN in force, so the way out is unsetting it."""
    monkeypatch.setenv(auth.SERVICE_TOKEN_ENV, "cnvs_sa_ci")
    requests_mock.get(f"{API}/instances", json={"instances": [_instance("legacy", managed=False)]})

    with pytest.raises(click.ClickException) as raised:
        managed_instance("https://legacy.canvasmedical.com", "list")

    assert "unset CANVAS_PLATFORM_TOKEN" in raised.value.message
    assert "canvas logout" not in raised.value.message


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


@pytest.mark.parametrize(
    "command",
    [
        ["list"],
        ["namespace", "list"],
        ["namespace", "inspect", NS],
        ["namespace", "reset", NS],
        ["namespace", "drop", NS],
    ],
    ids=" ".join,
)
def test_instance_command_refuses_an_unmanaged_instance_while_signed_in(
    command: list[str],
    requests_mock: requests_mock_module.Mocker,
    instances: None,
    ini_token: Mock,
) -> None:
    """Signed in, an instance Platform does not manage is refused with the way to sign out."""
    result = runner.invoke(app, [*command, "--host", "legacy"])

    assert result.exit_code == 1
    assert "Canvas Platform does not manage legacy." in result.stderr
    assert "sign out with `canvas logout`" in result.stderr
    ini_token.assert_not_called()
    assert not _calls(requests_mock, "GET", "https://legacy.canvasmedical.com")


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
        "plugins": [{"name": NAME, "publisher": "acme"}],
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
    requests_mock.get(
        f"{API}/instances",
        json={"instances": [_instance("acme"), _instance("acme-prod", production=True)]},
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
    assert f"permanently drop namespace '{NS}' on acme." in result.stdout
    assert "instance slug" not in result.stdout


@pytest.fixture
def production_instance(requests_mock: requests_mock_module.Mocker, signed_in: None) -> None:
    """`acme` is a managed production instance."""
    requests_mock.get(
        f"{API}/instances",
        json={"instances": [_instance("acme", "view_instance", production=True)]},
    )


@pytest.mark.parametrize(
    ("typed", "real_calls"),
    [("acme", 1), ("acme-staging", 0)],
    ids=["slug-matches", "slug-mismatch"],
)
def test_namespace_drop_on_production_also_asks_for_the_instance_slug(
    typed: str,
    real_calls: int,
    requests_mock: requests_mock_module.Mocker,
    production_instance: None,
) -> None:
    """A namespace has the same name on every instance a plugin runs on, so on production the
    typed slug is what catches a drop aimed at the wrong instance.
    """
    requests_mock.post(
        f"{NS_URL}/drop?dry_run=true", json={"dry_run": True, "namespace": NS, "tables": []}
    )
    requests_mock.post(
        f"{NS_URL}/drop?dry_run=false", json={"dry_run": False, "namespace": NS, "dropped": True}
    )

    result = runner.invoke(
        app, ["namespace", "drop", NS, "--host", "acme", "--execute"], input=f"{NS}\n{typed}\n"
    )

    assert f"permanently drop namespace '{NS}' on acme (PRODUCTION)." in result.stdout
    assert "Type the instance slug to confirm" in result.stdout
    assert result.exit_code == (0 if real_calls else 1), result.output
    assert len(_calls(requests_mock, "POST", f"{NS_URL}/drop?dry_run=false")) == real_calls


@pytest.mark.parametrize("verb", ["reset", "drop"])
def test_a_real_run_on_production_sends_the_typed_slug_to_platform(
    verb: str, requests_mock: requests_mock_module.Mocker, production_instance: None
) -> None:
    """Platform refuses a real reset or drop on production unless the request names the
    instance, so the slug typed at the prompt goes with the real call and not the preview.
    """
    requests_mock.post(f"{NS_URL}/{verb}", json={"dry_run": True, "namespace": NS})

    result = runner.invoke(
        app, ["namespace", verb, NS, "--host", "acme", "--execute"], input=f"{NS}\nacme\n"
    )

    assert result.exit_code == 0, result.output
    assert [r.qs for r in _calls(requests_mock, "POST", f"{NS_URL}/{verb}")] == [
        {"dry_run": ["true"]},
        {"dry_run": ["false"], "confirm_production": ["acme"]},
    ]


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


# -- scenarios across Platform and the CLI -----------------------------------


@pytest.mark.parametrize("verb", ["enable", "disable"])
def test_a_managed_plugin_on_an_unmanaged_instance_shows_platforms_refusal(
    verb: str, requests_mock: requests_mock_module.Mocker, managed_plugin: None, ini_token: Mock
) -> None:
    """Platform refuses a managed plugin's switch on an instance it does not manage. The CLI shows
    that and never retries on credentials.ini, which would switch it outside Platform's audit (D1).
    """
    requests_mock.get(
        f"{API}/instances",
        json={"instances": [_instance("acme", "deploy_plugin"), _instance("legacy")]},
    )
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


# -- credentials.ini while signed in, and its deprecation notice --------------

# Each per-plugin command, the instance function its credentials.ini path calls, and its
# arguments after the plugin name.
PLUGIN_COMMANDS: list[tuple[list[str], str, list[str]]] = [
    (["enable"], "enable", []),
    (["disable"], "disable", []),
    (["config", "list"], "list_secrets", []),
    (["config", "set"], "update", ["A=1"]),
    (["config", "unset"], "update", ["A"]),
    (["uninstall"], "uninstall", []),
]


@pytest.mark.parametrize(
    ("command", "direct", "extra"), PLUGIN_COMMANDS, ids=[" ".join(c[0]) for c in PLUGIN_COMMANDS]
)
@pytest.mark.parametrize("name", [NAME, "intake"], ids=["prefixed", "unprefixed"])
def test_plugin_command_refuses_an_unmanaged_plugin_on_an_instance_while_signed_in(
    command: list[str],
    direct: str,
    extra: list[str],
    name: str,
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
) -> None:
    """Signed in, a plugin Platform does not have is refused for a Canvas instance target."""
    requests_mock.get(f"{API}/plugins/{name}", status_code=404, json={"error": "Not found."})

    with patch(f"canvas_cli.apps.platform.commands.instance_plugin.{direct}") as mock:
        result = runner.invoke(app, [*command, name, *extra, "--instance", "legacy"])

    assert result.exit_code == 1
    assert f"Canvas Platform does not manage {name}." in result.stderr
    assert "sign out with `canvas logout`" in result.stderr
    mock.assert_not_called()


@pytest.mark.parametrize(
    ("command", "direct", "extra"), PLUGIN_COMMANDS, ids=[" ".join(c[0]) for c in PLUGIN_COMMANDS]
)
def test_signed_in_unknown_plugin_without_credentials_ini_is_refused(
    command: list[str],
    direct: str,
    extra: list[str],
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
) -> None:
    """Signed in with no flags and no credentials.ini, a plugin Platform does not have is
    refused with the way to sign out rather than a request for credentials.ini.
    """
    requests_mock.get(f"{API}/plugins/intake", status_code=404, json={"error": "Not found."})

    with patch(f"canvas_cli.apps.platform.commands.instance_plugin.{direct}") as mock:
        result = runner.invoke(app, [*command, "intake", *extra])

    assert result.exit_code == 1
    assert "Canvas Platform does not manage intake." in result.stderr
    assert "sign out with `canvas logout`" in result.stderr
    mock.assert_not_called()


@pytest.mark.parametrize(
    ("command", "direct", "extra"), PLUGIN_COMMANDS, ids=[" ".join(c[0]) for c in PLUGIN_COMMANDS]
)
@pytest.mark.parametrize(
    ("name", "answer"),
    [
        (
            "intake",
            {"json": {"name": "intake", "publisher": "other", "installs": [{"instance": "acme"}]}},
        ),
        (
            "intake",
            {
                "status_code": 409,
                "json": {
                    "error": "Two publishers have a plugin named 'intake'.",
                    "code": "ambiguous",
                },
            },
        ),
        (
            "acme__intake",
            {
                "json": {
                    "name": "acme__intake",
                    "publisher": "other",
                    "installs": [{"instance": "acme"}],
                }
            },
        ),
        (
            "vitals__chart",
            {
                "json": {
                    "name": "vitals__chart",
                    "publisher": "other",
                    "installs": [{"instance": "acme"}],
                }
            },
        ),
        (
            "acme__intake",
            {
                "status_code": 409,
                "json": {
                    "error": "Two publishers have a plugin named 'acme__intake'.",
                    "code": "ambiguous",
                },
            },
        ),
    ],
    ids=[
        "another-organizations-plugin",
        "ambiguous",
        "your-prefix-another-publisher",
        "unknown-prefix-another-publisher",
        "prefixed-ambiguous",
    ],
)
def test_plugin_none_of_your_organizations_publishes_is_not_managed(
    command: list[str],
    direct: str,
    extra: list[str],
    name: str,
    answer: dict[str, Any],
    requests_mock: requests_mock_module.Mocker,
    managed_plugin: None,
) -> None:
    """A plugin Platform shows only as another organization's plugin whose prefix the name
    does not carry, or as several publishers' plugins, is not one Platform manages for the
    person, with or without a prefix, so it is refused rather than changed through Platform.
    """
    requests_mock.get(f"{API}/me", json={"organizations": [{"slug": "acme"}]})
    requests_mock.get(f"{API}/plugins/{name}", **answer)

    with patch(f"canvas_cli.apps.platform.commands.instance_plugin.{direct}") as mock:
        result = runner.invoke(app, [*command, name, *extra, "--instance", "acme"])

    assert result.exit_code == 1
    assert f"Canvas Platform does not manage {name}." in result.stderr
    assert "sign out with `canvas logout`" in result.stderr
    assert not _calls(requests_mock, "POST", f"{API}/")
    assert not _calls(requests_mock, "PUT", f"{API}/")
    mock.assert_not_called()


def test_prefixed_plugin_its_publisher_owns_goes_through_platform_for_an_employee(
    requests_mock: requests_mock_module.Mocker, managed_plugin: None
) -> None:
    """A Canvas employee, none of whose organizations publishes ``acme__intake``, still goes
    through Platform for it, since the name carries its publisher acme's prefix.
    """
    requests_mock.get(
        f"{API}/me", json={"organizations": [{"slug": "canvas"}], "canvas_employee": True}
    )
    requests_mock.get(
        f"{API}/plugins/acme__intake",
        json={"name": "acme__intake", "publisher": "acme", "installs": [{"instance": "acme"}]},
    )
    requests_mock.post(f"{API}/deployments", status_code=202, json=_deployment("enable"))

    result = runner.invoke(app, ["enable", "acme__intake", "--instance", "acme"])

    assert result.exit_code == 0, result.output + result.stderr
    assert _calls(requests_mock, "POST", f"{API}/deployments")[0].json()["plugins"] == [
        {"name": "acme__intake", "publisher": "acme"}
    ]


EMPLOYEE_ME: dict[str, Any] = {"organizations": [{"slug": "canvas"}], "canvas_employee": True}
CUSTOMER_INTAKE: dict[str, Any] = {
    "name": "intake",
    "publisher": "acme",
    "installs": [{"instance": "acme"}],
}


def test_unprefixed_customer_plugin_goes_through_platform_for_an_employee(
    requests_mock: requests_mock_module.Mocker, managed_plugin: None
) -> None:
    """A Canvas employee, none of whose organizations publishes acme's ``intake``, goes
    through Platform for it, which then checks the command's capability.
    """
    requests_mock.get(f"{API}/me", json=EMPLOYEE_ME)
    requests_mock.get(f"{API}/plugins/intake", json=CUSTOMER_INTAKE)
    requests_mock.post(f"{API}/deployments", status_code=202, json=_deployment("enable"))

    with patch("canvas_cli.apps.platform.commands.instance_plugin.enable") as mock:
        result = runner.invoke(app, ["enable", "intake", "--instance", "acme"])

    assert result.exit_code == 0, result.output + result.stderr
    assert _calls(requests_mock, "POST", f"{API}/deployments")[0].json()["plugins"] == [
        {"name": "intake", "publisher": "acme"}
    ]
    mock.assert_not_called()


def test_employee_uninstall_of_a_customer_plugin_stops_at_platforms_capability_check(
    requests_mock: requests_mock_module.Mocker, managed_plugin: None
) -> None:
    """Platform's grants decide what a Canvas employee may do on a customer's plugin, so an
    uninstall Platform refuses stops with Platform's sentence and never reaches the instance.
    """
    requests_mock.get(f"{API}/me", json=EMPLOYEE_ME)
    requests_mock.get(f"{API}/plugins/intake", json=CUSTOMER_INTAKE)
    refusal = "You do not hold uninstall_plugin in Acme, which acme belongs to."
    requests_mock.post(
        f"{API}/deployments", status_code=403, json={"error": refusal, "code": "forbidden"}
    )

    with patch("canvas_cli.apps.platform.commands.instance_plugin.uninstall") as mock:
        result = runner.invoke(app, ["uninstall", "intake", "--instance", "acme", "--force"])

    assert result.exit_code == 1
    assert refusal in result.stderr
    assert "does not manage" not in result.stderr
    mock.assert_not_called()


def test_unprefixed_plugin_your_organization_publishes_goes_through_platform(
    requests_mock: requests_mock_module.Mocker, managed_plugin: None
) -> None:
    """An unprefixed name one of the person's organizations publishes goes through Platform,
    and the deployment names that publisher.
    """
    requests_mock.get(f"{API}/me", json={"organizations": [{"slug": "acme"}]})
    requests_mock.get(
        f"{API}/plugins/intake",
        json={"name": "intake", "publisher": "acme", "installs": [{"instance": "acme"}]},
    )
    requests_mock.post(f"{API}/deployments", status_code=202, json=_deployment("enable"))

    result = runner.invoke(app, ["enable", "intake", "--instance", "acme"])

    assert result.exit_code == 0, result.output + result.stderr
    assert _calls(requests_mock, "POST", f"{API}/deployments")[0].json()["plugins"] == [
        {"name": "intake", "publisher": "acme"}
    ]


@pytest.mark.parametrize(
    ("command", "direct", "extra"), PLUGIN_COMMANDS, ids=[" ".join(c[0]) for c in PLUGIN_COMMANDS]
)
@pytest.mark.parametrize(
    ("answer", "error"),
    [
        (
            {"exc": requests.exceptions.ConnectionError("Connection refused")},
            f"Could not reach Canvas Platform at {PLATFORM}: Connection refused",
        ),
        ({"status_code": 500, "json": {"error": "Platform is down."}}, "Platform is down."),
    ],
    ids=["unreachable", "server-error"],
)
def test_plugin_command_stops_when_platform_fails_the_plugin_lookup(
    command: list[str],
    direct: str,
    extra: list[str],
    answer: dict[str, Any],
    error: str,
    requests_mock: requests_mock_module.Mocker,
    managed_plugin: None,
) -> None:
    """A Platform that cannot be reached, or answers an error, on the plugin lookup stops the
    command with that error rather than reading the plugin as unmanaged and writing to the
    instance.
    """
    requests_mock.get(f"{API}/plugins/intake", **answer)

    with patch(f"canvas_cli.apps.platform.commands.instance_plugin.{direct}") as mock:
        result = runner.invoke(app, [*command, "intake", *extra, "--instance", "acme"])

    assert result.exit_code == 1
    assert f"Error: {error}" in result.stderr
    assert "does not manage" not in result.stderr
    assert not _calls(requests_mock, "POST", f"{API}/")
    assert not _calls(requests_mock, "PUT", f"{API}/")
    mock.assert_not_called()


@pytest.mark.parametrize(
    ("command", "direct", "extra"), PLUGIN_COMMANDS, ids=[" ".join(c[0]) for c in PLUGIN_COMMANDS]
)
def test_plugin_command_on_localhost_keeps_credentials_ini_while_signed_in(
    command: list[str],
    direct: str,
    extra: list[str],
    requests_mock: requests_mock_module.Mocker,
    signed_in: None,
) -> None:
    """Platform can never manage localhost, so a signed-in local run keeps credentials.ini."""
    with patch(f"canvas_cli.apps.platform.commands.instance_plugin.{direct}") as mock:
        result = runner.invoke(app, [*command, "intake", *extra, "--host", "localhost"])

    assert result.exit_code == 0, result.output + result.stderr
    assert mock.call_args.kwargs["host"] == "http://localhost:8000"
    assert not requests_mock.called


def _notice(command: str) -> str:
    return (
        f"`canvas {command}` with credentials.ini is deprecated in favor of `canvas login`, "
        "and is no longer supported as of December 14, 2026."
    )


@pytest.mark.parametrize(
    ("command", "direct", "extra"), PLUGIN_COMMANDS, ids=[" ".join(c[0]) for c in PLUGIN_COMMANDS]
)
def test_plugin_command_on_credentials_ini_prints_its_notice(
    command: list[str], direct: str, extra: list[str]
) -> None:
    """Every credentials.ini run names its own command in the deprecation notice."""
    with patch(f"canvas_cli.apps.platform.commands.instance_plugin.{direct}"):
        result = runner.invoke(app, [*command, NAME, *extra, "--host", "legacy"])

    assert result.exit_code == 0, result.output + result.stderr
    assert _notice(" ".join(command)) in result.stderr


def test_plugin_command_through_platform_prints_no_notice(
    requests_mock: requests_mock_module.Mocker, managed_plugin: None
) -> None:
    """The Platform path is the supported one, so it prints no credentials.ini notice."""
    requests_mock.post(f"{API}/deployments", status_code=202, json=_deployment("enable"))

    result = runner.invoke(app, ["enable", NAME, "--instance", "acme"])

    assert result.exit_code == 0, result.output
    assert "deprecated" not in result.stderr


@pytest.mark.parametrize(
    ("command", "url"),
    [
        (["list"], "https://legacy.canvasmedical.com/plugin-io/plugins/"),
        (["namespace", "list"], "https://legacy.canvasmedical.com/plugin-io/namespaces/"),
    ],
    ids=" ".join,
)
def test_instance_command_on_credentials_ini_prints_its_notice(
    command: list[str],
    url: str,
    requests_mock: requests_mock_module.Mocker,
    ini_token: Mock,
) -> None:
    """Signed out, an instance command reads the instance and prints its notice on stderr."""
    requests_mock.get(url, json={"results": [], "namespaces": []})

    result = runner.invoke(app, [*command, "--host", "legacy"])

    assert result.exit_code == 0, result.output + result.stderr
    assert _notice(" ".join(command)) in result.stderr
    assert "deprecated" not in result.stdout


@pytest.mark.parametrize(
    ("command", "direct", "extra"), PLUGIN_COMMANDS, ids=[" ".join(c[0]) for c in PLUGIN_COMMANDS]
)
def test_managed_plugin_on_localhost_keeps_credentials_ini_while_signed_in(
    command: list[str],
    direct: str,
    extra: list[str],
    requests_mock: requests_mock_module.Mocker,
    managed_plugin: None,
) -> None:
    """A prefixed plugin Platform manages still goes to localhost directly: Platform cannot
    reach a local instance, so it is never asked about the plugin.
    """
    with patch(f"canvas_cli.apps.platform.commands.instance_plugin.{direct}") as mock:
        result = runner.invoke(app, [*command, NAME, *extra, "--host", "localhost"])

    assert result.exit_code == 0, result.output + result.stderr
    assert mock.call_args.kwargs["host"] == "http://localhost:8000"
    assert not _calls(requests_mock, "GET", f"{API}/plugins/")


@pytest.fixture
def default_localhost(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A credentials.ini whose default host is localhost."""
    config = tmp_path / "credentials.ini"
    config.write_text("[localhost]\nclient_id=id\nclient_secret=secret\nis_default=true\n")
    monkeypatch.setattr(auth_utils, "CONFIG_PATH", config)


@pytest.mark.parametrize(
    ("command", "direct", "extra"), PLUGIN_COMMANDS, ids=[" ".join(c[0]) for c in PLUGIN_COMMANDS]
)
@pytest.mark.parametrize(
    "flags", [["--host", "localhost"], []], ids=["host-flag", "credentials-ini-default"]
)
def test_plugin_command_on_localhost_prints_no_notice(
    command: list[str],
    direct: str,
    extra: list[str],
    flags: list[str],
    default_localhost: None,
) -> None:
    """`canvas login` cannot serve localhost, so a local run is not told to switch to it,
    whether localhost is named with --host or is credentials.ini's default host.
    """
    with patch(f"canvas_cli.apps.platform.commands.instance_plugin.{direct}") as mock:
        result = runner.invoke(app, [*command, NAME, *extra, *flags])

    assert result.exit_code == 0, result.output + result.stderr
    assert mock.call_args.kwargs["host"] == "http://localhost:8000"
    assert "deprecated" not in result.stderr


@pytest.mark.parametrize(
    ("command", "direct", "extra"), PLUGIN_COMMANDS, ids=[" ".join(c[0]) for c in PLUGIN_COMMANDS]
)
def test_signed_in_local_default_host_wins_over_platform_installs(
    command: list[str],
    direct: str,
    extra: list[str],
    requests_mock: requests_mock_module.Mocker,
    managed_plugin: None,
    default_localhost: None,
) -> None:
    """Signed in with no flags, a credentials.ini default of localhost targets localhost,
    even for a plugin Platform has installed on a Canvas instance.
    """
    with patch(f"canvas_cli.apps.platform.commands.instance_plugin.{direct}") as mock:
        result = runner.invoke(app, [*command, NAME, *extra])

    assert result.exit_code == 0, result.output + result.stderr
    assert mock.call_args.kwargs["host"] == "http://localhost:8000"
    assert not _calls(requests_mock, "GET", f"{API}/plugins/")
    assert not _calls(requests_mock, "POST", f"{API}/")


@pytest.mark.parametrize(
    ("command", "direct", "extra"), PLUGIN_COMMANDS, ids=[" ".join(c[0]) for c in PLUGIN_COMMANDS]
)
@pytest.mark.parametrize(
    ("instance", "refusal"),
    [
        ("legacy", "Canvas Platform does not manage legacy."),
        ("other", "other is not one of your instances on Canvas Platform."),
    ],
    ids=["unmanaged", "unlisted"],
)
def test_managed_plugin_refuses_an_explicit_instance_platform_does_not_manage(
    command: list[str],
    direct: str,
    extra: list[str],
    instance: str,
    refusal: str,
    requests_mock: requests_mock_module.Mocker,
    managed_plugin: None,
) -> None:
    """An explicit --instance gets the same refusal and way back as the instance commands,
    before any deployment or variable call reaches Platform.
    """
    requests_mock.get(
        f"{API}/instances",
        json={
            "instances": [_instance("acme", "deploy_plugin"), _instance("legacy", managed=False)]
        },
    )

    with patch(f"canvas_cli.apps.platform.commands.instance_plugin.{direct}") as mock:
        result = runner.invoke(app, [*command, NAME, *extra, "--instance", instance])

    assert result.exit_code == 1
    assert refusal in result.stderr
    assert "sign out with `canvas logout`" in result.stderr
    assert not _calls(requests_mock, "POST", f"{API}/deployments")
    assert not _calls(requests_mock, "GET", f"{API}/instances/{instance}/")
    mock.assert_not_called()


def test_instance_command_on_localhost_prints_no_notice(
    requests_mock: requests_mock_module.Mocker, ini_token: Mock
) -> None:
    """A namespace run on localhost reads the local instance without the deprecation notice."""
    requests_mock.get("http://localhost:8000/plugin-io/namespaces/", json={"namespaces": []})

    result = runner.invoke(app, ["namespace", "list", "--host", "localhost"])

    assert result.exit_code == 0, result.output + result.stderr
    assert "deprecated" not in result.stderr


def test_namespace_instance_outdated_names_the_way_back_to_credentials_ini(
    requests_mock: requests_mock_module.Mocker, instances: None, ini_token: Mock
) -> None:
    """An instance too old for namespace routes is shown with how to use credentials.ini."""
    sentence = "acme runs a Canvas release that cannot manage namespaces yet."
    requests_mock.get(
        NS_URL, status_code=409, json={"error": sentence, "code": "instance_outdated"}
    )

    result = runner.invoke(app, ["namespace", "inspect", NS, "--host", "acme"])

    assert result.exit_code == 1
    output = result.stdout + result.stderr
    assert sentence in output
    assert "until it updates" in output
    assert "sign out with `canvas logout`" in output
    assert "credentials.ini" in output
    ini_token.assert_not_called()


@pytest.mark.parametrize("verb", ["reset", "drop"])
def test_namespace_real_run_waits_past_platforms_wait_and_reports_unknown_on_timeout(
    verb: str, requests_mock: requests_mock_module.Mocker, instances: None
) -> None:
    """A real reset or drop can outlast a short read timeout while the instance finishes it,
    so the CLI waits longer than Platform's 60 s and calls a timeout's outcome unknown.
    """
    requests_mock.post(
        f"{NS_URL}/{verb}?dry_run=true",
        json={"dry_run": True, "namespace": NS, "tables_to_drop": [], "tables_to_truncate": []},
    )
    requests_mock.post(f"{NS_URL}/{verb}?dry_run=false", exc=requests.exceptions.ReadTimeout)

    result = runner.invoke(
        app, ["namespace", verb, NS, "--host", "acme", "--execute"], input=f"{NS}\n"
    )

    assert result.exit_code == 1
    real = _calls(requests_mock, "POST", f"{NS_URL}/{verb}")[1]
    assert real.timeout > 60
    output = result.stdout + result.stderr
    assert "unknown" in output
    assert f"canvas namespace inspect {NS} --host acme" in output
    assert "Could not reach" not in output


@pytest.mark.parametrize("status", [502, 504])
@pytest.mark.parametrize("verb", ["reset", "drop"])
def test_namespace_real_run_answered_by_a_gateway_reports_unknown(
    verb: str, status: int, requests_mock: requests_mock_module.Mocker, instances: None
) -> None:
    """A load balancer's code-less 502 or 504 can come back while the instance finishes the
    write, so a real reset or drop it answers is reported as an unknown outcome.
    """
    requests_mock.post(
        f"{NS_URL}/{verb}?dry_run=true",
        json={"dry_run": True, "namespace": NS, "tables_to_drop": [], "tables_to_truncate": []},
    )
    requests_mock.post(
        f"{NS_URL}/{verb}?dry_run=false",
        status_code=status,
        text="<html><body>504 Gateway Time-out</body></html>",
        headers={"Content-Type": "text/html"},
    )

    result = runner.invoke(
        app, ["namespace", verb, NS, "--host", "acme", "--execute"], input=f"{NS}\n"
    )

    assert result.exit_code == 1
    output = result.stdout + result.stderr
    assert "unknown" in output
    assert f"canvas namespace inspect {NS} --host acme" in output


@pytest.mark.parametrize("verb", ["reset", "drop"])
def test_namespace_real_run_whose_connection_drops_reports_unknown(
    verb: str, requests_mock: requests_mock_module.Mocker, instances: None
) -> None:
    """A connection that drops after a confirmed real reset or drop was sent can leave the
    instance finishing the write, so the outcome is reported as unknown, as for a timeout.
    """
    requests_mock.post(
        f"{NS_URL}/{verb}?dry_run=true",
        json={"dry_run": True, "namespace": NS, "tables_to_drop": [], "tables_to_truncate": []},
    )
    requests_mock.post(
        f"{NS_URL}/{verb}?dry_run=false",
        exc=requests.exceptions.ConnectionError("Connection aborted: RemoteDisconnected"),
    )

    result = runner.invoke(
        app, ["namespace", verb, NS, "--host", "acme", "--execute"], input=f"{NS}\n"
    )

    assert result.exit_code == 1
    output = result.stdout + result.stderr
    assert "unknown" in output
    assert f"canvas namespace inspect {NS} --host acme" in output


def test_namespace_real_run_refused_by_platform_shows_platforms_sentence(
    requests_mock: requests_mock_module.Mocker, instances: None
) -> None:
    """A 502 that carries Platform's own code is Platform's answer, shown as it wrote it."""
    sentence = "Canvas Platform could not reach acme; try again shortly."
    requests_mock.post(
        f"{NS_URL}/drop?dry_run=true",
        json={"dry_run": True, "namespace": NS, "tables_to_drop": [], "tables_to_truncate": []},
    )
    requests_mock.post(
        f"{NS_URL}/drop?dry_run=false",
        status_code=502,
        json={"error": sentence, "code": "instance_unavailable"},
    )

    result = runner.invoke(
        app, ["namespace", "drop", NS, "--host", "acme", "--execute"], input=f"{NS}\n"
    )

    assert result.exit_code == 1
    output = result.stdout + result.stderr
    assert sentence in output
    assert "unknown" not in output
