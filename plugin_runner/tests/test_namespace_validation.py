"""Tests for namespace name validation."""

from plugin_runner.installation import (
    NAMESPACE_PATTERN,
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

    def test_reserved_prefix_pg_rejected(self) -> None:
        """Namespace starting with 'pg_' prefix should be rejected."""
        assert is_valid_namespace_name("pg_custom") is False
        assert is_valid_namespace_name("pg_my_namespace") is False

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
        """Namespace that is just '__' should be rejected."""
        assert is_valid_namespace_name("__") is False

    def test_namespace_with_numbers_accepted(self) -> None:
        """Namespace with numbers should be accepted if format is correct."""
        assert is_valid_namespace_name("org123__namespace456") is True

    def test_uppercase_rejected(self) -> None:
        """Namespaces with uppercase letters should be rejected."""
        assert is_valid_namespace_name("PUBLIC__test") is False
        assert is_valid_namespace_name("Public__test") is False
        assert is_valid_namespace_name("org__Test") is False

    def test_must_start_with_letter(self) -> None:
        """Both sides of the namespace must start with a lowercase letter."""
        assert is_valid_namespace_name("1org__name") is False
        assert is_valid_namespace_name("org__1name") is False
        assert is_valid_namespace_name("_org__name") is False

    def test_no_special_characters(self) -> None:
        """Namespaces should not contain special characters."""
        assert is_valid_namespace_name("org-name__data") is False
        assert is_valid_namespace_name("org__data-set") is False
        assert is_valid_namespace_name("org.name__data") is False

    def test_pattern_matches_manifest_schema(self) -> None:
        """NAMESPACE_PATTERN should match the manifest JSON Schema pattern."""
        assert NAMESPACE_PATTERN.pattern == r"^[a-z][a-z0-9_]*__[a-z][a-z0-9_]*$"
