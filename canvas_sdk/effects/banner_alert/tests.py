import shutil
from contextlib import chdir
from pathlib import Path
from typing import Any

import pytest
import requests
from pydantic import ValidationError
from typer.testing import CliRunner

import settings
from canvas_cli.apps.plugin.plugin import _build_package, plugin_url
from canvas_cli.main import app
from canvas_sdk.commands.tests.test_utils import MaskedValue

runner = CliRunner()


@pytest.fixture(scope="session")
def token() -> MaskedValue:
    return MaskedValue(
        requests.post(
            f"{settings.INTEGRATION_TEST_URL}/auth/token/",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "client_credentials",
                "client_id": settings.INTEGRATION_TEST_CLIENT_ID,
                "client_secret": settings.INTEGRATION_TEST_CLIENT_SECRET,
            },
        ).json()["access_token"]
    )


def get_first_patient_id(token: MaskedValue) -> dict:
    headers = {
        "Authorization": f"Bearer {token.value}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    patients = requests.get(f"{settings.INTEGRATION_TEST_URL}/api/Patient", headers=headers).json()
    return patients["entry"][0]["resource"]["key"]


@pytest.mark.integtest
def test_protocol_that_adds_banner_alert(
    token: MaskedValue,
) -> None:
    patient_id = get_first_patient_id(token)

    with chdir(Path("./custom-plugins")):
        runner.invoke(app, "init", input="add_banner_alert")

    protocol = open("./custom-plugins/add_banner_alert/protocols/my_protocol.py", "w")
    protocol.write(
        f"""from canvas_sdk.effects.banner_alert import AddBannerAlert
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol

class Protocol(BaseProtocol):
    RESPONDS_TO = EventType.Name(EventType.ENCOUNTER_CREATED)
    def compute(self):
        return [
            AddBannerAlert(
                patient_id="{patient_id}",
                key="banners-test",
                narrative="this is a test",
                placement=[AddBannerAlert.Placement.CHART],
                intent=AddBannerAlert.Intent.INFO,
            ).apply()
        ]
"""
    )
    protocol.close()

    # install the plugin
    requests.post(
        plugin_url(settings.INTEGRATION_TEST_URL),
        data={"is_enabled": True},
        files={"package": open(_build_package(Path("./custom-plugins/add_banner_alert")), "rb")},
        headers={"Authorization": f"Bearer {token.value}"},
    )

    # trigger the event
    requests.post(
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

    patient_banners = requests.get(
        f"{settings.INTEGRATION_TEST_URL}/api/BannerAlert/?patient__key={patient_id}",
        headers={
            "Authorization": f"Bearer {token.value}",
        },
    ).json()
    assert patient_banners["count"] > 0

    patient_banner = next(b for b in patient_banners["results"] if b["key"] == "banners-test")
    assert patient_banner["pluginName"] == "add_banner_alert"
    assert patient_banner["narrative"] == "this is a test"
    assert patient_banner["placement"] == ["chart"]
    assert patient_banner["intent"] == "info"
    assert patient_banner["href"] is None
    assert patient_banner["status"] == "active"

    # clean up
    if Path(f"./custom-plugins/add_banner_alert").exists():
        shutil.rmtree(Path(f"./custom-plugins/add_banner_alert"))

    # disable
    requests.patch(
        plugin_url(settings.INTEGRATION_TEST_URL, "add_banner_alert"),
        data={"is_enabled": False},
        headers={
            "Authorization": f"Bearer {token.value}",
        },
    )
    # delete
    requests.delete(
        plugin_url(settings.INTEGRATION_TEST_URL, "add_banner_alert"),
        headers={"Authorization": f"Bearer {token.value}"},
    )

    # confirm no more banner
    patient_banners_none = requests.get(
        f"http://localhost:8000/api/BannerAlert/?patient__key={patient_id}",
        headers={
            "Authorization": f"Bearer {token.value}",
        },
    ).json()
    patient_banner = next(
        (b for b in patient_banners_none["results"] if b["key"] == "banners-test"), None
    )
    assert patient_banner is None
