from datetime import date, datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from pydantic_core import InitErrorDetails, PydanticCustomError, ValidationError


class Model(BaseModel):
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
