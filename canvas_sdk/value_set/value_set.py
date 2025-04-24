from collections import defaultdict
from typing import Union, cast

from django.utils.functional import classproperty


class CodeConstants:
    """A class representing different code systems and their URLs."""

    CPT = "CPT"
    HCPCS = "HCPCS"
    HCPCSLEVELII = "HCPCSLEVELII"
    CVX = "CVX"
    LOINC = "LOINC"
    SNOMEDCT = "SNOMEDCT"
    FDB = "FDB"
    RXNORM = "RXNORM"
    ICD10CM = "ICD10CM"
    ICD10PCS = "ICD10PCS"
    NUCC = "NUCC"
    CANVAS = "CANVAS"
    INTERNAL = "INTERNAL"
    NDC = "NDC"

    URL_CPT = "http://www.ama-assn.org/go/cpt"
    URL_HCPCS = "http://www.cms.gov/medicare/coding/medhcpcsgeninfo"
    URL_HCPCSLEVELII = "https://coder.aapc.com/hcpcs-codes"
    URL_CVX = "http://hl7.org/fhir/sid/cvx"
    URL_LOINC = "http://loinc.org"
    URL_SNOMEDCT = "http://snomed.info/sct"
    URL_FDB = "http://www.fdbhealth.com/"
    URL_RXNORM = "http://www.nlm.nih.gov/research/umls/rxnorm"
    URL_ICD10 = "ICD-10"
    URL_NUCC = "http://www.nucc.org/"
    URL_CANVAS = "CANVAS"
    URL_INTERNAL = "INTERNAL"
    URL_NDC = "http://hl7.org/fhir/sid/ndc"


class CodeConstantsURLMappingMixin:
    """A class that maps code systems to their URLs."""

    CODE_SYSTEM_MAPPING = {
        CodeConstants.CPT: CodeConstants.URL_CPT,
        CodeConstants.HCPCS: CodeConstants.URL_HCPCS,
        CodeConstants.HCPCSLEVELII: CodeConstants.URL_HCPCSLEVELII,
        CodeConstants.CVX: CodeConstants.URL_CVX,
        CodeConstants.LOINC: CodeConstants.URL_LOINC,
        CodeConstants.SNOMEDCT: CodeConstants.URL_SNOMEDCT,
        CodeConstants.FDB: CodeConstants.URL_FDB,
        CodeConstants.RXNORM: CodeConstants.URL_RXNORM,
        CodeConstants.ICD10CM: CodeConstants.URL_ICD10,
        CodeConstants.ICD10PCS: CodeConstants.URL_ICD10,
        CodeConstants.NUCC: CodeConstants.URL_NUCC,
        CodeConstants.CANVAS: CodeConstants.URL_CANVAS,
        CodeConstants.INTERNAL: CodeConstants.URL_INTERNAL,
        CodeConstants.NDC: CodeConstants.URL_NDC,
    }


class CombinedValueSet(CodeConstantsURLMappingMixin):
    """A class representing a combination of two value sets."""

    def __init__(
        self,
        value_set_1: Union[type["ValueSet"], "CombinedValueSet"],
        value_set_2: Union[type["ValueSet"], "CombinedValueSet"],
    ) -> None:
        self.value_set_1 = value_set_1
        self.value_set_2 = value_set_2

    @property
    def values(self) -> dict[str, set]:
        """A property that returns the combined values from both value sets."""
        values: dict[str, set] = defaultdict(set)

        for vs in [self.value_set_1, self.value_set_2]:
            sub_values = vs.values

            for key in sub_values:
                values[key] |= sub_values[key]

        return values

    def __or__(self, value_set: Union[type["ValueSet"], "CombinedValueSet"]) -> "CombinedValueSet":
        """Implements the `|` (or) operator to combine value sets."""
        return CombinedValueSet(self, value_set)


class ValueSystems(type):
    """A metaclass for defining a ValueSet."""

    def __or__(self, value_set: Union[type["ValueSet"], "CombinedValueSet"]) -> "CombinedValueSet":  # type: ignore[override]
        """Implements the `|` (or) operator."""
        return CombinedValueSet(cast(type["ValueSet"], self), value_set)

    def __ror__(self, value_set: Union[type["ValueSet"], "CombinedValueSet"]) -> "CombinedValueSet":  # type: ignore[override]
        """Implements the `|` (or) operator."""
        return self.__or__(value_set)


class ValueSet(CodeConstantsURLMappingMixin, metaclass=ValueSystems):
    """The Base class for a ValueSet."""

    @classproperty
    def values(cls) -> dict[str, set[str]]:
        """A property that returns a dictionary of code systems and their associated values."""
        return {
            system: getattr(cls, system)
            for system in cls.CODE_SYSTEM_MAPPING
            if hasattr(cls, system)
        }


__exports__ = (
    "CodeConstants",
    "CodeConstantsURLMappingMixin",
    "CombinedValueSet",
    "ValueSystems",
    "ValueSet",
)
