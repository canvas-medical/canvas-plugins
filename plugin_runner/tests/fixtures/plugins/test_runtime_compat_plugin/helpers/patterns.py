"""Patterns plugin helper modules use, each taken from an installed plugin.

Every function runs inside a handler's compute(), as the original code did, and returns a
string describing its result.
"""

from dataclasses import dataclass
from typing import Any

from rapidfuzz import fuzz

from canvas_sdk.v1.data import LabOrder, Patient


class _Builder:
    def _build_question(self, question: str) -> str:
        return f"question: {question}"


class _PhoneCallBuilder(_Builder):
    def _build_question(self, question: str) -> str:
        return super()._build_question(question).upper()


def super_call() -> str:
    """A subclass extends a parent's underscore method through super()."""
    return _PhoneCallBuilder()._build_question("disposition")


@dataclass
class _SectionResult:
    key: str


def builtins_in_use() -> str:
    """A dataclass compared with None, bytearray, and the format builtin."""
    pair = [_SectionResult("visits"), _SectionResult("labs")]
    data = bytearray(b"ok")
    return f"{None in pair}|{bytes(data).decode()}|{format(3.14159, '.2f')}"


def numbers_and_frames() -> str:
    """Flooring a timestamp, and reading the line of a failing frame for a report."""
    seconds = (1760000000.75).__floor__()

    try:
        raise ValueError("report me")
    except ValueError as error:
        traceback: Any = error.__traceback__
        line = traceback.tb_frame.f_lineno

    return f"{seconds}|{isinstance(line, int)}"


def fuzzy_match() -> str:
    """A scorer from rapidfuzz's fuzz submodule."""
    return str(fuzz.token_set_ratio("hemoglobin a1c", "a1c hemoglobin"))


def list_item_assignment() -> str:
    """Item assignment with an index variable named like a list method."""
    scheduled_matches = ["a", "b", "c"]
    index = 1
    scheduled_matches[index] = "B"
    return ",".join(scheduled_matches)


class _MissingRelation(AttributeError):
    pass


class _Claim:
    @property
    def supervising_provider(self) -> str:
        raise _MissingRelation("no supervising provider")


def missing_relation() -> str:
    """A missing related object is caught as the exception it raises."""
    try:
        provider = _Claim().supervising_provider
    except _MissingRelation:
        return "no supervising provider"

    return f"fell through with {provider!r}"


def model_meta() -> str:
    """Field introspection on SDK models through `_meta`."""
    meta: Any = getattr(Patient, "_meta", None)
    names = {field.name for field in meta.concrete_fields}

    try:
        meta.get_field("entered_in_error")
        has_eie = True
    except Exception:
        has_eie = False

    return f"{LabOrder._meta.model_name}|{'first_name' in names}|{has_eie}"


def exception_ancestry() -> str:
    """Walking an exception's class hierarchy to classify it."""
    try:
        raise LookupError("not found")
    except LookupError as error:
        return str(any(c.__name__ == "LookupError" for c in type(error).__mro__))


def error_reporting() -> str:
    """An error passes an except clause naming another builtin exception, then is reported
    by its type's name.
    """
    try:
        try:
            raise KeyError("missing")
        except FileNotFoundError:
            return "wrong clause"
    except KeyError as error:
        return f"{type(error).__name__}: {ascii(str(error))}"


def _described() -> None:
    """Does a thing."""


def introspection() -> str:
    """dir() of an SDK module, median from statistics, and a copied docstring."""
    from statistics import median

    import canvas_sdk.commands as commands

    def wrapper() -> None:
        pass

    wrapper.__doc__ = _described.__doc__

    return f"{'PrescribeCommand' in dir(commands)}|{median([3, 1, 2])}|{wrapper.__doc__}"
