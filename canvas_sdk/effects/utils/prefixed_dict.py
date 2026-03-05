from datetime import date
from typing import Any, ClassVar

from pydantic import TypeAdapter


class _PrefixedDict:
    """Base class that converts dataclass fields to a prefixed dict, excluding None values."""

    _prefix: ClassVar[str]
    _unprefixed_fields: ClassVar[frozenset[str]]

    def __init_subclass__(
        cls,
        prefix: str = "",
        unprefixed_fields: frozenset[str] = frozenset(),
        **kwargs: Any,
    ) -> None:
        super().__init_subclass__(**kwargs)
        cls._prefix = prefix
        cls._unprefixed_fields = unprefixed_fields

    def _serialize_value(self, value: str | date) -> str:
        """Serializes values to string. For now, just serializes dates, but this can be added on to as needed."""
        if isinstance(value, date):
            return value.isoformat()
        return value

    def to_dict(self) -> dict[str, str]:
        """Convert to a dictionary with prefixed keys, excluding None values."""
        raw = TypeAdapter(type(self)).dump_python(self, mode="json", exclude_none=True)
        return {
            (f if f in self._unprefixed_fields else f"{self._prefix}_{f}"): self._serialize_value(v)
            for f, v in raw.items()
        }


__exports__ = ()
