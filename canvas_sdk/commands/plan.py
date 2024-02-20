from typing import Any

from canvas_sdk.commands.base import _BaseCommand, _BaseCommandAttributes


class PlanCommandAttributes(_BaseCommandAttributes):
    """Attributes speciic to the Plan Command."""

    narrative: str | None


class PlanCommand(_BaseCommand):
    """A class for managing a Plan command within a specific note."""

    narrative: str | None

    def __init__(
        self,
        narrative: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.narrative = narrative

    def __setattr__(self, name: str, value: Any) -> None:
        if name not in PlanCommandAttributes.__annotations__:
            return super().__setattr__(name, value)

        expected_type = PlanCommandAttributes.__annotations__[name]
        if issubclass(type(value), expected_type):
            super().__setattr__(name, value)
        else:
            raise TypeError(f"'{name}' requires a type of '{expected_type}'")

    @property
    def values(self) -> dict:
        """The Plan command's field values."""
        return {"narrative": self.narrative}
