import re
from datetime import date, datetime
from enum import StrEnum
from typing import Annotated, Any, NotRequired

from pydantic import Field, PlainValidator, WithJsonSchema
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


_PARTIAL_DATE = re.compile(r"\d{4}(?:-\d{2}(?:-\d{2})?)?")


def _approximate_date(value: Any) -> date | str:
    """A date, or a year (``YYYY``), month (``YYYY-MM``) or day (``YYYY-MM-DD``) as a string.

    A partial date is kept as the string it was given, so Canvas can record it as the
    approximate date it is ("2023", not January 1, 2023) the way the chart's own date field does.
    """
    if isinstance(value, datetime):
        if value.time() != datetime.min.time():
            raise ValueError("an approximate date must have no time")
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        text = value.strip()
        if _PARTIAL_DATE.fullmatch(text):
            year, month, day = (int(part) for part in (text.split("-") + ["1", "1"])[:3])
            try:
                date(year, month, day)
            except ValueError as error:
                raise ValueError(f"{text!r} is not a real date") from error
            return text
    raise ValueError(
        "an approximate date must be a date, or a year (YYYY), month (YYYY-MM) or day (YYYY-MM-DD)"
    )


#: A field Canvas records as an approximate date: a ``date``, or a ``YYYY``, ``YYYY-MM`` or
#: ``YYYY-MM-DD`` string when only part of the date is known.
ApproximateDate = Annotated[
    date | str,
    PlainValidator(_approximate_date),
    WithJsonSchema(
        {
            "type": "string",
            "pattern": r"^\d{4}(-\d{2}(-\d{2})?)?$",
            "description": "A year (YYYY), month (YYYY-MM) or day (YYYY-MM-DD)",
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
