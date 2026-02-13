# To run the tests, use the command `pytest` in the terminal or uv run pytest.
# Each test is wrapped inside a transaction that is rolled back at the end of the test.
# If you want to modify which files are used for testing, check the [tool.pytest.ini_options] section in pyproject.toml.
# from biography_factory import BiographyFactory
from datetime import datetime
from typing import cast

import factory

from canvas_generated.messages.events_pb2 import SIMPLE_API_REQUEST
from canvas_sdk.events import Event
from canvas_sdk.test_utils.factories import PatientFactory, StaffFactory
from canvas_sdk.v1.data import AttributeHub
from staff_plus.protocols.my_protocol import MyAPI, ProfileService
from staff_plus.models.proxy import StaffProxy, PatientProxy
# from specialty_factory import SpecialtyFactory

from staff_plus.models.biography import Biography
from staff_plus.models.specialty import Specialty, StaffSpecialty


# from tests.factories import SpecialtyFactory, BiographyFactory

class StaffProxyFactory(StaffFactory,factory.django.DjangoModelFactory[StaffProxy]):
    """Factory for creating StaffProxy."""
    class Meta:
        model = StaffProxy

class PatientProxyFactory(PatientFactory,factory.django.DjangoModelFactory[PatientProxy]):
    """Factory for creating PatientProxy."""
    class Meta:
        model = PatientProxy

# You can use a factory to create a patient instance for testing purposes.
def test_read_write_custom_data() -> None:

    # Test proxy factories
    patient = PatientProxyFactory.create()
    staff = StaffProxyFactory.create()

    now = str(datetime.now())
    # test attribute setting
    staff.set_attribute('patient_id', patient.id)
    patient.set_attribute("created_at", now)

    # test that attributes are in the db, not just in memory
    staff2 = StaffProxy.objects.get(id=staff.id)
    assert staff2.get_attribute('patient_id') == patient.id
    assert staff2.get_attribute('created_at') is None

    # test that attributes do not get misassigned to parent objects
    patient2 = PatientProxy.objects.get(id=patient.id)
    assert str(patient2.get_attribute('created_at')) == now
    print(f"patient2 {patient2.get_attribute('patient_id')}")
    assert patient2.get_attribute('patient_id') is None

    # test that attribute hubs work
    hub = AttributeHub.objects.create(type="data", externally_exposable_id="1234")
    hub.set_attribute('id', patient2.id)
    hub.set_attribute('created_at', patient.get_attribute('created_at'))
    assert hub.get_attribute('id') == patient2.id
    assert hub.get_attribute('created_at') == now

    # test creation and lookup of custom objects
    specialty = Specialty.objects.create(name="foo")
    assert specialty.name == "foo"
    specialty2 = Specialty.objects.get(dbid=specialty.dbid)
    assert specialty2.name == "foo"

    biography = Biography.objects.create(staff=staff, biography="biography", version=1.0, is_accepting_patients=True,
                                         extended_attributes={})
    biography.save()
    print(f"biography.dbid = {biography.dbid}")
    print(f"Biography {biography.__dict__}")

    biography2 = Biography.objects.get(dbid=biography.dbid)
    assert biography2.biography == "biography"

    # m2m associations can be created and read
    StaffSpecialty.objects.create(staff=staff, specialty=specialty)
    staff_ids = StaffSpecialty.objects.filter(specialty__name__in=[specialty.name]).values_list(
        "staff_id", flat=True
    )
    assert staff_ids[0] == staff.dbid


def test_api() -> None:
    staff = StaffProxyFactory.create()
    service = ProfileService(staff=staff)
    json_body = {
        "biography": "Some biography text in markdown format or HTML or something even better",
        "specialties": ["taxidermy", "philanthropy", "noodling"],
        "languages": ["english", "vulcan"],
        "practicing_since": 2005,
        "accepting_patients": False
    }

    service.upsert_profile_v1(json_body)
    assert staff.get_attribute("biography") == json_body["biography"]