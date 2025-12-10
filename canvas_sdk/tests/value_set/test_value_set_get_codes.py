"""Tests for ValueSet.get_codes() method."""

from canvas_sdk.value_set.value_set import CombinedValueSet, ValueSet


class MockValueSetSingle(ValueSet):
    """A mock ValueSet with a single code system."""

    SNOMEDCT = {"123456", "789012", "345678"}


class MockValueSetMultiple(ValueSet):
    """A mock ValueSet with multiple code systems."""

    SNOMEDCT = {"123456", "789012"}
    ICD10CM = {"E11.9", "E10.9"}
    LOINC = {"12345-6", "67890-1"}


class MockValueSetEmpty(ValueSet):
    """A mock ValueSet with no codes."""

    pass


def test_get_codes_single_system() -> None:
    """Test getting codes from a ValueSet with a single code system."""
    codes = MockValueSetSingle.get_codes()

    assert isinstance(codes, set)
    assert len(codes) == 3
    assert "123456" in codes
    assert "789012" in codes
    assert "345678" in codes


def test_get_codes_multiple_systems() -> None:
    """Test getting codes from a ValueSet with multiple code systems."""
    codes = MockValueSetMultiple.get_codes()

    assert isinstance(codes, set)
    assert len(codes) == 6

    # SNOMED codes
    assert "123456" in codes
    assert "789012" in codes

    # ICD-10 codes
    assert "E11.9" in codes
    assert "E10.9" in codes

    # LOINC codes
    assert "12345-6" in codes
    assert "67890-1" in codes


def test_get_codes_empty_valueset() -> None:
    """Test getting codes from an empty ValueSet."""
    codes = MockValueSetEmpty.get_codes()

    assert isinstance(codes, set)
    assert len(codes) == 0


def test_get_codes_returns_unique_codes() -> None:
    """Test that get_codes() returns unique codes even if there are duplicates."""

    class MockValueSetDuplicates(ValueSet):
        """Mock ValueSet with duplicate codes across systems."""

        SNOMEDCT = {"123456", "789012"}
        ICD10CM = {"123456", "E11.9"}  # 123456 appears in both

    codes = MockValueSetDuplicates.get_codes()

    assert isinstance(codes, set)
    assert len(codes) == 3  # Should deduplicate
    assert "123456" in codes
    assert "789012" in codes
    assert "E11.9" in codes


def test_get_codes_preserves_original_valueset() -> None:
    """Test that calling get_codes() doesn't modify the original ValueSet."""
    original_snomed = MockValueSetSingle.SNOMEDCT.copy()

    codes = MockValueSetSingle.get_codes()
    codes.add("new_code")

    # Original ValueSet should be unchanged
    assert original_snomed == MockValueSetSingle.SNOMEDCT
    assert "new_code" not in MockValueSetSingle.SNOMEDCT


def test_get_codes_combined_valuesets() -> None:
    """Test get_codes() with combined ValueSets using the | operator."""
    combined: CombinedValueSet = MockValueSetSingle | MockValueSetMultiple
    codes = combined.get_codes()

    assert isinstance(codes, set)
    # Should have all unique codes from both ValueSets
    assert len(codes) == 7

    # From MockValueSetSingle
    assert "345678" in codes

    # From MockValueSetMultiple
    assert "E11.9" in codes
    assert "12345-6" in codes
