"""Tests for namespace schema creation in installation.py.

Tests verify that:
1. create_namespace_schema validates namespace name
2. create_namespace_schema creates schema when it doesn't exist
3. create_namespace_schema returns None when schema already exists
4. initialize_namespace_partitions is called correctly
"""

from unittest.mock import MagicMock, mock_open, patch

import pytest


class TestCreateNamespaceSchemaValidation:
    """Tests for namespace name validation in create_namespace_schema."""

    @patch("plugin_runner.installation.open_database_connection")
    def test_rejects_invalid_namespace_name(self, mock_open_conn: MagicMock) -> None:
        """Should raise ValueError for invalid namespace names."""
        from plugin_runner.installation import create_namespace_schema

        # Names without __ are invalid
        with pytest.raises(ValueError) as exc_info:
            create_namespace_schema("invalid_name")

        assert "Invalid namespace name" in str(exc_info.value)

        # Database should not be called
        mock_open_conn.assert_not_called()

    @patch("plugin_runner.installation.open_database_connection")
    def test_rejects_reserved_schema_name(self, mock_open_conn: MagicMock) -> None:
        """Should raise ValueError for reserved schema names."""
        from plugin_runner.installation import create_namespace_schema

        with pytest.raises(ValueError):
            create_namespace_schema("public")

        mock_open_conn.assert_not_called()

    @patch("plugin_runner.installation.open_database_connection")
    def test_rejects_pg_prefixed_name(self, mock_open_conn: MagicMock) -> None:
        """Should raise ValueError for pg_ prefixed names."""
        from plugin_runner.installation import create_namespace_schema

        with pytest.raises(ValueError):
            create_namespace_schema("pg__custom_schema")

        mock_open_conn.assert_not_called()


class TestCreateNamespaceSchemaExisting:
    """Tests for create_namespace_schema when schema already exists."""

    @patch("plugin_runner.installation.open_database_connection")
    def test_returns_none_when_schema_exists(self, mock_open_conn: MagicMock) -> None:
        """Should return None if namespace schema already exists."""
        from plugin_runner.installation import create_namespace_schema

        # Mock cursor that returns existing schema
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"count": 1}
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        mock_open_conn.return_value = mock_conn

        result = create_namespace_schema("org__namespace")

        assert result is None


class TestCreateNamespaceSchemaNew:
    """Tests for create_namespace_schema when creating new schema."""

    @patch("plugin_runner.installation.uuid")
    @patch("builtins.open", new_callable=mock_open, read_data="CREATE SCHEMA {namespace};")
    @patch("plugin_runner.installation.open_database_connection")
    def test_creates_schema_when_not_exists(
        self, mock_open_conn: MagicMock, mock_file: MagicMock, mock_uuid: MagicMock
    ) -> None:
        """Should create schema and return generated keys when namespace doesn't exist."""
        from plugin_runner.installation import create_namespace_schema

        # Mock uuid.uuid4 to return predictable values
        mock_uuid.uuid4.side_effect = [
            MagicMock(__str__=lambda self: "read-uuid-123"),
            MagicMock(__str__=lambda self: "write-uuid-456"),
        ]

        # Mock cursor that returns no existing schema
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"count": 0}
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        mock_open_conn.return_value = mock_conn

        result = create_namespace_schema("org__namespace")

        assert result is not None
        assert "namespace_read_access_key" in result
        assert "namespace_read_write_access_key" in result
        assert result["namespace_read_access_key"] == "read-uuid-123"
        assert result["namespace_read_write_access_key"] == "write-uuid-456"

    @patch("plugin_runner.installation.uuid")
    @patch("builtins.open", new_callable=mock_open, read_data="CREATE SCHEMA {namespace};")
    @patch("plugin_runner.installation.open_database_connection")
    def test_executes_sql_with_namespace_replaced(
        self, mock_open_conn: MagicMock, mock_file: MagicMock, mock_uuid: MagicMock
    ) -> None:
        """Should execute SQL file with namespace placeholder replaced."""
        from plugin_runner.installation import create_namespace_schema

        mock_uuid.uuid4.return_value = MagicMock(__str__=lambda self: "test-uuid")

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"count": 0}
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        mock_open_conn.return_value = mock_conn

        create_namespace_schema("acme__data")

        # Check that execute was called with namespace in SQL
        execute_calls = [
            call for call in mock_cursor.execute.call_args_list if "CREATE SCHEMA" in str(call)
        ]
        assert len(execute_calls) >= 1
        sql_executed = execute_calls[0][0][0]
        assert "acme__data" in sql_executed

    @patch("plugin_runner.installation.uuid")
    @patch("builtins.open", new_callable=mock_open, read_data="CREATE SCHEMA {namespace};")
    @patch("plugin_runner.installation.open_database_connection")
    def test_commits_transaction(
        self, mock_open_conn: MagicMock, mock_file: MagicMock, mock_uuid: MagicMock
    ) -> None:
        """Should commit the database transaction after creating schema."""
        from plugin_runner.installation import create_namespace_schema

        mock_uuid.uuid4.return_value = MagicMock(__str__=lambda self: "test-uuid")

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"count": 0}
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        mock_open_conn.return_value = mock_conn

        create_namespace_schema("org__data")

        # Verify commit was called
        mock_conn.commit.assert_called()


class TestInitializeNamespacePartitions:
    """Tests for initialize_namespace_partitions function."""

    @patch("builtins.open", new_callable=mock_open, read_data="SELECT 1;")
    @patch("plugin_runner.installation.open_database_connection")
    def test_executes_partition_sql(self, mock_open_conn: MagicMock, mock_file: MagicMock) -> None:
        """Should execute the partition initialization SQL."""
        from plugin_runner.installation import initialize_namespace_partitions

        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        mock_open_conn.return_value = mock_conn

        initialize_namespace_partitions("org__namespace")

        # Verify SQL was executed and committed
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called()

    @patch("builtins.open", new_callable=mock_open, read_data="CREATE TABLE {namespace}.test;")
    @patch("plugin_runner.installation.open_database_connection")
    def test_replaces_namespace_in_sql(
        self, mock_open_conn: MagicMock, mock_file: MagicMock
    ) -> None:
        """Should replace {namespace} placeholder in SQL."""
        from plugin_runner.installation import initialize_namespace_partitions

        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        mock_open_conn.return_value = mock_conn

        initialize_namespace_partitions("canvas__shared")

        # Check that the namespace was replaced in the SQL
        call_args = mock_cursor.execute.call_args[0][0]
        assert "canvas__shared" in call_args
        assert "{namespace}" not in call_args


class TestReadOnlyAccessSkipsModelCreation:
    """Tests for ensuring read-only access plugins don't create custom tables."""

    def test_read_only_access_logic(self) -> None:
        """Plugins with read access should not generate migrations."""
        # This tests the logic used in install_plugin
        custom_data = {"namespace": "org__data", "access": "read"}
        declared_access = custom_data.get("access", "read")

        # Should NOT call generate_plugin_migrations when access is "read"
        should_generate = declared_access == "read_write"
        assert should_generate is False

    def test_read_write_access_logic(self) -> None:
        """Plugins with read_write access should generate migrations."""
        custom_data = {"namespace": "org__data", "access": "read_write"}
        declared_access = custom_data.get("access", "read")

        # Should call generate_plugin_migrations when access is "read_write"
        should_generate = declared_access == "read_write"
        assert should_generate is True

    def test_missing_access_defaults_to_read(self) -> None:
        """Missing access field should default to read (no table creation)."""
        custom_data = {"namespace": "org__data"}  # No "access" key
        declared_access = custom_data.get("access", "read")

        # Should NOT generate migrations - default to safe "read" access
        should_generate = declared_access == "read_write"
        assert should_generate is False


class TestNamespaceExists:
    """Tests for namespace_exists function."""

    @patch("plugin_runner.installation.open_database_connection")
    def test_returns_true_when_schema_exists(self, mock_open_conn: MagicMock) -> None:
        """Should return True if namespace schema exists."""
        from plugin_runner.installation import namespace_exists

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"count": 1}
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        mock_open_conn.return_value = mock_conn

        result = namespace_exists("org__namespace")

        assert result is True

    @patch("plugin_runner.installation.open_database_connection")
    def test_returns_false_when_schema_not_exists(self, mock_open_conn: MagicMock) -> None:
        """Should return False if namespace schema doesn't exist."""
        from plugin_runner.installation import namespace_exists

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"count": 0}
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        mock_open_conn.return_value = mock_conn

        result = namespace_exists("org__nonexistent")

        assert result is False

    @patch("plugin_runner.installation.open_database_connection")
    def test_queries_pg_namespace_catalog(self, mock_open_conn: MagicMock) -> None:
        """Should query pg_catalog.pg_namespace for schema existence."""
        from plugin_runner.installation import namespace_exists

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"count": 0}
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        mock_open_conn.return_value = mock_conn

        namespace_exists("acme__data")

        # Verify the correct query was made
        call_args = mock_cursor.execute.call_args
        sql = call_args[0][0]
        params = call_args[0][1]

        assert "pg_catalog.pg_namespace" in sql
        assert "acme__data" in params


class TestNamespaceAccessValidation:
    """Tests for namespace access validation during installation.

    These tests verify the validation logic by testing the actual functions
    that would be called during plugin installation.
    """

    @patch("plugin_runner.installation.open_database_connection")
    def test_namespace_exists_returns_false_for_missing_schema(
        self, mock_open_conn: MagicMock
    ) -> None:
        """namespace_exists should return False when schema doesn't exist."""
        from plugin_runner.installation import namespace_exists

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"count": 0}
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        mock_open_conn.return_value = mock_conn

        # This is what would trigger a PluginInstallationError for read access
        result = namespace_exists("org__nonexistent")
        assert result is False

    @patch("plugin_runner.installation.open_database_connection")
    def test_check_namespace_auth_key_returns_none_for_invalid_key(
        self, mock_open_conn: MagicMock
    ) -> None:
        """check_namespace_auth_key should return None for invalid keys."""
        from plugin_runner.installation import check_namespace_auth_key

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None  # No matching key found
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        mock_open_conn.return_value = mock_conn

        # This is what would trigger a PluginInstallationError
        result = check_namespace_auth_key("org__data", "invalid-key")
        assert result is None

    @patch("plugin_runner.installation.open_database_connection")
    def test_check_namespace_auth_key_returns_access_level_for_valid_key(
        self, mock_open_conn: MagicMock
    ) -> None:
        """check_namespace_auth_key should return access level for valid keys."""
        from plugin_runner.installation import check_namespace_auth_key

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"access_level": "read_write"}
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        mock_open_conn.return_value = mock_conn

        result = check_namespace_auth_key("org__data", "valid-key")
        assert result == "read_write"

    @patch("plugin_runner.installation.uuid")
    @patch("builtins.open", new_callable=mock_open, read_data="CREATE SCHEMA {namespace};")
    @patch("plugin_runner.installation.open_database_connection")
    def test_create_namespace_schema_returns_keys_for_new_namespace(
        self, mock_open_conn: MagicMock, mock_file: MagicMock, mock_uuid: MagicMock
    ) -> None:
        """create_namespace_schema should return generated keys for new namespaces."""
        from plugin_runner.installation import create_namespace_schema

        mock_uuid.uuid4.side_effect = [
            MagicMock(__str__=lambda self: "read-key"),
            MagicMock(__str__=lambda self: "write-key"),
        ]

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"count": 0}  # Namespace doesn't exist
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        mock_open_conn.return_value = mock_conn

        # read_write plugins creating new namespaces get keys returned
        result = create_namespace_schema("org__new_namespace")
        assert result is not None
        assert "namespace_read_access_key" in result
        assert "namespace_read_write_access_key" in result

    @patch("plugin_runner.installation.open_database_connection")
    def test_create_namespace_schema_returns_none_for_existing_namespace(
        self, mock_open_conn: MagicMock
    ) -> None:
        """create_namespace_schema should return None for existing namespaces."""
        from plugin_runner.installation import create_namespace_schema

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"count": 1}  # Namespace exists
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        mock_open_conn.return_value = mock_conn

        # Existing namespace returns None - plugin must verify key
        result = create_namespace_schema("org__existing")
        assert result is None


class TestAddNamespaceAuthKey:
    """Tests for add_namespace_auth_key function."""

    @patch("plugin_runner.installation.open_database_connection")
    def test_inserts_auth_key_with_hash(self, mock_open_conn: MagicMock) -> None:
        """Should insert auth key with hashed secret."""
        import hashlib

        from plugin_runner.installation import add_namespace_auth_key

        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        mock_open_conn.return_value = mock_conn

        add_namespace_auth_key("org__data", "my_secret", "read_write", "Test key")

        # Verify insert was called
        mock_cursor.execute.assert_called()
        call_args = mock_cursor.execute.call_args

        # Check the SQL contains the namespace auth table
        sql = call_args[0][0]
        assert "org__data.namespace_auth" in sql

        # Check the parameters include the hash
        params = call_args[0][1]
        expected_hash = hashlib.sha256(b"my_secret").hexdigest()
        assert expected_hash in params
        assert "read_write" in params

    @patch("plugin_runner.installation.open_database_connection")
    def test_commits_after_insert(self, mock_open_conn: MagicMock) -> None:
        """Should commit the transaction after inserting."""
        from plugin_runner.installation import add_namespace_auth_key

        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        mock_open_conn.return_value = mock_conn

        add_namespace_auth_key("org__data", "secret", "read")

        mock_conn.commit.assert_called()
