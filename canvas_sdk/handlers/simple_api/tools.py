from collections.abc import ItemsView, Iterable, Iterator, KeysView, Mapping, ValuesView
from typing import Any, TypeVar, overload

KeyType = TypeVar("KeyType")
ValueType = TypeVar("ValueType", covariant=True)


class MultiDict(Mapping[KeyType, ValueType]):
    """Immutable key-value data structure that can store multiple values per key."""

    def __init__(self, items: Iterable[tuple[KeyType, ValueType]] | None = None) -> None:
        self._dict: dict[KeyType, ValueType] = {}
        self._items = []
        for key, value in items or ():
            if key not in self._dict:
                self._dict[key] = value
            self._items.append((key, value))

    def __len__(self) -> int:
        return len(self._dict)

    def __iter__(self) -> Iterator[KeyType]:
        return iter(self.keys())

    def __getitem__(self, key: KeyType, /) -> ValueType:
        return self._dict[key]

    def __contains__(self, x: object, /) -> bool:
        return x in self._dict

    @overload
    def get(self, __key: KeyType, /) -> Any: ...

    @overload
    def get(self, __key: KeyType, /, __default: Any = None) -> Any: ...

    def get(self, __key: KeyType, __default: Any | None = None) -> Any:
        """Get a value for a key if present, and if not, return the default value."""
        return self._dict.get(__key, __default)

    def get_list(self, __key: KeyType) -> list[ValueType]:
        """Get the values for a key if present, and if not, return an empty list."""
        return [value for key, value in self._items if key == __key]

    def items(self) -> ItemsView[KeyType, ValueType]:
        """Return an items view of the dict."""
        return self._dict.items()

    def multi_items(self) -> Iterable[tuple[KeyType, ValueType]]:
        """Return an iterable of tuples of the keys and values in the dict."""
        yield from self._items

    def keys(self) -> KeysView[KeyType]:
        """Return a keys view of the dict."""
        return self._dict.keys()

    def __reversed__(self) -> Iterator[KeyType]:
        return iter(reversed(list(self.keys())))

    def values(self) -> ValuesView[ValueType]:
        """Return a values view of the dict."""
        return self._dict.values()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MultiDict):
            return NotImplemented

        return other._items == self._items


class CaseInsensitiveMultiDict(MultiDict[str, ValueType]):
    """
    Case-insensitive immutable key-value data structure that can store multiple values per key.

    Keys in the dict are interpreted in a case-insensitive manner.
    """

    def __init__(self, items: Iterable[tuple[str, ValueType]] | None = None) -> None:
        super().__init__(((key.lower(), value) for key, value in items or ()))

    def __getitem__(self, key: str, /) -> ValueType:
        return super().__getitem__(key.lower())

    def __contains__(self, x: object, /) -> bool:
        if not isinstance(x, str):
            return False

        return super().__contains__(x.lower())

    def get(self, __key: KeyType, __default: Any | None = None) -> Any:
        """Get a value for a key if present, and if not, return the default value."""
        if not isinstance(__key, str):
            return __default

        return super().get(__key.lower(), __default)

    def get_list(self, __key: KeyType) -> list[ValueType]:
        """Get the values for a key if present, and if not, return an empty list."""
        if not isinstance(__key, str):
            return []

        return super().get_list(__key.lower())


def separate_headers(headers: Mapping[str, str]) -> list[tuple[str, str]]:
    """
    Break apart header values containing comma-separated lists into discrete key-value pairs.
    """
    headers_list = []

    for key, values in headers.items():
        for value in values.split(","):
            headers_list.append((key, value.strip()))

    return headers_list


__exports__ = (
    "KeyType",
    "ValueType",
    "MultiDict",
    "CaseInsensitiveMultiDict",
    "separate_headers",
)
