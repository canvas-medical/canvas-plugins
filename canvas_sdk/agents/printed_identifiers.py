"""Patient identifiers read off a scanned document, checked against the text as printed.

A fax or scan is read by a model, which can misread a character (``J0HN`` for ``JOHN``)
or quietly fix one, and can read a birth date day-first. When the model passes each
identifier both as it read it and exactly as printed, :func:`check_printed` refuses what
cannot be trusted, and :func:`repair_candidates` offers the readings a common misread
would explain, for the matching code to try after the identifiers as read match no one.

Fax misreads tried: 0/O, 1/I/l, 5/S, 8/B. In names only digits and ``|`` are replaced,
since a digit in a name is always a misread; in an MRN both directions are. A birth date
is never altered.
"""

import re
from dataclasses import dataclass, field
from datetime import date
from typing import Any

LEGIBILITY = ("clear", "readable_with_artifacts", "illegible")

# Characters a fax confuses, folded together for comparing a reading with the print.
_FOLD = str.maketrans({"0": "o", "1": "l", "i": "l", "|": "l", "5": "s", "8": "b"})
_NAME_REPAIRS = {"0": ("o",), "1": ("l", "i"), "|": ("l", "i"), "5": ("s",), "8": ("b",)}
_MRN_REPAIRS = {
    "0": ("o",),
    "o": ("0",),
    "1": ("i", "l"),
    "i": ("1",),
    "l": ("1",),
    "5": ("s",),
    "s": ("5",),
    "8": ("b",),
    "b": ("8",),
}
# Letters a fax prints inside a numeric date, read as the digits they stand for.
_DATE_DIGITS = str.maketrans({"o": "0", "i": "1", "l": "1", "|": "1", "s": "5", "b": "8"})
# Words printed beside an MRN that are not part of it.
_MRN_LABEL_WORDS = frozenset({"mrn", "mr", "id", "no", "number", "chart", "acct", "pt", "patient"})
_MONTHS = {
    name: number
    for number, names in enumerate(
        (
            ("jan", "january"),
            ("feb", "february"),
            ("mar", "march"),
            ("apr", "april"),
            ("may",),
            ("jun", "june"),
            ("jul", "july"),
            ("aug", "august"),
            ("sep", "sept", "september"),
            ("oct", "october"),
            ("nov", "november"),
            ("dec", "december"),
        ),
        start=1,
    )
    for name in names
}
_DATE_LABEL = re.compile(r"^\s*(dob|d\.o\.b\.?|birth\s*date|date\s*of\s*birth)\s*[:#]?\s*", re.I)

# The most readings tried per field, and per document, fewest changed characters first.
MAX_VARIANTS_PER_FIELD = 8
MAX_CANDIDATES = 16

REPAIRED = "fax_repair"
SWAPPED = "name_swapped"


def _tokens(value: str, *, folded: bool) -> list[str]:
    lowered = value.lower().translate(_FOLD) if folded else value.lower()
    return re.findall(r"[a-z0-9|]+", lowered)


def _name_agrees(read: str, printed: str) -> bool:
    """Every word of the name read is printed, allowing for fax misreads."""
    shown = set(_tokens(printed, folded=True))
    return all(token in shown for token in _tokens(read, folded=True))


def _mrn_agrees(read: str, printed: str) -> bool:
    """The MRN read is the printed one, its label words dropped, allowing for misreads."""
    shown = [t for t in _tokens(printed, folded=False) if t not in _MRN_LABEL_WORDS]
    return "".join(_tokens(read, folded=True)) == "".join(shown).translate(_FOLD)


def parse_printed_date(printed: str) -> date | None:
    """The birth date as printed, read month first with a four-digit year, or None.

    Takes ``03/09/1971`` (and ``-`` or ``.``), ``1971-03-09``, and ``March 9, 1971`` or
    ``9 Mar 1971``. A two-digit year or a date that is not one is None: it is never
    guessed.
    """
    shown = _DATE_LABEL.sub("", printed).strip().lower()
    numeric = shown.translate(_DATE_DIGITS)
    if match := re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", numeric):
        year, month, day = (int(part) for part in match.groups())
    elif match := re.fullmatch(r"(\d{1,2})\s*[/.-]\s*(\d{1,2})\s*[/.-]\s*(\d{4})", numeric):
        month, day, year = (int(part) for part in match.groups())
    elif match := re.fullmatch(r"([a-z]+)\.?\s+(\d{1,2}),?\s+(\d{4})", shown):
        month, day, year = _MONTHS.get(match[1], 0), int(match[2]), int(match[3])
    elif match := re.fullmatch(r"(\d{1,2})\s+([a-z]+)\.?,?\s+(\d{4})", shown):
        day, month, year = int(match[1]), _MONTHS.get(match[2], 0), int(match[3])
    else:
        return None
    try:
        return date(year, month, day)
    except ValueError:
        return None


def check_printed(arguments: dict[str, Any]) -> str | None:
    """Why the identifiers cannot be trusted, or None when they can.

    Refuses identifiers the model called illegible or handwritten, pages that name
    different patients, and a value read that its printed text does not support. Checks
    only what the model passed: without ``as_printed`` there is nothing to compare.
    """
    if arguments.get("legibility") == "illegible":
        return "The identifiers are illegible; a person files this document."
    if arguments.get("handwritten"):
        return "The identifiers are handwritten; a person files this document."
    if arguments.get("pages_disagree"):
        return "The pages name different patients; a person files this document."
    printed = arguments.get("as_printed") or {}
    name = str(printed.get("name") or "").strip()
    for key in ("first_name", "last_name"):
        read = str(arguments.get(key) or "").strip()
        if read and name and not _name_agrees(read, name):
            return f"The {key.replace('_', ' ')} read is not the name as printed."
    mrn = str(arguments.get("mrn") or "").strip()
    printed_mrn = str(printed.get("mrn") or "").strip()
    if mrn and printed_mrn and not _mrn_agrees(mrn, printed_mrn):
        return "The MRN read is not the MRN as printed."
    birth_date = str(arguments.get("birth_date") or "").strip()
    printed_date = str(printed.get("birth_date") or "").strip()
    if birth_date and printed_date:
        shown = parse_printed_date(printed_date)
        if shown is None:
            return (
                "The printed birth date cannot be read without guessing (a two-digit year "
                "or an unknown format); a person files this document."
            )
        if shown.isoformat() != birth_date:
            return "The birth date read is not the birth date as printed."
    return None


def _variants(value: str, repairs: dict[str, tuple[str, ...]]) -> tuple[list[str], bool]:
    """``value`` first, then readings with confusable characters swapped, fewest swaps first.

    Returns the readings and whether they are all of them: past ``MAX_VARIANTS_PER_FIELD``
    the list is cut short, and the caller must not treat a match among them as the only one.
    """
    found = [value]
    seen = {value}
    frontier = [value]
    while frontier:
        current = frontier.pop(0)
        for index, char in enumerate(current):
            for swap in repairs.get(char.lower(), ()):
                candidate = current[:index] + swap + current[index + 1 :]
                if candidate in seen:
                    continue
                if len(found) >= MAX_VARIANTS_PER_FIELD:
                    return found, False
                seen.add(candidate)
                found.append(candidate)
                frontier.append(candidate)
    return found, True


@dataclass(frozen=True)
class Repairs:
    """The readings to try, and whether they are every reading the misreads explain."""

    candidates: list[tuple[str, dict[str, Any]]] = field(default_factory=list)
    complete: bool = True


def repair_candidates(arguments: dict[str, Any]) -> Repairs:
    """Readings of the identifiers a common misread or slip would explain, with why.

    For a document whose identifiers as read matched no one, and only when the model
    passed them as printed. Each candidate is ``(how, identifiers)``: ``fax_repair`` for
    a misread character or a middle name or initial dropped, ``name_swapped`` for first
    and last name the other way round (tried only when the printed name has no comma,
    which would say which is which). The birth date is never changed. ``complete`` is
    False when there are more readings than the caps allow: a match among those tried
    could then have a rival among those dropped, so it must not be taken as the only one.
    """
    printed = arguments.get("as_printed") or {}
    if not printed:
        return Repairs()
    base = {
        key: arguments[key]
        for key in ("first_name", "last_name", "birth_date", "mrn")
        if arguments.get(key)
    }
    first = str(base.get("first_name") or "")
    lasts, lasts_complete = _variants(str(base.get("last_name") or ""), _NAME_REPAIRS)
    firsts, firsts_complete = _variants(first, _NAME_REPAIRS)
    if len(first.split()) > 1:
        firsts.append(first.split()[0])
    mrns, mrns_complete = _variants(str(base.get("mrn") or ""), _MRN_REPAIRS)

    candidates: list[tuple[str, dict[str, Any]]] = []
    name = str(printed.get("name") or "")
    if base.get("first_name") and base.get("last_name") and name and "," not in name:
        swapped = {**base, "first_name": base["last_name"], "last_name": base["first_name"]}
        candidates.append((SWAPPED, swapped))
    repaired: list[dict[str, Any]] = []
    for last in lasts:
        for given in firsts:
            for mrn in mrns:
                identifiers = {**base, "last_name": last, "first_name": given, "mrn": mrn}
                identifiers = {key: value for key, value in identifiers.items() if value}
                if identifiers != base:
                    repaired.append(identifiers)
    # Fewest fields changed first.
    repaired.sort(
        key=lambda identifiers: sum(identifiers.get(k) != base.get(k) for k in identifiers)
    )
    candidates.extend((REPAIRED, identifiers) for identifiers in repaired)
    complete = (
        lasts_complete and firsts_complete and mrns_complete and len(candidates) <= MAX_CANDIDATES
    )
    return Repairs(candidates=candidates[:MAX_CANDIDATES], complete=complete)


__exports__ = ()
