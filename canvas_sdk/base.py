from datetime import date, datetime
from enum import Enum
from typing import Any

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
        return getattr(self.Meta, f"{method}_required_fields", tuple())

    def _create_error_detail(self, type: str, message: str, value: Any) -> InitErrorDetails:
        return InitErrorDetails({"type": PydanticCustomError(type, message), "input": value})

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        required_fields = self._get_effect_method_required_fields(method)
        class_name = self.__repr_name__()  # type: ignore[misc]

        class_name_article = "an" if class_name.startswith(("A", "E", "I", "O", "U")) else "a"
        return [
            self._create_error_detail(
                "missing",
                f"Field '{field}' is required to {method.replace('_', ' ')} {class_name_article} {class_name}",
                v,
            )
            for field in required_fields
            if (v := getattr(self, field)) is None
        ]

    def _validate_before_effect(self, method: str) -> None:
        self.model_validate(self)
        if error_details := self._get_error_details(method):
            raise ValidationError.from_exception_data(self.__class__.__name__, error_details)
