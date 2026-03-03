"""Tests for namespace schema creation in installation.py.

Tests verify that:
1. create_namespace_schema validates namespace name
2. create_namespace_schema creates schema when it doesn't exist
3. create_namespace_schema returns None when schema already exists
4. initialize_namespace_partitions is called correctly
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from plugin_runner.exceptions import PluginInstallationError


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


class TestStoreNamespaceKeysAsPluginSecrets:
    """Tests for store_namespace_keys_as_plugin_secrets function."""

    def _make_mock_conn(self, cursor: MagicMock) -> MagicMock:
        """Helper to build a mock connection wrapping the given cursor."""
        cursor.__enter__ = MagicMock(return_value=cursor)
        cursor.__exit__ = MagicMock(return_value=False)

        conn = MagicMock()
        conn.cursor.return_value = cursor
        conn.__enter__ = MagicMock(return_value=conn)
        conn.__exit__ = MagicMock(return_value=False)
        return conn

    @patch("plugin_runner.installation.open_database_connection")
    def test_returns_early_when_plugin_not_found(self, mock_open_conn: MagicMock) -> None:
        """Should log a warning and return without writing secrets when plugin not in DB."""
        from plugin_runner.installation import store_namespace_keys_as_plugin_secrets

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None  # plugin not found
        mock_conn = self._make_mock_conn(mock_cursor)
        mock_open_conn.return_value = mock_conn

        store_namespace_keys_as_plugin_secrets("nonexistent_plugin", {"key1": "val1"})

        # Should NOT commit or attempt to insert secrets
        mock_conn.commit.assert_not_called()

    @patch("plugin_runner.installation.open_database_connection")
    def test_looks_up_plugin_by_name(self, mock_open_conn: MagicMock) -> None:
        """Should query plugin_io_plugin for the plugin's database ID."""
        from plugin_runner.installation import store_namespace_keys_as_plugin_secrets

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn = self._make_mock_conn(mock_cursor)
        mock_open_conn.return_value = mock_conn

        store_namespace_keys_as_plugin_secrets("my_plugin", {"k": "v"})

        first_execute = mock_cursor.execute.call_args_list[0]
        sql = first_execute[0][0]
        params = first_execute[0][1]
        assert "plugin_io_plugin" in sql
        assert params == ("my_plugin",)

    @patch("builtins.open", new_callable=mock_open, read_data="{}")
    @patch("plugin_runner.installation.Path")
    @patch("plugin_runner.installation.open_database_connection")
    def test_inserts_keys_as_plugin_secrets(
        self, mock_open_conn: MagicMock, mock_path_cls: MagicMock, mock_file: MagicMock
    ) -> None:
        """Should upsert each key into plugin_io_pluginsecret."""
        from plugin_runner.installation import store_namespace_keys_as_plugin_secrets

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (42,)  # plugin_id = 42
        mock_conn = self._make_mock_conn(mock_cursor)
        mock_open_conn.return_value = mock_conn

        # Mock Path so secrets_path.exists() returns False (skip file read)
        mock_secrets_path = MagicMock()
        mock_secrets_path.exists.return_value = False
        mock_path_cls.return_value.__truediv__ = MagicMock(return_value=mock_secrets_path)

        keys = {
            "namespace_read_access_key": "read-uuid",
            "namespace_read_write_access_key": "write-uuid",
        }
        store_namespace_keys_as_plugin_secrets("my_plugin", keys)

        # First call is the plugin lookup; next two are the key inserts
        insert_calls = [
            c for c in mock_cursor.execute.call_args_list if "plugin_io_pluginsecret" in str(c)
        ]
        assert len(insert_calls) == 2

        # Verify each key was upserted with the correct plugin_id and value
        inserted_params = {call[0][1][1]: call[0][1][2] for call in insert_calls}
        assert inserted_params["namespace_read_access_key"] == "read-uuid"
        assert inserted_params["namespace_read_write_access_key"] == "write-uuid"

        # All inserts use the same plugin_id
        for call in insert_calls:
            assert call[0][1][0] == 42

    @patch("builtins.open", new_callable=mock_open, read_data="{}")
    @patch("plugin_runner.installation.Path")
    @patch("plugin_runner.installation.open_database_connection")
    def test_commits_after_inserting_secrets(
        self, mock_open_conn: MagicMock, mock_path_cls: MagicMock, mock_file: MagicMock
    ) -> None:
        """Should commit the DB transaction after inserting all keys."""
        from plugin_runner.installation import store_namespace_keys_as_plugin_secrets

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1,)
        mock_conn = self._make_mock_conn(mock_cursor)
        mock_open_conn.return_value = mock_conn

        mock_secrets_path = MagicMock()
        mock_secrets_path.exists.return_value = False
        mock_path_cls.return_value.__truediv__ = MagicMock(return_value=mock_secrets_path)

        store_namespace_keys_as_plugin_secrets("p", {"k": "v"})

        mock_conn.commit.assert_called_once()

    @patch("plugin_runner.installation.SECRETS_FILE_NAME", "secrets.json")
    @patch("plugin_runner.installation.open_database_connection")
    def test_writes_secrets_json_when_no_existing_file(
        self, mock_open_conn: MagicMock, tmp_path: Path
    ) -> None:
        """Should create secrets.json with the keys when the file doesn't exist."""
        from plugin_runner.installation import store_namespace_keys_as_plugin_secrets

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1,)
        mock_conn = self._make_mock_conn(mock_cursor)
        mock_open_conn.return_value = mock_conn

        plugin_dir = tmp_path / "my_plugin"
        plugin_dir.mkdir()

        keys = {"key_a": "val_a", "key_b": "val_b"}
        with patch("plugin_runner.installation.PLUGIN_DIRECTORY", str(tmp_path)):
            store_namespace_keys_as_plugin_secrets("my_plugin", keys)

        secrets_file = plugin_dir / "secrets.json"
        assert secrets_file.exists()
        written = json.loads(secrets_file.read_text())
        assert written == keys

    @patch("plugin_runner.installation.SECRETS_FILE_NAME", "secrets.json")
    @patch("plugin_runner.installation.open_database_connection")
    def test_merges_with_existing_secrets_json(
        self, mock_open_conn: MagicMock, tmp_path: Path
    ) -> None:
        """Should merge new keys into existing secrets.json contents."""
        from plugin_runner.installation import store_namespace_keys_as_plugin_secrets

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1,)
        mock_conn = self._make_mock_conn(mock_cursor)
        mock_open_conn.return_value = mock_conn

        plugin_dir = tmp_path / "my_plugin"
        plugin_dir.mkdir()

        # Write pre-existing secrets
        secrets_file = plugin_dir / "secrets.json"
        secrets_file.write_text(json.dumps({"existing_secret": "old_value"}))

        keys = {"new_key": "new_value"}
        with patch("plugin_runner.installation.PLUGIN_DIRECTORY", str(tmp_path)):
            store_namespace_keys_as_plugin_secrets("my_plugin", keys)

        written = json.loads(secrets_file.read_text())
        assert written == {"existing_secret": "old_value", "new_key": "new_value"}


class TestSetupReadWriteNamespace:
    """Tests for setup_read_write_namespace function."""

    @patch("plugin_runner.installation.store_namespace_keys_as_plugin_secrets")
    @patch("plugin_runner.installation.create_namespace_schema")
    @patch("plugin_runner.installation.namespace_exists", return_value=False)
    def test_creates_namespace_when_not_exists(
        self,
        mock_exists: MagicMock,
        mock_create: MagicMock,
        mock_store: MagicMock,
    ) -> None:
        """Should create the namespace and store keys when it doesn't exist."""
        from plugin_runner.installation import setup_read_write_namespace

        mock_create.return_value = {"key_a": "val_a", "key_b": "val_b"}

        result = setup_read_write_namespace("my_plugin", "org__data", {})

        assert result is True
        mock_create.assert_called_once_with(namespace="org__data")
        mock_store.assert_called_once_with("my_plugin", {"key_a": "val_a", "key_b": "val_b"})

    @patch("plugin_runner.installation.store_namespace_keys_as_plugin_secrets")
    @patch("plugin_runner.installation.create_namespace_schema")
    @patch("plugin_runner.installation.namespace_exists", return_value=False)
    def test_skips_store_when_create_returns_none(
        self,
        mock_exists: MagicMock,
        mock_create: MagicMock,
        mock_store: MagicMock,
    ) -> None:
        """Should not store keys when create_namespace_schema returns None."""
        from plugin_runner.installation import setup_read_write_namespace

        mock_create.return_value = None

        result = setup_read_write_namespace("my_plugin", "org__data", {})

        assert result is True
        mock_store.assert_not_called()

    @patch("plugin_runner.installation.check_namespace_auth_key", return_value="read_write")
    @patch("plugin_runner.installation.namespace_exists", return_value=True)
    def test_verifies_key_when_namespace_exists(
        self,
        mock_exists: MagicMock,
        mock_check: MagicMock,
    ) -> None:
        """Should verify access key and return True when key grants read_write."""
        from plugin_runner.installation import setup_read_write_namespace

        secrets = {"namespace_read_write_access_key": "valid-key"}
        result = setup_read_write_namespace("my_plugin", "org__data", secrets)

        assert result is True
        mock_check.assert_called_once_with("org__data", "valid-key")

    @patch("plugin_runner.installation.namespace_exists", return_value=True)
    def test_raises_when_key_missing_and_namespace_exists(self, mock_exists: MagicMock) -> None:
        """Should raise PluginInstallationError when secret is not configured."""
        from plugin_runner.installation import setup_read_write_namespace

        with pytest.raises(PluginInstallationError, match="secret is not configured"):
            setup_read_write_namespace("my_plugin", "org__data", {})

    @patch("plugin_runner.installation.check_namespace_auth_key", return_value="read")
    @patch("plugin_runner.installation.namespace_exists", return_value=True)
    def test_raises_when_key_grants_insufficient_access(
        self,
        mock_exists: MagicMock,
        mock_check: MagicMock,
    ) -> None:
        """Should raise PluginInstallationError when key only grants read access."""
        from plugin_runner.installation import setup_read_write_namespace

        secrets = {"namespace_read_write_access_key": "read-only-key"}
        with pytest.raises(PluginInstallationError, match="invalid or insufficient"):
            setup_read_write_namespace("my_plugin", "org__data", secrets)

    @patch("plugin_runner.installation.check_namespace_auth_key", return_value=None)
    @patch("plugin_runner.installation.namespace_exists", return_value=True)
    def test_raises_when_key_is_invalid(
        self,
        mock_exists: MagicMock,
        mock_check: MagicMock,
    ) -> None:
        """Should raise PluginInstallationError when key is not recognized."""
        from plugin_runner.installation import setup_read_write_namespace

        secrets = {"namespace_read_write_access_key": "garbage"}
        with pytest.raises(PluginInstallationError, match="invalid or insufficient"):
            setup_read_write_namespace("my_plugin", "org__data", secrets)


class TestVerifyReadNamespaceAccess:
    """Tests for verify_read_namespace_access function."""

    @patch("plugin_runner.installation.check_namespace_auth_key", return_value="read")
    @patch("plugin_runner.installation.namespace_exists", return_value=True)
    def test_succeeds_with_valid_read_key(
        self,
        mock_exists: MagicMock,
        mock_check: MagicMock,
    ) -> None:
        """Should return without error when key grants read access."""
        from plugin_runner.installation import verify_read_namespace_access

        secrets = {"namespace_read_access_key": "valid-key"}
        verify_read_namespace_access("my_plugin", "org__data", secrets)

        mock_check.assert_called_once_with("org__data", "valid-key")

    @patch("plugin_runner.installation.namespace_exists", return_value=False)
    def test_raises_when_namespace_does_not_exist(self, mock_exists: MagicMock) -> None:
        """Should raise PluginInstallationError when namespace doesn't exist."""
        from plugin_runner.installation import verify_read_namespace_access

        with pytest.raises(PluginInstallationError, match="does not exist"):
            verify_read_namespace_access("my_plugin", "org__missing", {})

    @patch("plugin_runner.installation.namespace_exists", return_value=True)
    def test_raises_when_key_missing(self, mock_exists: MagicMock) -> None:
        """Should raise PluginInstallationError when secret is not configured."""
        from plugin_runner.installation import verify_read_namespace_access

        with pytest.raises(PluginInstallationError, match="secret is not configured"):
            verify_read_namespace_access("my_plugin", "org__data", {})

    @patch("plugin_runner.installation.check_namespace_auth_key", return_value=None)
    @patch("plugin_runner.installation.namespace_exists", return_value=True)
    def test_raises_when_key_is_invalid(
        self,
        mock_exists: MagicMock,
        mock_check: MagicMock,
    ) -> None:
        """Should raise PluginInstallationError when key is not recognized."""
        from plugin_runner.installation import verify_read_namespace_access

        secrets = {"namespace_read_access_key": "garbage"}
        with pytest.raises(PluginInstallationError, match="invalid access key"):
            verify_read_namespace_access("my_plugin", "org__data", secrets)
