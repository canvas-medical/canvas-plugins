import re
from datetime import date
from enum import StrEnum
from typing import Annotated, Any, NotRequired

from pydantic import Field, PlainValidator, TypeAdapter, WithJsonSchema
from typing_extensions import TypedDict

from canvas_sdk.base import Model


class CodeSystems(StrEnum):
    """A class representing different code systems and their URLs."""

    SNOMED = "http://snomed.info/sct"
    RXNORM = "http://www.nlm.nih.gov/research/umls/rxnorm"
    LOINC = "http://loinc.org"
    FDB = "http://www.fdbhealth.com/"
    ICD10 = "ICD-10"
    CVX = "http://hl7.org/fhir/sid/cvx"
    CPT = "http://www.ama-assn.org/go/cpt"
    NUCC = "http://www.nucc.org/"
    NDC = "http://hl7.org/fhir/sid/ndc"
    HCPCS = "http://www.cms.gov/medicare/coding/medhcpcsgeninfo"
    UNITS_OF_MEASURE = "http://unitsofmeasure.org"
    FULLSCRIPT = "http://fullscript.com"
    UNSTRUCTURED = "UNSTRUCTURED"


class Coding(TypedDict):
    """Coding object in Canvas."""

    system: str
    code: str
    display: NotRequired[str]


class ClinicalQuantity(TypedDict):
    """A ClinicalQuantity for prescribe/refill commands."""

    representative_ndc: str
    ncpdp_quantity_qualifier_code: str
    description: NotRequired[str]


class ServiceProvider(Model):
    """ServiceProvider model."""

    first_name: str = Field(max_length=512)
    last_name: str = Field(max_length=512)
    specialty: str = Field(max_length=512)
    practice_name: str = Field(max_length=512)
    business_fax: str | None = Field(max_length=512, default=None)
    business_phone: str | None = Field(max_length=512, default=None)
    business_address: str | None = Field(max_length=512, default=None)
    notes: str | None = Field(max_length=512, default=None)


_PARTIAL_DATE = re.compile(r"\d{4}|\d{1,2}/\d{4}")
_DATE = TypeAdapter(date)


def _approximate_date(value: Any) -> date | str:
    """A year (``YYYY``) or month (``MM/YYYY`` or ``M/YYYY``) as a string, or else a ``date``.

    A partial date is kept as the string it was given, so Canvas can record it as the
    approximate date it is ("2023", not January 1, 2023), written the way the chart's own date
    field takes it. Any other value is read exactly as a ``date`` field reads it, so a full day,
    a midnight datetime or a timestamp comes back as a ``date``.
    """
    if isinstance(value, str) and _PARTIAL_DATE.fullmatch(value):
        month, _, year = value.rpartition("/")
        try:
            date(int(year), int(month or 1), 1)
        except ValueError as error:
            raise ValueError(f"{value!r} is not a real year or month") from error
        return value
    return _DATE.validate_python(value)


#: A field Canvas records as an approximate date: a ``date``, or a ``YYYY``, ``MM/YYYY`` or
#: ``M/YYYY`` string when only the year or the month is known.
ApproximateDate = Annotated[
    date | str,
    PlainValidator(_approximate_date),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^(\d{4}|\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2})$",
            "description": "A year (YYYY), month (MM/YYYY) or day (YYYY-MM-DD)",
        }
    ),
]


__exports__ = (
    "ApproximateDate",
    "CodeSystems",
    "Coding",
    "ClinicalQuantity",
    "ServiceProvider",
)
