import dataclasses
from abc import ABC, abstractmethod
from typing import Any


@dataclasses.dataclass
class ResponseOption:
    """A response option for a question."""

    TYPE_TEXT = "TXT"
    TYPE_INTEGER = "INT"
    TYPE_RADIO = "SING"
    TYPE_CHECKBOX = "MULT"

    def __init__(self, dbid: int, name: str, code: str, value: str) -> None:
        self.dbid: int = dbid
        self.name: str = name
        self.code: str = code
        self.value: str = value

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, ResponseOption):
            return (
                self.dbid == other.dbid
                and self.name == other.name
                and self.code == other.code
                and self.value == other.value
            )
        return False

    def __repr__(self) -> str:
        return f"ResponseOption({self.dbid=!r}, {self.name=!r}, {self.code=!r}, {self.value=!r})"


class BaseQuestion(ABC):
    """Base class for questions."""

    type: str

    def __init__(
        self, name: str, label: str, coding: dict[str, str], options: list[ResponseOption]
    ) -> None:
        self.name: str = name
        self.label: str = label
        self.coding: dict[str, str] = coding
        self.options: list[ResponseOption] = options
        self.response: Any | None = None

    def __repr__(self) -> str:
        return f"Question({self.name=!r}, {self.label=!r}, {self.type=!r}, {self.options=!r}, {self.response=!r})"

    @abstractmethod
    def add_response(self, *args: Any, **kwargs: Any) -> None:
        """Record a response for the question.

        Subclasses will override this to perform type-specific validation.
        """
        raise NotImplementedError("Subclasses must implement this method.")


class TextQuestion(BaseQuestion):
    """A question that expects a text response."""

    type = ResponseOption.TYPE_TEXT

    def add_response(self, /, text: str) -> None:
        """For a text question, the response must be a string."""
        if not isinstance(text, str):
            raise ValueError(
                f"Response for a text question must be a string. Question: {self.label}"
            )
        self.response = text


class IntegerQuestion(BaseQuestion):
    """A question that expects an integer response."""

    type = ResponseOption.TYPE_INTEGER

    def add_response(self, /, integer: int) -> None:
        """For an integer question, the response must be convertible to int."""
        try:
            self.response = int(integer)
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Response for IntegerQuestion must be convertible to an integer. Question: {self.label}"
            ) from e


class RadioQuestion(BaseQuestion):
    """A question that expects a single-choice response."""

    type = ResponseOption.TYPE_RADIO

    def add_response(self, /, option: ResponseOption) -> None:
        """Record a radio response.

        Expects a single keyword argument 'option' of type ResponseOption.
        Validates that the option's value is among the allowed options.
        """
        if option not in self.options:
            raise ValueError(
                f"Invalid response option for radio question '{self.label}'. Allowed options: {self.options}"
            )

        self.response = option.dbid


class CheckboxQuestion(BaseQuestion):
    """A question that expects a multiple-choice response."""

    type = ResponseOption.TYPE_CHECKBOX

    def add_response(
        self, /, option: ResponseOption, selected: bool = True, comment: str = ""
    ) -> None:
        """Record a checkbox response.

        Validates that:
          - 'option' is a ResponseOption.
          - 'selected' is a bool (defaults to True if not provided).
          - 'comment' is a string (defaults to empty string if not provided).
        The response is stored as a list of dictionaries.
        """
        if option not in self.options:
            raise ValueError(
                f"Invalid response option for checkbox question '{self.label}'. Allowed values: {self.options}"
            )

        if not self.response:
            self.response = []
        self.response.append(
            {"text": option.name, "value": option.dbid, "comment": comment, "selected": selected}
        )


__exports__ = (
    "ResponseOption",
    "BaseQuestion",
    "TextQuestion",
    "IntegerQuestion",
    "RadioQuestion",
    "CheckboxQuestion",
)
