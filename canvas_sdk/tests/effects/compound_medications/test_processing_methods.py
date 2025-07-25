from canvas_sdk.effects.compound_medications.compound_medication import CompoundMedication


def test_process_formulation_method() -> None:
    """Test the process_formulation static method."""
    # Test normal formulation
    result = CompoundMedication.process_formulation("Test Formulation")
    assert result == "Test Formulation"

    # Test formulation with whitespace
    result = CompoundMedication.process_formulation("  Test Formulation  ")
    assert result == "Test Formulation"

    # Test None input
    result = CompoundMedication.process_formulation(None)
    assert result is None

    # Test empty string
    result = CompoundMedication.process_formulation("")
    assert result == ""

    # Test whitespace only
    result = CompoundMedication.process_formulation("   ")
    assert result == ""


def test_process_ndc_method() -> None:
    """Test the process_ndc static method."""
    # Test normal NDC
    result = CompoundMedication.process_ndc("1234567890")
    assert result == "1234567890"

    # Test NDC with dashes
    result = CompoundMedication.process_ndc("12345-678-90")
    assert result == "1234567890"

    # Test NDC with multiple dashes
    result = CompoundMedication.process_ndc("12-34-56-78-90")
    assert result == "1234567890"

    # Test None input
    result = CompoundMedication.process_ndc(None)
    assert result is None

    # Test empty string
    result = CompoundMedication.process_ndc("")
    assert result == ""


def test_process_compound_medication_data_method() -> None:
    """Test the process_compound_medication_data static method."""
    # Test data with both formulation and NDC
    input_data = {
        "formulation": "  Test Formulation  ",
        "controlled_substance_ndc": "12345-678-90",
        "potency_unit_code": "C48542",
        "controlled_substance": "N",
        "active": True,
    }

    result = CompoundMedication.process_compound_medication_data(input_data)

    assert result["formulation"] == "Test Formulation"
    assert result["controlled_substance_ndc"] == "1234567890"
    assert result["potency_unit_code"] == "C48542"  # Unchanged
    assert result["controlled_substance"] == "N"  # Unchanged
    assert result["active"] is True  # Unchanged

    # Test data with None values
    input_data = {
        "formulation": None,
        "controlled_substance_ndc": None,
        "potency_unit_code": "C48542",
    }

    result = CompoundMedication.process_compound_medication_data(input_data)

    assert result["formulation"] is None
    assert result["controlled_substance_ndc"] is None
    assert result["potency_unit_code"] == "C48542"

    # Test empty data
    input_data = {}
    result = CompoundMedication.process_compound_medication_data(input_data)
    assert result == {}

    # Test data without compound medication fields
    input_data = {
        "other_field": "value",
        "another_field": 123,
    }

    result = CompoundMedication.process_compound_medication_data(input_data)
    assert result == input_data  # Should be unchanged


def test_process_compound_medication_data_doesnt_modify_original() -> None:
    """Test that process_compound_medication_data doesn't modify the original dictionary."""
    original_data = {
        "formulation": "  Test Formulation  ",
        "controlled_substance_ndc": "12345-678-90",
        "potency_unit_code": "C48542",
    }

    # Store original values
    original_formulation = original_data["formulation"]
    original_ndc = original_data["controlled_substance_ndc"]

    # Process data
    result = CompoundMedication.process_compound_medication_data(original_data)

    # Original data should be unchanged
    assert original_data["formulation"] == original_formulation
    assert original_data["controlled_substance_ndc"] == original_ndc

    # Result should be processed
    assert result["formulation"] == "Test Formulation"
    assert result["controlled_substance_ndc"] == "1234567890"


def test_process_compound_medication_data_with_mixed_fields() -> None:
    """Test processing with a mix of fields that need and don't need processing."""
    input_data = {
        "formulation": "  Valid Formulation  ",
        "potency_unit_code": "C48542",
        "controlled_substance": "II",
        "controlled_substance_ndc": "98765-432-10",
        "active": False,
        "other_field": "unchanged",
    }

    result = CompoundMedication.process_compound_medication_data(input_data)

    # Processed fields
    assert result["formulation"] == "Valid Formulation"
    assert result["controlled_substance_ndc"] == "9876543210"

    # Unchanged fields
    assert result["potency_unit_code"] == "C48542"
    assert result["controlled_substance"] == "II"
    assert result["active"] is False
    assert result["other_field"] == "unchanged"


def test_process_compound_medication_data_edge_cases() -> None:
    """Test edge cases for compound medication data processing."""
    # Test with empty strings
    input_data = {
        "formulation": "",
        "controlled_substance_ndc": "",
    }

    result = CompoundMedication.process_compound_medication_data(input_data)

    assert result["formulation"] == ""
    assert result["controlled_substance_ndc"] == ""

    # Test with whitespace strings
    input_data = {
        "formulation": "   ",
        "controlled_substance_ndc": "   ",
    }

    result = CompoundMedication.process_compound_medication_data(input_data)

    assert result["formulation"] == ""
    assert result["controlled_substance_ndc"] == "   "  # NDC processing only removes dashes


def test_process_formulation_edge_cases() -> None:
    """Test edge cases for formulation processing."""
    # Test with newlines and tabs
    result = CompoundMedication.process_formulation("  \n\t  Test Formulation  \n\t  ")
    assert result == "Test Formulation"

    # Test with multiple spaces
    result = CompoundMedication.process_formulation("Test     Formulation")
    assert result == "Test     Formulation"  # Internal spaces preserved

    # Test with special characters
    result = CompoundMedication.process_formulation("  Test-Formulation 2.5%  ")
    assert result == "Test-Formulation 2.5%"


def test_process_ndc_edge_cases() -> None:
    """Test edge cases for NDC processing."""
    # Test with no dashes
    result = CompoundMedication.process_ndc("1234567890")
    assert result == "1234567890"

    # Test with only dashes
    result = CompoundMedication.process_ndc("---")
    assert result == ""

    # Test with mixed characters
    result = CompoundMedication.process_ndc("ABC-123-XYZ")
    assert result == "ABC123XYZ"

    # Test with spaces (should not be affected)
    result = CompoundMedication.process_ndc("123 45-678 90")
    assert result == "123 45678 90"
