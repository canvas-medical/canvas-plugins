from canvas_sdk.effects.compound_medications.compound_medication import CompoundMedication
from canvas_sdk.v1.data.compound_medication import CompoundMedication as CompoundMedicationModel


def test_static_validation_method_valid_data() -> None:
    """Test that static validation method passes for valid data."""
    errors = CompoundMedication.validate_compound_medication_fields(
        formulation="Valid Formulation",
        potency_unit_code=CompoundMedicationModel.PotencyUnits.TABLET,
        controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_NOT_SCHEDULED,
        controlled_substance_ndc="",
    )

    assert len(errors) == 0


def test_static_validation_method_empty_formulation() -> None:
    """Test that static validation method catches empty formulation."""
    errors = CompoundMedication.validate_compound_medication_fields(
        formulation="",
        potency_unit_code=CompoundMedicationModel.PotencyUnits.TABLET,
        controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_NOT_SCHEDULED,
        controlled_substance_ndc="",
    )

    assert len(errors) == 1
    assert "Field 'formulation' cannot be empty" in str(errors[0])


def test_static_validation_method_formulation_too_long() -> None:
    """Test that static validation method catches formulation that's too long."""
    long_formulation = "A" * 106
    errors = CompoundMedication.validate_compound_medication_fields(
        formulation=long_formulation,
        potency_unit_code=CompoundMedicationModel.PotencyUnits.TABLET,
        controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_NOT_SCHEDULED,
        controlled_substance_ndc="",
    )

    assert len(errors) == 1
    assert "Field 'formulation' must be 105 characters or less" in str(errors[0])


def test_static_validation_method_invalid_potency_unit() -> None:
    """Test that static validation method catches invalid potency unit."""
    errors = CompoundMedication.validate_compound_medication_fields(
        formulation="Valid Formulation",
        potency_unit_code="INVALID_CODE",
        controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_NOT_SCHEDULED,
        controlled_substance_ndc="",
    )

    assert len(errors) == 1
    assert "Invalid potency unit code: INVALID_CODE" in str(errors[0])


def test_static_validation_method_invalid_controlled_substance() -> None:
    """Test that static validation method catches invalid controlled substance."""
    errors = CompoundMedication.validate_compound_medication_fields(
        formulation="Valid Formulation",
        potency_unit_code=CompoundMedicationModel.PotencyUnits.TABLET,
        controlled_substance="INVALID_SCHEDULE",
        controlled_substance_ndc="",
    )

    assert len(errors) == 2  # Invalid controlled substance + NDC validation
    error_messages = [str(error) for error in errors]
    assert any("Invalid controlled substance: INVALID_SCHEDULE" in msg for msg in error_messages)
    assert any(
        "NDC is required when a Controlled Substance is specified" in msg for msg in error_messages
    )


def test_static_validation_method_ndc_required_for_scheduled() -> None:
    """Test that static validation method catches missing NDC for scheduled substances."""
    errors = CompoundMedication.validate_compound_medication_fields(
        formulation="Valid Formulation",
        potency_unit_code=CompoundMedicationModel.PotencyUnits.TABLET,
        controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_II,
        controlled_substance_ndc="",
    )

    assert len(errors) == 1
    assert "NDC is required when a Controlled Substance is specified" in str(errors[0])


def test_static_validation_method_ndc_whitespace_validation() -> None:
    """Test that static validation method catches whitespace-only NDC for scheduled substances."""
    errors = CompoundMedication.validate_compound_medication_fields(
        formulation="Valid Formulation",
        potency_unit_code=CompoundMedicationModel.PotencyUnits.TABLET,
        controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_II,
        controlled_substance_ndc="   ",
    )

    assert len(errors) == 1
    assert "NDC is required when a Controlled Substance is specified" in str(errors[0])


def test_static_validation_method_none_values() -> None:
    """Test that static validation method handles None values correctly."""
    errors = CompoundMedication.validate_compound_medication_fields(
        formulation=None,
        potency_unit_code=None,
        controlled_substance=None,
        controlled_substance_ndc=None,
    )

    assert len(errors) == 0


def test_static_validation_method_multiple_errors() -> None:
    """Test that static validation method collects multiple errors."""
    errors = CompoundMedication.validate_compound_medication_fields(
        formulation="",
        potency_unit_code="INVALID_CODE",
        controlled_substance="INVALID_SCHEDULE",
        controlled_substance_ndc="",
    )

    assert (
        len(errors) == 4
    )  # Empty formulation, invalid potency unit, invalid controlled substance, NDC required

    error_messages = [str(error) for error in errors]
    assert any("Field 'formulation' cannot be empty" in msg for msg in error_messages)
    assert any("Invalid potency unit code: INVALID_CODE" in msg for msg in error_messages)
    assert any("Invalid controlled substance: INVALID_SCHEDULE" in msg for msg in error_messages)
    assert any(
        "NDC is required when a Controlled Substance is specified" in msg for msg in error_messages
    )


def test_static_validation_method_valid_ndc_for_scheduled() -> None:
    """Test that static validation method passes for valid NDC with scheduled substance."""
    errors = CompoundMedication.validate_compound_medication_fields(
        formulation="Valid Formulation",
        potency_unit_code=CompoundMedicationModel.PotencyUnits.TABLET,
        controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_II,
        controlled_substance_ndc="12345-678-90",
    )

    assert len(errors) == 0


def test_static_validation_method_all_potency_units_valid() -> None:
    """Test that static validation method passes for all valid potency units."""
    for potency_unit_code, _ in CompoundMedicationModel.PotencyUnits.choices:
        errors = CompoundMedication.validate_compound_medication_fields(
            formulation="Valid Formulation",
            potency_unit_code=potency_unit_code,
            controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_NOT_SCHEDULED,
            controlled_substance_ndc="",
        )

        assert len(errors) == 0, f"Potency unit {potency_unit_code} should be valid"


def test_static_validation_method_all_controlled_substances_valid() -> None:
    """Test that static validation method passes for all valid controlled substances."""
    for controlled_substance, _ in CompoundMedicationModel.ControlledSubstanceOptions.choices:
        ndc = (
            "12345-678-90"
            if controlled_substance
            != CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_NOT_SCHEDULED.value
            else ""
        )

        errors = CompoundMedication.validate_compound_medication_fields(
            formulation="Valid Formulation",
            potency_unit_code=CompoundMedicationModel.PotencyUnits.TABLET,
            controlled_substance=controlled_substance,
            controlled_substance_ndc=ndc,
        )

        assert len(errors) == 0, f"Controlled substance {controlled_substance} should be valid"


def test_static_validation_method_formulation_whitespace() -> None:
    """Test that static validation method catches whitespace-only formulation."""
    errors = CompoundMedication.validate_compound_medication_fields(
        formulation="   ",
        potency_unit_code=CompoundMedicationModel.PotencyUnits.TABLET,
        controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_NOT_SCHEDULED,
        controlled_substance_ndc="",
    )

    assert len(errors) == 1
    assert "Field 'formulation' cannot be empty" in str(errors[0])


def test_static_validation_method_boundary_formulation_length() -> None:
    """Test that static validation method handles boundary case for formulation length."""
    # Test exactly 105 characters (should pass)
    formulation_105 = "A" * 105
    errors = CompoundMedication.validate_compound_medication_fields(
        formulation=formulation_105,
        potency_unit_code=CompoundMedicationModel.PotencyUnits.TABLET,
        controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_NOT_SCHEDULED,
        controlled_substance_ndc="",
    )

    assert len(errors) == 0

    # Test 106 characters (should fail)
    formulation_106 = "A" * 106
    errors = CompoundMedication.validate_compound_medication_fields(
        formulation=formulation_106,
        potency_unit_code=CompoundMedicationModel.PotencyUnits.TABLET,
        controlled_substance=CompoundMedicationModel.ControlledSubstanceOptions.SCHEDULE_NOT_SCHEDULED,
        controlled_substance_ndc="",
    )

    assert len(errors) == 1
    assert "Field 'formulation' must be 105 characters or less" in str(errors[0])
