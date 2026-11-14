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
import unicodedata
from collections.abc import Iterable
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
_MRN_LABEL_WORDS = frozenset({"mrn", "mr", "id", "no", "number", "chart", "pt", "patient"})
# Words that label a number printed beside the MRN that is not it.
_OTHER_NUMBER_LABELS = frozenset(
    {"acct", "account", "visit", "encounter", "enc", "fin", "csn", "room", "bed", "order", "phone"}
)
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
_DATE_LABEL = re.compile(
    r"^\s*(dob|d\.o\.b\.?|birth\s*date|date\s*of\s*birth|born)\s*[:#]?\s*", re.I
)
# A day printed as an ordinal, such as the "9th" of "March 9th, 1971".
_ORDINAL = re.compile(r"\b(\d{1,2})(st|nd|rd|th)\b")
# The read parts of a name, in the order a print shows them.
_NAME_KEYS = ("first_name", "middle_name", "last_name", "suffix")
# Generational suffixes, folded as names are, so a printed one is told from a middle name.
_SUFFIXES = frozenset(
    "".join(re.findall(r"[a-z0-9|]+", word.translate(_FOLD)))
    for word in ("jr", "sr", "ii", "iii", "iv")
)

# The most readings tried per field, and per document, fewest changed characters first.
MAX_VARIANTS_PER_FIELD = 8
MAX_CANDIDATES = 16

REPAIRED = "fax_repair"
SWAPPED = "name_swapped"


def _tokens(value: str, *, folded: bool) -> list[str]:
    """The words of ``value``, lowercased with accents stripped, so RENÉE is one word."""
    decomposed = unicodedata.normalize("NFKD", value)
    plain = "".join(char for char in decomposed if not unicodedata.combining(char)).lower()
    lowered = plain.translate(_FOLD) if folded else plain
    return re.findall(r"[a-z0-9|]+", lowered)


def _name_agrees(read: str, printed: str) -> bool:
    """Every word of the name read is printed, allowing for fax misreads."""
    shown = set(_tokens(printed, folded=True))
    return all(token in shown for token in _tokens(read, folded=True))


def _mrn_agrees(read: str, printed: str) -> bool:
    """The MRN read is the whole printed MRN, allowing for misreads.

    The print is split at label words: the text before any label, or after an MRN label,
    is an MRN, joined as "VL-4471" joins to "vl4471"; the text after a label such as ACCT
    is another number. The MRN read must equal one MRN segment whole, so part of an MRN,
    an account number, or one of two numbers printed together never agrees.
    """
    wanted = "".join(_tokens(read, folded=True))
    if not wanted:
        return False
    segments: list[tuple[bool, list[str]]] = [(True, [])]
    for token in _tokens(printed, folded=False):
        if token in _MRN_LABEL_WORDS or token in _OTHER_NUMBER_LABELS:
            segments.append((token in _MRN_LABEL_WORDS, []))
        else:
            segments[-1][1].append(token.translate(_FOLD))
    return any(is_mrn and "".join(words) == wanted for is_mrn, words in segments)


def parse_printed_date(printed: str) -> date | None:
    """The birth date as printed, read month first with a four-digit year, or None.

    Takes ``03/09/1971`` (and ``-`` or ``.``), ``1971-03-09``, ``March 9th, 1971``, and
    ``9 Mar 1971`` or ``09-MAR-1971``, after a ``DOB`` or ``Born`` label. A two-digit year
    or a date that is not one is None: it is never guessed.
    """
    shown = _ORDINAL.sub(r"\1", _DATE_LABEL.sub("", printed).strip().lower())
    numeric = shown.translate(_DATE_DIGITS)
    if match := re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", numeric):
        year, month, day = (int(part) for part in match.groups())
    elif match := re.fullmatch(r"(\d{1,2})\s*[/.-]\s*(\d{1,2})\s*[/.-]\s*(\d{4})", numeric):
        month, day, year = (int(part) for part in match.groups())
    elif match := re.fullmatch(r"([a-z]+)\.?\s+(\d{1,2}),?\s+(\d{4})", shown):
        month, day, year = _MONTHS.get(match[1], 0), int(match[2]), int(match[3])
    elif match := re.fullmatch(r"(\d{1,2})[\s-]+([a-z]+)\.?,?[\s-]+(\d{4})", shown):
        day, month, year = int(match[1]), _MONTHS.get(match[2], 0), int(match[3])
    else:
        return None
    try:
        return date(year, month, day)
    except ValueError:
        return None


def _printed_name_words(name: str) -> list[str]:
    """The words of a printed name, initials left out, folded for fax misreads."""
    return [word for word in _tokens(name, folded=True) if len(word) > 1]


def _whole_name_read(arguments: dict[str, Any], name: str) -> str | None:
    """Why the name read leaves out part of the printed name, or None when it does not.

    A name read in part matches the wrong patient: "ANN SMITH-JONES" read as last name
    "Smith" finds Ann Smith, and a first name left out finds whoever shares the last name.
    """
    if not str(arguments.get("last_name") or "").strip():
        return "The name is printed; pass the last name read."
    words = _printed_name_words(name)
    if len(words) > 1 and not str(arguments.get("first_name") or "").strip():
        return "The first name is printed; pass the first name read."
    read = set(_tokens(" ".join(str(arguments.get(key) or "") for key in _NAME_KEYS), folded=True))
    if any(word not in read for word in words):
        return "Part of the name as printed was not read; pass the whole name as printed."
    return None


def confirm_against_print(
    patient: Any, arguments: dict[str, Any], outside_mrns: Iterable[str] = ()
) -> tuple[str, int]:
    """Whether the matched ``patient``'s own record agrees with the print, and how far.

    Compares, in code and without the model's readings, the patient's last name and first
    name (or nickname) with the printed name, their birth date with the printed date, and
    their MRN, or one of ``outside_mrns`` (the current numbers other organizations keep for
    them), with the printed MRN. Any other printed name word must be the patient's
    recorded suffix or middle name, or a middle initial that agrees with it. Returns
    ``(refused, confirmed)``: why the patient is not the one printed, or empty, and how many
    printed identifiers the patient's record confirms.
    """
    printed = arguments.get("as_printed") or {}
    confirmed = 0
    if name := str(printed.get("name") or "").strip():
        if refused := _name_refused(patient, name):
            return refused, 0
        confirmed += 2
    if printed_date := str(printed.get("birth_date") or "").strip():
        if parse_printed_date(printed_date) != patient.birth_date:
            return "The matched patient's birth date does not match the print.", 0
        confirmed += 1
    if printed_mrn := str(printed.get("mrn") or "").strip():
        numbers = [patient.mrn or "", *outside_mrns]
        if not any(number and _mrn_agrees(number, printed_mrn) for number in numbers):
            return "The matched patient's MRN does not match the print.", 0
        confirmed += 1
    return "", confirmed


def _name_refused(patient: Any, name: str) -> str:
    """Why the patient's recorded name is not the printed one, or empty when it is."""
    shown = set(_tokens(name, folded=True))
    last = set(_tokens(patient.last_name or "", folded=True))
    if not last <= shown:
        return "The matched patient's last name does not match the print."
    givens = [
        set(_tokens(str(value), folded=True))
        for value in (patient.first_name, getattr(patient, "nickname", ""))
        if value
    ]
    if not any(given <= shown for given in givens):
        return "The matched patient's first name does not match the print."
    rest = shown - last - set().union(*(given for given in givens if given <= shown))
    printed_suffix = rest & _SUFFIXES
    if printed_suffix and printed_suffix != set(_tokens(patient.suffix or "", folded=True)):
        return "The matched patient's suffix does not match the print."
    middle = _tokens(patient.middle_name or "", folded=True)
    for word in rest - printed_suffix:
        if len(word) == 1 and not middle:
            continue
        if not any(part == word or (len(word) == 1 and part[0] == word) for part in middle):
            return "The matched patient's middle name does not match the print."
    return ""


def check_printed(arguments: dict[str, Any]) -> str | None:
    """Why the identifiers cannot be trusted, or None when they can.

    Refuses identifiers the model called illegible or handwritten, pages that name
    different patients, an identifier read without its printed text in ``as_printed``,
    and a value read that its printed text does not support.
    """
    if arguments.get("legibility") == "illegible":
        return "The identifiers are illegible; a person files this document."
    if arguments.get("handwritten"):
        return "The identifiers are handwritten; a person files this document."
    if arguments.get("pages_disagree"):
        return "The pages name different patients; a person files this document."
    printed = arguments.get("as_printed") or {}
    for label, read_keys, printed_key in (
        ("name", _NAME_KEYS, "name"),
        ("birth date", ("birth_date",), "birth_date"),
        ("MRN", ("mrn",), "mrn"),
    ):
        was_read = any(str(arguments.get(key) or "").strip() for key in read_keys)
        if was_read and not str(printed.get(printed_key) or "").strip():
            return f"Pass the {label} as printed in `as_printed`; it is checked against the print."
    name = str(printed.get("name") or "").strip()
    for key in _NAME_KEYS:
        read = str(arguments.get(key) or "").strip()
        if read and name and not _name_agrees(read, name):
            return f"The {key.replace('_', ' ')} read is not the name as printed."
    if name and (refused := _whole_name_read(arguments, name)):
        return refused
    mrn = str(arguments.get("mrn") or "").strip()
    printed_mrn = str(printed.get("mrn") or "").strip()
    if printed_mrn and not mrn:
        return "The MRN is printed; pass the MRN read."
    if mrn and printed_mrn and not _mrn_agrees(mrn, printed_mrn):
        return "The MRN read is not the MRN as printed."
    birth_date = str(arguments.get("birth_date") or "").strip()
    printed_date = str(printed.get("birth_date") or "").strip()
    if printed_date and not birth_date:
        return "The birth date is printed; pass the birth date read."
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
