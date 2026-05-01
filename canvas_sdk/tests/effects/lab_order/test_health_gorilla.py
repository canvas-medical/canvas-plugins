import json

import pytest
from pydantic import ValidationError

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.lab_order import HealthGorillaLabOrderOverride


def test_apply_with_all_fields_emits_full_payload() -> None:
    """All set fields appear in the effect payload under data."""
    effect = HealthGorillaLabOrderOverride(
        practitioner_account_number="12349876",
        organizational_account_number="12349876",
        hg_organization_id="f-388554647b89801ea5e8320b",
        hg_tenant_id="2cd27b62c3407f285c5ef6a4",
        hg_location_id="3395266614caee5d2dade684",
        bill_to_code="self",
    )

    proto_effect = effect.apply()

    assert proto_effect.type == EffectType.HEALTH_GORILLA_LAB_ORDER_OVERRIDE
    assert json.loads(proto_effect.payload) == {
        "data": {
            "practitioner_account_number": "12349876",
            "organizational_account_number": "12349876",
            "hg_organization_id": "f-388554647b89801ea5e8320b",
            "hg_tenant_id": "2cd27b62c3407f285c5ef6a4",
            "hg_location_id": "3395266614caee5d2dade684",
            "bill_to_code": "self",
        }
    }


def test_apply_omits_unset_fields() -> None:
    """Fields left as None are excluded from the payload entirely.

    A plugin overriding only one value should not stomp the others to None on
    the home-app side; the contract is "absent = no override".
    """
    effect = HealthGorillaLabOrderOverride(bill_to_code="patient")

    proto_effect = effect.apply()

    assert json.loads(proto_effect.payload) == {"data": {"bill_to_code": "patient"}}


def test_bill_to_code_rejects_invalid_value() -> None:
    """Pydantic Literal constrains bill_to_code to the four HG-recognized codes."""
    with pytest.raises(ValidationError):
        HealthGorillaLabOrderOverride(bill_to_code="client")  # type: ignore[arg-type]


@pytest.mark.parametrize("code", ["self", "patient", "guarantor", "thirdParty"])
def test_bill_to_code_accepts_valid_values(code: str) -> None:
    """All four HG-recognized bill-to codes round-trip cleanly."""
    effect = HealthGorillaLabOrderOverride(bill_to_code=code)  # type: ignore[arg-type]

    proto_effect = effect.apply()

    assert json.loads(proto_effect.payload)["data"]["bill_to_code"] == code


def test_empty_override_emits_empty_data() -> None:
    """An effect with no fields set is a valid no-op; payload is data: {}."""
    effect = HealthGorillaLabOrderOverride()

    proto_effect = effect.apply()

    assert proto_effect.type == EffectType.HEALTH_GORILLA_LAB_ORDER_OVERRIDE
    assert json.loads(proto_effect.payload) == {"data": {}}
