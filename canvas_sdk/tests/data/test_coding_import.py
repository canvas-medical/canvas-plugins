"""Tests for Coding model imports."""


def test_coding_can_be_imported_from_data_module() -> None:
    """Ensure Coding class can be imported from canvas_sdk.v1.data."""
    from canvas_sdk.v1.data import Coding

    assert Coding is not None
    assert Coding.__name__ == "Coding"


def test_coding_import_from_data_module_matches_direct_import() -> None:
    """Ensure Coding imported from data module is the same as direct import."""
    from canvas_sdk.v1.data import Coding
    from canvas_sdk.v1.data.coding import Coding as DirectCoding

    assert Coding is DirectCoding
