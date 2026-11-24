import pytest

from canvas_sdk.test_utils.factories import DeviceCodingFactory, DeviceFactory
from canvas_sdk.v1.data import DeviceCoding


@pytest.mark.django_db
def test_device_codings_return_only_its_codings() -> None:
    """Device.codings returns only that device's codings."""
    parent = DeviceFactory.create()
    coding = DeviceCodingFactory.create(device=parent)
    DeviceCodingFactory.create()

    assert list(parent.codings.all()) == [coding]


@pytest.mark.django_db
def test_device_coding_resolves_to_its_device() -> None:
    """The device foreign key resolves to the parent Device."""
    parent = DeviceFactory.create()
    coding = DeviceCodingFactory.create(device=parent)

    fetched = DeviceCoding.objects.get(dbid=coding.dbid)

    assert fetched.device == parent
