import pytest
from django.db import models

from canvas_sdk.test_utils.factories import ContentTypeFactory, GroupFactory, PatientGroupFactory
from canvas_sdk.v1.data.group import Group


def test_group_fields() -> None:
    """Group exposes the content_type FK and object_id."""
    assert isinstance(Group._meta.get_field("content_type"), models.ForeignKey)
    assert isinstance(Group._meta.get_field("object_id"), models.BigIntegerField)


@pytest.mark.django_db
def test_patient_group_accessor_resolves_content_object() -> None:
    """group.patient_group resolves the PatientGroup content object; team stays None."""
    patient_group = PatientGroupFactory.create()
    group = GroupFactory.create(
        content_type=ContentTypeFactory.create(app_label="api", model="patientgroup"),
        object_id=patient_group.dbid,
    )

    assert group.patient_group == patient_group
    assert group.team is None
