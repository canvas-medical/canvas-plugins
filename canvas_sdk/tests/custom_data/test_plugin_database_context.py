"""Tests for plugin_database_context thread safety.

Tests verify that:
1. get_current_plugin returns the correct plugin name for each thread
2. The thread-local storage works correctly for concurrent threads
3. The context manager properly manages plugin state
4. Search_path operations work on PostgreSQL (skipped on SQLite)
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import MagicMock, patch

import pytest
from django.db import connection

from canvas_sdk.v1.plugin_database_context import (
    clear_current_plugin,
    get_current_plugin,
    plugin_database_context,
    set_current_plugin,
)

# Check if we're using SQLite (search_path is PostgreSQL-specific)
IS_SQLITE = connection.vendor == "sqlite"


class TestPluginContextThreadLocal:
    """Tests for thread-local plugin context storage."""

    def test_set_and_get_current_plugin(self):
        """Basic set/get should work in single thread."""
        clear_current_plugin()

        set_current_plugin("my_plugin")
        assert get_current_plugin() == "my_plugin"

        clear_current_plugin()
        assert get_current_plugin() is None

    def test_clear_current_plugin(self):
        """Clear should remove the plugin name."""
        set_current_plugin("test_plugin")
        assert get_current_plugin() == "test_plugin"

        clear_current_plugin()
        assert get_current_plugin() is None

    def test_get_returns_none_when_not_set(self):
        """get_current_plugin should return None when no plugin is set."""
        clear_current_plugin()
        assert get_current_plugin() is None

    def test_overwrite_plugin_name(self):
        """Setting a new plugin name should overwrite the old one."""
        set_current_plugin("plugin_a")
        assert get_current_plugin() == "plugin_a"

        set_current_plugin("plugin_b")
        assert get_current_plugin() == "plugin_b"

        clear_current_plugin()


class TestPluginContextThreadIsolation:
    """Tests for thread isolation of plugin context."""

    def test_threads_have_isolated_contexts(self):
        """Each thread should have its own plugin context."""
        results = {}
        errors = []

        def thread_func(plugin_name, thread_id):
            try:
                set_current_plugin(plugin_name)
                # Small delay to allow other threads to run
                time.sleep(0.01)
                # Verify our plugin name is still correct
                actual = get_current_plugin()
                results[thread_id] = {
                    "expected": plugin_name,
                    "actual": actual,
                }
            except Exception as e:
                errors.append((thread_id, str(e)))
            finally:
                clear_current_plugin()

        threads = []
        for i in range(10):
            plugin_name = f"plugin_{i}"
            t = threading.Thread(target=thread_func, args=(plugin_name, i))
            threads.append(t)

        # Start all threads
        for t in threads:
            t.start()

        # Wait for all threads to complete
        for t in threads:
            t.join()

        # Verify no errors
        assert len(errors) == 0, f"Thread errors: {errors}"

        # Verify each thread saw its own plugin name
        for thread_id, result in results.items():
            assert result["actual"] == result["expected"], (
                f"Thread {thread_id}: expected {result['expected']}, got {result['actual']}"
            )

    def test_concurrent_threads_with_executor(self):
        """Test with ThreadPoolExecutor for more realistic concurrency."""
        num_threads = 20
        results = {}

        def worker(plugin_name):
            set_current_plugin(plugin_name)
            time.sleep(0.005)  # Simulate some work
            result = get_current_plugin()
            clear_current_plugin()
            return plugin_name, result

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = {
                executor.submit(worker, f"plugin_{i}"): i for i in range(num_threads)
            }

            for future in as_completed(futures):
                expected, actual = future.result()
                results[expected] = actual

        # Verify all results
        for expected, actual in results.items():
            assert actual == expected, f"Expected {expected}, got {actual}"

    def test_rapid_context_switching(self):
        """Test rapid setting and clearing of plugin context."""
        num_threads = 10
        iterations = 100
        errors = []

        def worker(thread_id):
            for i in range(iterations):
                plugin_name = f"rapid_{thread_id}_{i}"
                set_current_plugin(plugin_name)
                actual = get_current_plugin()
                if actual != plugin_name:
                    errors.append(
                        f"Thread {thread_id}, iter {i}: expected {plugin_name}, got {actual}"
                    )
                clear_current_plugin()

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(num_threads)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Errors: {errors[:10]}"


class TestPluginDatabaseContextManagerMocked:
    """Tests for plugin_database_context with mocked database operations.

    These tests verify the context manager's logic without requiring PostgreSQL.
    """

    def test_context_sets_and_clears_plugin_name(self):
        """Context manager should set and clear the plugin name."""
        clear_current_plugin()
        assert get_current_plugin() is None

        # Patch at django.db level since connection is imported locally in the function
        with patch("django.db.connection") as mock_conn:
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
            mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

            with plugin_database_context("test_plugin"):
                assert get_current_plugin() == "test_plugin"

        # After context, should be cleared
        assert get_current_plugin() is None

    def test_context_restores_previous_plugin(self):
        """Nested contexts should restore the previous plugin."""
        with patch("django.db.connection") as mock_conn:
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
            mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

            with plugin_database_context("outer_plugin"):
                assert get_current_plugin() == "outer_plugin"

                with plugin_database_context("inner_plugin"):
                    assert get_current_plugin() == "inner_plugin"

                # Should be restored to outer
                assert get_current_plugin() == "outer_plugin"

        assert get_current_plugin() is None

    def test_context_clears_on_exception(self):
        """Context should clean up even if exception is raised."""
        clear_current_plugin()

        with patch("django.db.connection") as mock_conn:
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
            mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

            try:
                with plugin_database_context("test_plugin"):
                    assert get_current_plugin() == "test_plugin"
                    raise ValueError("Test exception")
            except ValueError:
                pass

        # Should still be cleared after exception
        assert get_current_plugin() is None

    def test_search_path_sql_is_executed(self):
        """Verify that SET search_path SQL is executed."""
        with patch("django.db.connection") as mock_conn:
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
            mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

            with plugin_database_context("my_plugin"):
                pass

            # Check that execute was called with SET search_path
            calls = mock_cursor.execute.call_args_list
            assert len(calls) >= 1

            # First call should set search_path to the plugin
            first_call = calls[0]
            assert "SET search_path" in first_call[0][0]
            assert "my_plugin" in first_call[0][1]

    def test_search_path_restored_to_public(self):
        """Verify search_path is restored to public after context."""
        with patch("django.db.connection") as mock_conn:
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
            mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

            with plugin_database_context("temp_plugin"):
                pass

            # Last call should reset to public
            calls = mock_cursor.execute.call_args_list
            last_call = calls[-1]
            assert "SET search_path" in last_call[0][0]
            assert "public" in last_call[0][0]


class TestPluginDatabaseContextThreadSafetyMocked:
    """Tests for thread-safe context operations with mocked database.

    These tests verify that multiple threads can simultaneously use
    plugin_database_context and each thread maintains its own plugin state.
    """

    def test_parallel_threads_have_correct_plugin_context(self):
        """Multiple threads should each have their own plugin context."""
        num_threads = 10
        results = {}
        errors = []
        barrier = threading.Barrier(num_threads)

        def worker(thread_id, plugin_name):
            try:
                barrier.wait()

                with patch("django.db.connection") as mock_conn:
                    mock_cursor = MagicMock()
                    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
                    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

                    with plugin_database_context(plugin_name):
                        time.sleep(0.01)
                        actual_plugin = get_current_plugin()

                        results[thread_id] = {
                            "plugin_name": plugin_name,
                            "actual_plugin": actual_plugin,
                            "plugin_match": actual_plugin == plugin_name,
                        }
            except Exception as e:
                errors.append((thread_id, str(e)))

        threads = []
        for i in range(num_threads):
            plugin_name = f"thread_plugin_{i}"
            t = threading.Thread(target=worker, args=(i, plugin_name))
            threads.append(t)

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        assert len(errors) == 0, f"Thread errors: {errors}"

        for thread_id, result in results.items():
            assert result["plugin_match"], (
                f"Thread {thread_id}: expected {result['plugin_name']}, "
                f"got {result['actual_plugin']}"
            )

    def test_high_concurrency_stress_test(self):
        """Stress test with many threads and iterations."""
        num_threads = 20
        iterations_per_thread = 10
        results = []
        errors = []
        lock = threading.Lock()

        def worker(thread_id):
            for iteration in range(iterations_per_thread):
                plugin_name = f"stress_plugin_{thread_id}_{iteration}"
                try:
                    with patch("django.db.connection") as mock_conn:
                        mock_cursor = MagicMock()
                        mock_conn.cursor.return_value.__enter__ = MagicMock(
                            return_value=mock_cursor
                        )
                        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

                        with plugin_database_context(plugin_name):
                            actual = get_current_plugin()
                            success = actual == plugin_name

                            with lock:
                                results.append({
                                    "thread_id": thread_id,
                                    "iteration": iteration,
                                    "expected": plugin_name,
                                    "actual": actual,
                                    "success": success,
                                })

                            if not success:
                                with lock:
                                    errors.append(
                                        f"Thread {thread_id}, iter {iteration}: "
                                        f"expected {plugin_name}, got {actual}"
                                    )
                except Exception as e:
                    with lock:
                        errors.append(f"Thread {thread_id}, iter {iteration}: {e}")

        threads = []
        for i in range(num_threads):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        total_ops = num_threads * iterations_per_thread
        successful = sum(1 for r in results if r["success"])

        assert len(errors) == 0, f"Errors encountered: {errors[:10]}..."
        assert successful == total_ops, f"Only {successful}/{total_ops} operations succeeded"

    def test_nested_contexts_in_parallel_threads(self):
        """Test nested contexts work correctly in parallel."""
        num_threads = 5
        results = {}
        errors = []
        barrier = threading.Barrier(num_threads)

        def worker(thread_id):
            outer_plugin = f"outer_{thread_id}"
            inner_plugin = f"inner_{thread_id}"

            try:
                barrier.wait()

                with patch("django.db.connection") as mock_conn:
                    mock_cursor = MagicMock()
                    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
                    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

                    with plugin_database_context(outer_plugin):
                        outer_check = get_current_plugin()

                        with plugin_database_context(inner_plugin):
                            inner_check = get_current_plugin()

                        restored_check = get_current_plugin()

                    after_check = get_current_plugin()

                results[thread_id] = {
                    "outer_expected": outer_plugin,
                    "outer_actual": outer_check,
                    "inner_expected": inner_plugin,
                    "inner_actual": inner_check,
                    "restored_expected": outer_plugin,
                    "restored_actual": restored_check,
                    "after_expected": None,
                    "after_actual": after_check,
                }
            except Exception as e:
                errors.append((thread_id, str(e)))

        threads = []
        for i in range(num_threads):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        assert len(errors) == 0, f"Thread errors: {errors}"

        for thread_id, result in results.items():
            assert result["outer_actual"] == result["outer_expected"], (
                f"Thread {thread_id}: outer plugin mismatch"
            )
            assert result["inner_actual"] == result["inner_expected"], (
                f"Thread {thread_id}: inner plugin mismatch"
            )
            assert result["restored_actual"] == result["restored_expected"], (
                f"Thread {thread_id}: restored plugin mismatch"
            )
            assert result["after_actual"] == result["after_expected"], (
                f"Thread {thread_id}: after context should be None"
            )


class TestConfigurableThreadCount:
    """Tests with configurable thread counts for flexibility."""

    @pytest.mark.parametrize("num_threads", [1, 5, 10, 25, 50])
    def test_variable_thread_count(self, num_threads):
        """Test thread isolation with various thread counts."""
        results = {}
        barrier = threading.Barrier(num_threads)

        def worker(thread_id, plugin_name):
            barrier.wait()
            set_current_plugin(plugin_name)
            time.sleep(0.005)
            result = get_current_plugin()
            clear_current_plugin()
            return thread_id, plugin_name, result

        threads = []

        def run_and_store(thread_id, plugin_name):
            tid, expected, actual = worker(thread_id, plugin_name)
            results[tid] = (expected, actual)

        for i in range(num_threads):
            t = threading.Thread(target=run_and_store, args=(i, f"var_plugin_{i}"))
            threads.append(t)

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # Verify all results
        assert len(results) == num_threads
        for thread_id, (expected, actual) in results.items():
            assert actual == expected, f"Thread {thread_id}: expected {expected}, got {actual}"

    @pytest.mark.parametrize("num_threads", [2, 5, 10])
    def test_variable_thread_count_with_context_manager(self, num_threads):
        """Test context manager with various thread counts (mocked)."""
        results = {}
        errors = []
        barrier = threading.Barrier(num_threads)

        def worker(thread_id, plugin_name):
            try:
                barrier.wait()
                with patch("django.db.connection") as mock_conn:
                    mock_cursor = MagicMock()
                    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
                    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

                    with plugin_database_context(plugin_name):
                        time.sleep(0.01)
                        actual = get_current_plugin()
                        results[thread_id] = (plugin_name, actual)
            except Exception as e:
                errors.append((thread_id, str(e)))

        threads = []
        for i in range(num_threads):
            t = threading.Thread(target=worker, args=(i, f"ctx_plugin_{i}"))
            threads.append(t)

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        assert len(errors) == 0, f"Errors: {errors}"
        assert len(results) == num_threads

        for thread_id, (expected, actual) in results.items():
            assert actual == expected


# PostgreSQL-specific tests (skipped on SQLite)
@pytest.mark.skipif(IS_SQLITE, reason="search_path is PostgreSQL-specific")
@pytest.mark.django_db
class TestPluginDatabaseContextPostgres:
    """Tests that require PostgreSQL for search_path verification."""

    def test_search_path_is_set(self):
        """Context manager should set the database search_path."""
        with plugin_database_context("my_test_plugin"):
            with connection.cursor() as cursor:
                cursor.execute("SHOW search_path")
                search_path = cursor.fetchone()[0]

            assert "my_test_plugin" in search_path

    def test_search_path_restored_after_context(self):
        """search_path should be restored to public after context exits."""
        with plugin_database_context("temp_plugin"):
            pass

        with connection.cursor() as cursor:
            cursor.execute("SHOW search_path")
            search_path = cursor.fetchone()[0]

        assert "temp_plugin" not in search_path

    def test_parallel_threads_with_search_path_verification(self):
        """Verify search_path is correctly set per thread on PostgreSQL."""
        num_threads = 5
        results = {}
        errors = []
        barrier = threading.Barrier(num_threads)

        def worker(thread_id, plugin_name):
            try:
                barrier.wait()

                with plugin_database_context(plugin_name):
                    time.sleep(0.01)

                    with connection.cursor() as cursor:
                        cursor.execute("SHOW search_path")
                        search_path = cursor.fetchone()[0]

                    actual_plugin = get_current_plugin()

                    results[thread_id] = {
                        "plugin_name": plugin_name,
                        "actual_plugin": actual_plugin,
                        "search_path": search_path,
                        "search_path_correct": plugin_name in search_path,
                    }
            except Exception as e:
                errors.append((thread_id, str(e)))

        threads = []
        for i in range(num_threads):
            plugin_name = f"search_path_plugin_{i}"
            t = threading.Thread(target=worker, args=(i, plugin_name))
            threads.append(t)

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        assert len(errors) == 0, f"Thread errors: {errors}"

        for thread_id, result in results.items():
            assert result["actual_plugin"] == result["plugin_name"], (
                f"Thread {thread_id}: plugin mismatch"
            )
            assert result["search_path_correct"], (
                f"Thread {thread_id}: search_path '{result['search_path']}' "
                f"does not contain '{result['plugin_name']}'"
            )
