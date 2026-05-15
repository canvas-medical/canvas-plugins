"""Tests for the update check module."""

import json
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from canvas_cli.utils.update_check import (
    CHECK_INTERVAL_SECONDS,
    check_for_updates,
)


@pytest.fixture()
def app_dir(tmp_path: Path) -> str:
    """Return a temporary directory path as a string."""
    return str(tmp_path)


@pytest.fixture()
def cache_path(tmp_path: Path) -> Path:
    """Return the expected cache file path within the temporary directory."""
    return tmp_path / "update_check.json"


class TestCheckForUpdates:
    """Tests for the check_for_updates function."""

    def test_no_check_when_env_var_set(self, app_dir: str) -> None:
        """Should skip entirely when CANVAS_NO_UPDATE_CHECK is set."""
        with (
            patch.dict("os.environ", {"CANVAS_NO_UPDATE_CHECK": "1"}),
            patch("canvas_cli.utils.update_check._fetch_latest_version") as mock_fetch,
        ):
            check_for_updates("0.112.0", app_dir)
            mock_fetch.assert_not_called()

    def test_fetches_and_caches_when_no_cache(self, app_dir: str, cache_path: Path) -> None:
        """Should fetch from PyPI and write a cache file on first run."""
        with patch(
            "canvas_cli.utils.update_check._fetch_latest_version",
            return_value="0.112.0",
        ):
            check_for_updates("0.112.0", app_dir)

        assert cache_path.is_file()
        data = json.loads(cache_path.read_text())
        assert data["latest_version"] == "0.112.0"
        assert "last_checked" in data

    def test_uses_cache_when_fresh(
        self, app_dir: str, cache_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Should use cached version and not fetch when cache is fresh."""
        cache_path.write_text(
            json.dumps({"last_checked": time.time(), "latest_version": "0.113.0"})
        )

        with patch("canvas_cli.utils.update_check._fetch_latest_version") as mock_fetch:
            check_for_updates("0.112.0", app_dir)
            mock_fetch.assert_not_called()

        captured = capsys.readouterr()
        assert "newer version" in captured.err

    def test_fetches_when_cache_expired(self, app_dir: str, cache_path: Path) -> None:
        """Should re-fetch when cache is older than the check interval."""
        expired_time = time.time() - CHECK_INTERVAL_SECONDS - 1
        cache_path.write_text(
            json.dumps({"last_checked": expired_time, "latest_version": "0.111.0"})
        )

        with patch(
            "canvas_cli.utils.update_check._fetch_latest_version",
            return_value="0.113.0",
        ) as mock_fetch:
            check_for_updates("0.112.0", app_dir)
            mock_fetch.assert_called_once()

        data = json.loads(cache_path.read_text())
        assert data["latest_version"] == "0.113.0"

    def test_prints_notice_when_newer_version_available(
        self, app_dir: str, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Should print a notice to stderr when a newer version exists."""
        with patch(
            "canvas_cli.utils.update_check._fetch_latest_version",
            return_value="0.113.0",
        ):
            check_for_updates("0.112.0", app_dir)

        captured = capsys.readouterr()
        assert "[notice]" in captured.err
        assert "0.112.0" in captured.err
        assert "0.113.0" in captured.err
        assert "pip install --upgrade canvas" in captured.err

    def test_no_notice_when_up_to_date(
        self, app_dir: str, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Should print nothing when already on the latest version."""
        with patch(
            "canvas_cli.utils.update_check._fetch_latest_version",
            return_value="0.112.0",
        ):
            check_for_updates("0.112.0", app_dir)

        captured = capsys.readouterr()
        assert captured.err == ""

    def test_no_notice_when_ahead(self, app_dir: str, capsys: pytest.CaptureFixture[str]) -> None:
        """Should print nothing when running a version newer than PyPI (e.g. dev build)."""
        with patch(
            "canvas_cli.utils.update_check._fetch_latest_version",
            return_value="0.112.0",
        ):
            check_for_updates("0.113.0", app_dir)

        captured = capsys.readouterr()
        assert captured.err == ""

    def test_swallows_network_errors(
        self, app_dir: str, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Should silently handle fetch failures without crashing."""
        with patch(
            "canvas_cli.utils.update_check._fetch_latest_version",
            side_effect=OSError("network down"),
        ):
            check_for_updates("0.112.0", app_dir)

        captured = capsys.readouterr()
        assert captured.err == ""

    def test_swallows_corrupt_cache(
        self, app_dir: str, cache_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Should handle a corrupt cache file gracefully."""
        cache_path.write_text("not valid json!!!")

        with patch(
            "canvas_cli.utils.update_check._fetch_latest_version",
            return_value="0.113.0",
        ):
            check_for_updates("0.112.0", app_dir)

        captured = capsys.readouterr()
        assert "newer version" in captured.err
