import shutil
from collections.abc import Generator
from contextlib import chdir
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest
import requests
from django.core.exceptions import ImproperlyConfigured
from pydantic import ValidationError
from typer.testing import CliRunner

import settings
from canvas_cli.apps.plugin.plugin import _build_package, plugin_url
from canvas_cli.main import app
from canvas_sdk.commands.tests.test_utils import MaskedValue, wait_for_log
from canvas_sdk.effects.banner_alert import AddBannerAlert, RemoveBannerAlert

runner = CliRunner()


@pytest.fixture(scope="session")
def token() -> MaskedValue:
    """Get a valid token."""
    response = requests.post(
        f"{settings.INTEGRATION_TEST_URL}/auth/token/",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": settings.INTEGRATION_TEST_CLIENT_ID,
            "client_secret": settings.INTEGRATION_TEST_CLIENT_SECRET,
        },
    )
    response.raise_for_status()

    return MaskedValue(response.json()["access_token"])


@pytest.fixture(scope="session")
def first_patient_id(token: MaskedValue) -> dict:
    """Get the first patient id."""
    headers = {
        "Authorization": f"Bearer {token.value}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    response = requests.get(f"{settings.INTEGRATION_TEST_URL}/api/Patient", headers=headers)
    response.raise_for_status()
    patients = response.json()
    return patients["entry"][0]["resource"]["key"]


@pytest.fixture(scope="session")
def plugin_name() -> str:
    """Get the plugin name to be used."""
    return f"addbanneralert{datetime.now().timestamp()}".replace(".", "")


@pytest.fixture(scope="session")
def write_and_install_protocol_and_clean_up(
    first_patient_id: str, plugin_name: str, token: MaskedValue
) -> Generator[Any, Any, Any]:
    """Write the protocol code, install the plugin, and clean up after the test."""
    if not settings.INTEGRATION_TEST_URL:
        raise ImproperlyConfigured("INTEGRATION_TEST_URL is not set")

    # write the protocol
    with chdir(Path("./custom-plugins")):
        runner.invoke(app, "init", input=plugin_name)

    protocol_code = f"""
from canvas_sdk.effects.banner_alert import AddBannerAlert
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol

class Protocol(BaseProtocol):
    RESPONDS_TO = EventType.Name(EventType.ENCOUNTER_CREATED)
    def compute(self):
        return [
            AddBannerAlert(
                patient_id="{first_patient_id}",
                key="{plugin_name}",
                narrative="this is a test",
                placement=[AddBannerAlert.Placement.CHART],
                intent=AddBannerAlert.Intent.INFO,
            ).apply()
        ]
"""

    with open(f"./custom-plugins/{plugin_name}/protocols/my_protocol.py", "w") as protocol:
        protocol.write(protocol_code)

    with open(_build_package(Path(f"./custom-plugins/{plugin_name}")), "rb") as package:
        message_received_event, thread, ws = wait_for_log(
            settings.INTEGRATION_TEST_URL,
            token.value,
            f"Loading plugin '{plugin_name}",
        )

        # install the plugin
        response = requests.post(
            plugin_url(settings.INTEGRATION_TEST_URL),
            data={"is_enabled": True},
            files={"package": package},
            headers={"Authorization": f"Bearer {token.value}"},
        )
        response.raise_for_status()

        message_received_event.wait(timeout=15.0)

        # unfortunately sometimes the log websocket just doesn't return any
        # messages, so asserting on the state of the timeout here causes failures
        # even though the delay itself will cause the waiting test to pass (because
        # the plugin has been loaded).
        # timeout_not_hit = message_received_event.wait(timeout=15.0)
        # if not timeout_not_hit:
        #     ws.close()
        # assert timeout_not_hit, f"plugin loading message timeout hit: Loading plugin '{plugin_name}"
    yield

    ws.close()
    thread.join()

    # clean up
    if Path(f"./custom-plugins/{plugin_name}").exists():
        shutil.rmtree(Path(f"./custom-plugins/{plugin_name}"))

    # disable
    response = requests.patch(
        plugin_url(settings.INTEGRATION_TEST_URL, plugin_name),
        data={"is_enabled": False},
        headers={
            "Authorization": f"Bearer {token.value}",
        },
    )
    response.raise_for_status()

    # delete
    response = requests.delete(
        plugin_url(settings.INTEGRATION_TEST_URL, plugin_name),
        headers={"Authorization": f"Bearer {token.value}"},
    )
    response.raise_for_status()

    # confirm no more banner
    response = requests.get(
        f"{settings.INTEGRATION_TEST_URL}/api/BannerAlert/?patient__key={first_patient_id}",
        headers={
            "Authorization": f"Bearer {token.value}",
        },
    )
    response.raise_for_status()
    patient_banners_none = response.json()
    patient_banner = next(
        (b for b in patient_banners_none["results"] if b["key"] == plugin_name), None
    )
    assert patient_banner is None


@pytest.mark.integtest
def test_protocol_that_adds_banner_alert(
    write_and_install_protocol_and_clean_up: None,
    token: MaskedValue,
    plugin_name: str,
    first_patient_id: str,
) -> None:
    """Test that the protocol adds a banner alert."""
    # trigger the event
    response = requests.post(
        f"{settings.INTEGRATION_TEST_URL}/api/Note/",
        headers={
            "Authorization": f"Bearer {token.value}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        json={
            "patient": 1,
            "provider": 1,
            "note_type": "office",
            "note_type_version": 1,
            "lastModifiedBySessionKey": "8fee3c03a525cebee1d8a6b8e63dd4dg",
        },
    )
    response.raise_for_status()

    response = requests.get(
        f"{settings.INTEGRATION_TEST_URL}/api/BannerAlert/?patient__key={first_patient_id}",
        headers={
            "Authorization": f"Bearer {token.value}",
        },
    )
    response.raise_for_status()

    patient_banners = response.json()
    assert patient_banners["count"] > 0

    patient_banner = next(b for b in patient_banners["results"] if b["key"] == plugin_name)
    assert patient_banner["pluginName"] == plugin_name
    assert patient_banner["narrative"] == "this is a test"
    assert patient_banner["placement"] == ["chart"]
    assert patient_banner["intent"] == "info"
    assert patient_banner["href"] is None
    assert patient_banner["status"] == "active"


@pytest.mark.parametrize(
    "Effect,params,expected_payload",
    [
        (
            AddBannerAlert,
            {
                "patient_id": "uuid",
                "key": "test-key",
                "narrative": "hellooo",
                "placement": [AddBannerAlert.Placement.APPOINTMENT_CARD],
                "intent": AddBannerAlert.Intent.INFO,
            },
            '{"patient": "uuid", "patient_filter": null, "key": "test-key", "data": {"narrative": "hellooo", "placement": ["appointment_card"], "intent": "info", "href": null}}',
        ),
        (
            AddBannerAlert,
            {
                "patient_filter": {"active": True},
                "key": "test-key",
                "narrative": "hellooo",
                "placement": [AddBannerAlert.Placement.APPOINTMENT_CARD],
                "intent": AddBannerAlert.Intent.INFO,
            },
            '{"patient": null, "patient_filter": {"active": true}, "key": "test-key", "data": {"narrative": "hellooo", "placement": ["appointment_card"], "intent": "info", "href": null}}',
        ),
        (
            RemoveBannerAlert,
            {"patient_id": "uuid", "key": "testeroo"},
            '{"patient": "uuid", "patient_filter": null, "key": "testeroo"}',
        ),
        (
            RemoveBannerAlert,
            {"patient_filter": {"active": True}, "key": "testeroo"},
            '{"patient": null, "patient_filter": {"active": true}, "key": "testeroo"}',
        ),
    ],
)
def test_banner_alert_apply_method_succeeds_with_all_required_fields(
    Effect: type[AddBannerAlert] | type[RemoveBannerAlert], params: dict, expected_payload: str
) -> None:
    """Test that the apply method succeeds with all required fields."""
    b = Effect()
    for k, v in params.items():
        setattr(b, k, v)
    applied = b.apply()
    assert applied.payload == expected_payload


@pytest.mark.parametrize(
    "Effect,expected_err_msgs",
    [
        (
            AddBannerAlert,
            [
                "5 validation errors for AddBannerAlert",
                "Field 'patient_id' or 'patient_filter' is required to apply an AddBannerAlert [type=missing",
                "Field 'key' is required to apply an AddBannerAlert [type=missing",
                "Field 'narrative' is required to apply an AddBannerAlert [type=missing",
                "Field 'placement' is required to apply an AddBannerAlert [type=missing",
                "Field 'intent' is required to apply an AddBannerAlert [type=missing",
            ],
        ),
        (
            RemoveBannerAlert,
            [
                "2 validation errors for RemoveBannerAlert",
                "Field 'patient_id' or 'patient_filter' is required to apply a RemoveBannerAlert [type=missing",
                "Field 'key' is required to apply a RemoveBannerAlert [type=missing",
            ],
        ),
    ],
)
def test_banner_alert_apply_method_raises_error_without_required_fields(
    Effect: type[AddBannerAlert] | type[RemoveBannerAlert], expected_err_msgs: str
) -> None:
    """Test that the apply method raises an error when missing required fields."""
    b = Effect()
    with pytest.raises(ValidationError) as e:
        b.apply()
    err_msg = repr(e.value)
    for expected in expected_err_msgs:
        assert expected in err_msg
