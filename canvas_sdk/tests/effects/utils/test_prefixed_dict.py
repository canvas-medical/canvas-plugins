from datetime import date

from pydantic.dataclasses import dataclass

from canvas_sdk.effects.utils import _PrefixedDict


@dataclass
class SimpleItem(_PrefixedDict, prefix="item"):
    """SimpleItem."""

    name: str | None = None
    value: str | None = None


@dataclass
class ItemWithUnprefixed(_PrefixedDict, prefix="item", unprefixed_fields=frozenset({"global_id"})):
    """ItemWithUnprefixed."""

    name: str | None = None
    global_id: str | None = None


@dataclass
class ItemWithDate(_PrefixedDict, prefix="entry"):
    """ItemWithDate."""

    label: str | None = None
    start_date: date | None = None


def test_to_dict_prefixes_fields() -> None:
    """to_dict should prepend the configured prefix to each field name."""
    item = SimpleItem(name="foo", value="bar")
    assert item.to_dict() == {"item_name": "foo", "item_value": "bar"}


def test_to_dict_excludes_none_values() -> None:
    """Fields set to None should be omitted from the resulting dict."""
    item = SimpleItem(name="foo")
    assert item.to_dict() == {"item_name": "foo"}


def test_to_dict_all_none_returns_empty() -> None:
    """A dataclass with all None fields should produce an empty dict."""
    item = SimpleItem()
    assert item.to_dict() == {}


def test_unprefixed_fields_are_not_prefixed() -> None:
    """Fields listed in unprefixed_fields should keep their original name."""
    item = ItemWithUnprefixed(name="foo", global_id="abc")
    assert item.to_dict() == {"item_name": "foo", "global_id": "abc"}


def test_unprefixed_field_excluded_when_none() -> None:
    """Unprefixed fields should still be excluded when their value is None."""
    item = ItemWithUnprefixed(name="foo")
    assert item.to_dict() == {"item_name": "foo"}


def test_date_serialized_to_isoformat() -> None:
    """Date values should be serialized to ISO 8601 format strings."""
    item = ItemWithDate(label="test", start_date=date(2025, 3, 15))
    assert item.to_dict() == {"entry_label": "test", "entry_start_date": "2025-03-15"}


def test_date_none_excluded() -> None:
    """A None date field should be excluded from the dict."""
    item = ItemWithDate(label="test")
    assert item.to_dict() == {"entry_label": "test"}


def test_prefix_inherited_per_subclass() -> None:
    """Each subclass should maintain its own independent prefix."""

    @dataclass
    class Alpha(_PrefixedDict, prefix="a"):
        x: str | None = None

    @dataclass
    class Beta(_PrefixedDict, prefix="b"):
        x: str | None = None

    assert Alpha(x="1").to_dict() == {"a_x": "1"}
    assert Beta(x="1").to_dict() == {"b_x": "1"}
