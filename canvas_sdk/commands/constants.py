from enum import StrEnum
from typing import NotRequired

from pydantic import Field
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


__exports__ = (
    "CodeSystems",
    "Coding",
    "ClinicalQuantity",
    "ServiceProvider",
)
