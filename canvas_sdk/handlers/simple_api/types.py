from typing import Any

from requests.structures import CaseInsensitiveDict

JSON = dict[str, Any] | list[Any] | int | float | str | bool

__all__ = ["CaseInsensitiveDict", "JSON"]
