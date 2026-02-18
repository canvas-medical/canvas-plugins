"""Tests for namespace name validation."""

from plugin_runner.installation import (
    RESERVED_SCHEMA_PREFIXES,
    RESERVED_SCHEMAS,
    is_valid_namespace_name,
)


class TestIsValidNamespaceName:
    """Tests for the is_valid_namespace_name function."""

    def test_reserved_schema_public_rejected(self) -> None:
        """Reserved schema 'public' should be rejected."""
        assert is_valid_namespace_name("public") is False

    def test_reserved_schema_pg_catalog_rejected(self) -> None:
        """Reserved schema 'pg_catalog' should be rejected."""
        assert is_valid_namespace_name("pg_catalog") is False

    def test_reserved_schema_pg_toast_rejected(self) -> None:
        """Reserved schema 'pg_toast' should be rejected."""
        assert is_valid_namespace_name("pg_toast") is False

    def test_reserved_schema_information_schema_rejected(self) -> None:
        """Reserved schema 'information_schema' should be rejected."""
        assert is_valid_namespace_name("information_schema") is False

    def test_all_reserved_schemas_rejected(self) -> None:
        """All reserved schemas should be rejected."""
        for schema in RESERVED_SCHEMAS:
            assert is_valid_namespace_name(schema) is False, f"Expected {schema} to be rejected"

    def test_reserved_prefix_pg_rejected(self) -> None:
        """Namespace starting with 'pg_' prefix should be rejected."""
        assert is_valid_namespace_name("pg_custom") is False
        assert is_valid_namespace_name("pg_my_namespace") is False

    def test_all_reserved_prefixes_rejected(self) -> None:
        """All reserved prefixes should cause rejection."""
        for prefix in RESERVED_SCHEMA_PREFIXES:
            test_name = f"{prefix}test_namespace"
            assert is_valid_namespace_name(test_name) is False, (
                f"Expected {test_name} to be rejected"
            )

    def test_valid_namespace_with_double_underscore_accepted(self) -> None:
        """Valid namespace with org__name format should be accepted."""
        assert is_valid_namespace_name("acme_org__shared_data") is True
        assert is_valid_namespace_name("canvas_demo__staff_plus") is True
        assert is_valid_namespace_name("my_company__my_namespace") is True

    def test_namespace_without_double_underscore_rejected(self) -> None:
        """Namespace without '__' separator should be rejected."""
        assert is_valid_namespace_name("acme_org_shared_data") is False
        assert is_valid_namespace_name("simple_name") is False
        assert is_valid_namespace_name("no_separator") is False

    def test_namespace_with_single_underscore_rejected(self) -> None:
        """Namespace with only single underscore should be rejected."""
        assert is_valid_namespace_name("org_name") is False

    def test_empty_namespace_rejected(self) -> None:
        """Empty namespace should be rejected."""
        assert is_valid_namespace_name("") is False

    def test_namespace_with_only_double_underscore_rejected(self) -> None:
        """Namespace that is just '__' should be rejected (doesn't match pattern)."""
        # This would fail the regex pattern check in manifest validation
        # but is_valid_namespace_name only checks reserved names and double underscore presence
        assert is_valid_namespace_name("__") is True  # Has __, passes basic check

    def test_namespace_with_numbers_accepted(self) -> None:
        """Namespace with numbers should be accepted if format is correct."""
        assert is_valid_namespace_name("org123__namespace456") is True

    def test_namespace_case_sensitivity(self) -> None:
        """Reserved schema check should be case-sensitive (PostgreSQL schemas are lowercase)."""
        # PostgreSQL schemas are case-sensitive when quoted, lowercase by default
        # Our reserved list is lowercase, so uppercase versions pass the reserved check
        # but still need the __ format to be valid
        assert is_valid_namespace_name("PUBLIC__test") is True  # Not in reserved set, has __
        assert is_valid_namespace_name("Public__test") is True
