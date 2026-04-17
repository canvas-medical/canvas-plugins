import functools
import inspect
import re
import warnings
from collections.abc import Callable
from datetime import date, datetime
from enum import Enum
from typing import Any, get_type_hints
from uuid import UUID

from pydantic import BaseModel, ConfigDict, NonNegativeInt
from pydantic_core import InitErrorDetails, PydanticCustomError, ValidationError

from canvas_generated.messages.effects_pb2 import Effect

_DELAY_PARAM = inspect.Parameter(
    "delay_seconds",
    inspect.Parameter.KEYWORD_ONLY,
    default=None,
    annotation="NonNegativeInt | None",
)

_DELAY_SECONDS_DESC = (
    "delay_seconds (NonNegativeInt | None): Optional number of seconds to delay the effect. "
    "Must be >= 0."
)

_DOCSTRING_SECTION_HEADERS = (
    "Returns",
    "Raises",
    "Yields",
    "Yield",
    "Example",
    "Examples",
    "Note",
    "Notes",
    "Attributes",
    "See Also",
)


def _insert_delay_seconds_into_doc(doc: str | None) -> str:
    """Insert ``delay_seconds`` into an existing Google-style ``Args:`` block, or append one."""
    if not doc:
        return "\n\nArgs:\n    " + _DELAY_SECONDS_DESC + "\n"

    args_match = re.search(r"^([ \t]*)Args:[ \t]*$", doc, re.MULTILINE)
    if args_match is None:
        return doc.rstrip() + "\n\nArgs:\n    " + _DELAY_SECONDS_DESC + "\n"

    args_indent = args_match.group(1)
    entry_line = f"{args_indent}    {_DELAY_SECONDS_DESC}"

    section_re = rf"^{re.escape(args_indent)}(?:{'|'.join(_DOCSTRING_SECTION_HEADERS)}):[ \t]*$"
    next_match = re.search(section_re, doc[args_match.end() :], re.MULTILINE)
    abs_pos = args_match.end() + next_match.start() if next_match else len(doc)
    while abs_pos > 0 and doc[abs_pos - 1] == "\n":
        abs_pos -= 1
    return doc[:abs_pos] + "\n" + entry_line + doc[abs_pos:]


def async_effect(func: Callable[..., Effect]) -> Callable[..., Effect]:
    """Add a `delay_seconds` keyword argument to a method that returns an Effect.

    The wrapped method returns a plain Effect. This decorator:
    - Injects `delay_seconds` as a keyword-only argument on the public signature.
    - Validates it is non-negative (raises ValueError otherwise).
    - Sets it on the returned Effect when provided.
    """

    @functools.wraps(func)
    def wrapper(*args: Any, delay_seconds: NonNegativeInt | None = None, **kwargs: Any) -> Effect:
        if delay_seconds is not None:
            if not isinstance(delay_seconds, int) or isinstance(delay_seconds, bool):
                raise ValueError(
                    f"delay_seconds must be an integer, got {type(delay_seconds).__name__}"
                )
            if delay_seconds < 0:
                raise ValueError(f"delay_seconds must be non-negative, got {delay_seconds}")
        effect = func(*args, **kwargs)
        if delay_seconds is not None:
            effect.delay_seconds = delay_seconds
        return effect

    sig = inspect.signature(func)
    wrapper.__signature__ = sig.replace(  # type: ignore[attr-defined]
        parameters=[*sig.parameters.values(), _DELAY_PARAM]
    )

    wrapper.__doc__ = _insert_delay_seconds_into_doc(wrapper.__doc__)

    return wrapper


class _AsyncEffectMixin:
    """Auto-wrap public methods that return ``Effect`` with :func:`async_effect`.

    Any subclass gets a ``delay_seconds`` kwarg added to each of its own
    public methods whose return annotation is exactly ``Effect``.
    """

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        for name, attr in list(vars(cls).items()):
            if not inspect.isfunction(attr) or name.startswith("_"):
                continue
            raw_return = attr.__annotations__.get("return")
            if raw_return is Effect:
                setattr(cls, name, async_effect(attr))
                continue
            if not isinstance(raw_return, str) or "Effect" not in raw_return:
                continue
            try:
                hints = get_type_hints(attr)
            except Exception as exc:
                warnings.warn(
                    f"Could not resolve type hints for {cls.__qualname__}.{name}: {exc}. "
                    "This method will not receive delay_seconds support.",
                    stacklevel=2,
                )
                continue
            if hints.get("return") is Effect:
                setattr(cls, name, async_effect(attr))


class Model(BaseModel, _AsyncEffectMixin):
    """A base model that includes validation methods."""

    class Meta:
        pass

    model_config = ConfigDict(
        strict=True,
        revalidate_instances="always",
        validate_assignment=True,
        json_encoders={
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat(),
            Enum: lambda v: v.value,
        },
    )

    def _get_effect_method_required_fields(self, method: Any) -> tuple:
        return getattr(self.Meta, f"{method}_required_fields", ())

    def _create_error_detail(self, type: str, message: str, value: Any) -> InitErrorDetails:
        return InitErrorDetails({"type": PydanticCustomError(type, message), "input": value})

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        required_fields = self._get_effect_method_required_fields(method)
        class_name = self.__repr_name__()  # type: ignore[misc]

        class_name_article = "an" if class_name.startswith(("A", "E", "I", "O", "U")) else "a"

        error_details = []
        for field in required_fields:
            fields = field.split("|")
            if not all(getattr(self, f) is None for f in fields):
                continue
            field_description = " or ".join([f"'{f}'" for f in fields])
            message = f"Field {field_description} is required to {method.replace('_', ' ')} {class_name_article} {class_name}"
            error = self._create_error_detail("missing", message, None)
            error_details.append(error)

        return error_details

    def _validate_before_effect(self, method: str) -> None:
        self.model_validate(self)
        if error_details := self._get_error_details(method):
            raise ValidationError.from_exception_data(self.__class__.__name__, error_details)


class TrackableFieldsModel(Model):
    """
    A base model with additional functionality for tracking modified fields.

    Attributes:
        _dirty_keys (set[str]): A set to track which fields have been modified.
    """

    _dirty_excluded_keys: list[str] = [
        "note_uuid",
    ]

    _dirty_keys: set[str] = set()

    def __init__(self, /, **data: Any) -> None:
        """Initialize the command and mark all provided keys as dirty."""
        super().__init__(**data)

        # Initialize a set to track which fields have been modified.
        self._dirty_keys = set()

        # Explicitly mark all keys provided in the constructor as dirty.
        self._dirty_keys.update(data.keys())

    def __setattr__(self, name: str, value: Any) -> None:
        """Set an attribute and mark it as dirty unless excluded."""
        if not name.startswith("_") and name not in self._dirty_excluded_keys:
            self._dirty_keys.add(name)
        super().__setattr__(name, value)

    def is_dirty(self, key: str) -> bool:
        """Returns True if the given property has been modified (i.e. marked as dirty), False otherwise."""
        return key in self._dirty_keys

    @property
    def values(self) -> dict:
        """Return a dictionary of modified attributes with type-specific transformations."""
        result = {}
        for key in self._dirty_keys:
            value = getattr(self, key)
            if isinstance(value, Enum):
                # If it's an enum, use its .value.
                result[key] = value.value if value else None
            elif isinstance(value, date | datetime):
                # If it's a date/datetime, use isoformat().
                result[key] = value.isoformat() if value else None
            elif isinstance(value, UUID):
                # If it's a UUID, use its string representation.
                result[key] = str(value) if value else None
            else:
                # For strings, integers, or any other type, return as is.
                result[key] = value
        return result
