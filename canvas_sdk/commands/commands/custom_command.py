from typing import Any

from pydantic_core import InitErrorDetails

from canvas_sdk.commands.base import _BaseCommand


class CustomCommand(_BaseCommand):
    """A class for managing a custom command within a specific note.

    This class can be extended to create custom commands with predefined schema_key
    or passing schema_key directly to the constructor.
    """

    class Meta:
        key = "customCommand"
        schema_key: str | None = None

    _schema_key: str | None = None
    content: str | None = None
    print_content: str | None = None

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Ensure Meta.key is always 'customCommand' for all CustomCommand subclasses."""
        # Always enforce key = "customCommand" for all subclasses
        cls.Meta.key = "customCommand"

        # Call parent __init_subclass__ to perform validation
        super().__init_subclass__(**kwargs)

    def __init__(self, **data: Any) -> None:
        """Initialize with schema_key from Meta if not provided."""
        meta_schema_key = getattr(self.__class__.Meta, "schema_key", None)

        # Extract schema_key before init if provided
        instance_schema_key = data.pop("schema_key", None)

        # If Meta defines schema_key, use it and don't allow override
        if meta_schema_key is not None and instance_schema_key is not None:
            raise AttributeError(
                f"Cannot set schema_key on {self.__class__.__name__} instance. "
                f"schema_key is already defined in Meta as '{meta_schema_key}'."
            )

        super().__init__(**data)

        # Set _schema_key after init to ensure it's tracked
        if meta_schema_key is None and instance_schema_key is not None:
            self._schema_key = instance_schema_key

    @property
    def schema_key(self) -> str | None:
        """Get schema_key from Meta if defined, otherwise from instance attribute."""
        meta_schema_key = getattr(self.__class__.Meta, "schema_key", None)
        return meta_schema_key if meta_schema_key is not None else self._schema_key

    @property
    def values(self) -> dict:
        """Get values for the custom command."""
        return {**super().values, "schema_key": self.schema_key}

    def _get_error_details(self, method: str) -> list[InitErrorDetails]:
        """Get error details for the custom command."""
        errors = super()._get_error_details(method)

        if method == "originate":
            if not self.content:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Content must be provided for a custom command.",
                        self.content,
                    )
                )
            if not self.schema_key:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Schema key must be provided for a custom command.",
                        self.schema_key,
                    )
                )
        return errors


__exports__ = ("CustomCommand",)
