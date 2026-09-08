import pytest

from canvas_sdk.v1.data.immunization import ImmunizationStatement
from canvas_sdk.value_set.value_set import ValueSet


class _DiabetesSampleValueSet(ValueSet):
    """Tiny value set fixture for find() tests."""

    VALUE_SET_NAME = "Diabetes Sample"
    OID = "tests.diabetes-sample"
    SNOMEDCT = {"73211009"}


@pytest.mark.django_db
def test_immunization_statement_find_resolves_singular_coding_accessor() -> None:
    """ImmunizationStatement.objects.find() no longer raises FieldError (KOALA-6939).

    Before the q_object override this raised
    ``FieldError: Cannot resolve keyword 'codings' into field`` because the coding child uses the
    singular ``coding`` reverse accessor. It should now resolve and simply return no rows.
    """
    assert list(ImmunizationStatement.objects.find(_DiabetesSampleValueSet)) == []
