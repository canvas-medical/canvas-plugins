"""Tests for the ratchet that decides which plugins may use the deprecated rules."""

from pathlib import Path

import pytest

from plugin_runner import sandbox_allowlists
from plugin_runner.sandbox_allowlists import (
    KEY_VARIABLE,
    MissingAllowlist,
    MissingAllowlistKey,
    digest,
    is_allowlisted,
    is_always_legacy,
    is_blessed_import,
)


@pytest.fixture(autouse=True)
def _clear_cache() -> None:
    """Each test supplies its own allowlist contents."""
    sandbox_allowlists._allowlist.cache_clear()
    sandbox_allowlists._blessed_imports.cache_clear()
    sandbox_allowlists._always_legacy.cache_clear()


def test_a_plugin_listed_to_always_use_the_deprecated_rules_is_recognized(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The always list is keyed on instance and plugin, like the legacy allowlist."""
    key = "test-key"
    monkeypatch.setenv(KEY_VARIABLE, key)
    monkeypatch.setattr(
        sandbox_allowlists,
        "_always_legacy",
        lambda: frozenset({digest(key, "duohealth", "charting_ui")}),
    )

    assert is_always_legacy("duohealth", "charting_ui")
    assert not is_always_legacy("duohealth", "other_plugin")
    assert not is_always_legacy("duohealth-dev", "charting_ui")


def test_without_a_key_no_plugin_is_always_on_the_deprecated_rules(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An unreadable always list leaves plugins on the normal path."""
    monkeypatch.delenv(KEY_VARIABLE, raising=False)

    assert not is_always_legacy("duohealth", "charting_ui")


def test_a_missing_always_list_lists_nobody(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The always list is optional."""
    monkeypatch.setenv(KEY_VARIABLE, "test-key")
    monkeypatch.setattr(sandbox_allowlists, "ALWAYS_LEGACY_PATH", tmp_path / "absent.txt")

    assert not is_always_legacy("duohealth", "charting_ui")


def test_a_listed_plugin_is_allowlisted(monkeypatch: pytest.MonkeyPatch, tmp_path: object) -> None:
    """A plugin whose digest is in the file may use the deprecated rules."""
    key = "test-key"
    monkeypatch.setenv(KEY_VARIABLE, key)
    monkeypatch.setattr(
        sandbox_allowlists,
        "_allowlist",
        lambda: frozenset({digest(key, "wovenly", "old_plugin")}),
    )

    assert is_allowlisted("wovenly", "old_plugin")


def test_an_unlisted_plugin_is_not_allowlisted(monkeypatch: pytest.MonkeyPatch) -> None:
    """Anything not in the file loads under the current rules."""
    key = "test-key"
    monkeypatch.setenv(KEY_VARIABLE, key)
    monkeypatch.setattr(
        sandbox_allowlists,
        "_allowlist",
        lambda: frozenset({digest(key, "wovenly", "old_plugin")}),
    )

    assert not is_allowlisted("wovenly", "new_plugin")


def test_the_same_plugin_on_another_instance_is_not_allowlisted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Entries are scoped to one instance, so a copy elsewhere is a separate decision."""
    key = "test-key"
    monkeypatch.setenv(KEY_VARIABLE, key)
    monkeypatch.setattr(
        sandbox_allowlists,
        "_allowlist",
        lambda: frozenset({digest(key, "wovenly", "old_plugin")}),
    )

    assert not is_allowlisted("wovenly-dev", "old_plugin")


def test_a_missing_key_raises_rather_than_refusing_everything(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Without the key the answer is unknown, so the check raises rather than answering.

    The caller decides what an unreadable allowlist means, and says why when it refuses
    a plugin, instead of a quiet "not listed" for every plugin at once.
    """
    monkeypatch.delenv(KEY_VARIABLE, raising=False)

    with pytest.raises(MissingAllowlistKey):
        is_allowlisted("wovenly", "old_plugin")


def test_the_digest_reveals_neither_customer_nor_plugin() -> None:
    """The stored entry is opaque: the file names nobody."""
    entry = digest("test-key", "wovenly", "old_plugin")

    assert "wovenly" not in entry
    assert "old_plugin" not in entry
    assert len(entry) == 64


def test_the_digest_depends_on_the_key() -> None:
    """Without the key an entry cannot be reproduced from a guessed name."""
    assert digest("one", "wovenly", "old_plugin") != digest("two", "wovenly", "old_plugin")


def test_a_missing_allowlist_file_raises_rather_than_refusing_everything(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """An absent allowlist is a misconfiguration, not an empty allowlist.

    Reading it as empty would refuse every plugin that depends on the deprecated rules,
    on every instance at once.
    """
    monkeypatch.setenv(KEY_VARIABLE, "test-key")
    monkeypatch.setattr(sandbox_allowlists, "ALLOWLIST_PATH", tmp_path / "absent.txt")

    with pytest.raises(MissingAllowlist):
        is_allowlisted("wovenly", "old_plugin")


def test_the_committed_allowlist_only_shrinks() -> None:
    """The allowlist is a ratchet.

    Raising this bound is a deliberate act: a plugin is being granted the deprecated
    rules that did not have them, which is what this mechanism exists to prevent.
    """
    # 202: one instance created after the list was generated, raised deliberately.
    high_water_mark = 202

    sandbox_allowlists._allowlist.cache_clear()

    if not sandbox_allowlists.ALLOWLIST_PATH.exists():
        pytest.skip("allowlist not generated yet")

    entries = sandbox_allowlists._allowlist()

    assert len(entries) <= high_water_mark, (
        f"The allowlist has grown to {len(entries)} entries. It may only shrink; "
        "a plugin cannot newly acquire the deprecated sandbox rules."
    )
    assert all(len(entry) == 64 for entry in entries)


def test_the_committed_always_list_only_shrinks() -> None:
    """The always list is a ratchet too, with its own bound."""
    high_water_mark = 13

    sandbox_allowlists._always_legacy.cache_clear()
    entries = sandbox_allowlists._always_legacy()

    assert sandbox_allowlists.ALWAYS_LEGACY_PATH.exists()
    assert len(entries) <= high_water_mark, (
        f"The always list has grown to {len(entries)} entries. It may only shrink."
    )
    assert all(len(entry) == 64 for entry in entries)


def test_a_blessed_import_is_permitted(monkeypatch: pytest.MonkeyPatch) -> None:
    """A named plugin may import a module that is not generally allowed."""
    key = "test-key"
    monkeypatch.setenv(KEY_VARIABLE, key)
    monkeypatch.setattr(
        sandbox_allowlists,
        "_blessed_imports",
        lambda: frozenset({digest(key, "hyperscribe", "sqlite3")}),
    )

    assert is_blessed_import("hyperscribe", "sqlite3")
    assert not is_blessed_import("hyperscribe", "socket")
    assert not is_blessed_import("other_plugin", "sqlite3")


def test_blessing_without_a_key_grants_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unlike the legacy allowlist, an unreadable blessing list simply grants nothing.

    The default is to refuse the import, so failing closed here matches the answer an
    absent entry would give, rather than refusing plugins wholesale.
    """
    monkeypatch.delenv(KEY_VARIABLE, raising=False)

    assert not is_blessed_import("hyperscribe", "sqlite3")
