from enum import StrEnum
from typing import NotRequired

from typing_extensions import TypedDict


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
