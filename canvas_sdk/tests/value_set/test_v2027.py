import ast
from pathlib import Path

import pytest

from canvas_sdk.value_set.v2026 import condition as condition_2026
from canvas_sdk.value_set.v2026 import encounter as encounter_2026
from canvas_sdk.value_set.v2027 import (
    condition,
    encounter,
    intervention,
    laboratory_test,
    no_qdm_category_assigned,
    procedure,
)
from canvas_sdk.value_set.v2027.individual_characteristic import Race
from canvas_sdk.value_set.value_set import ValueSet

V2027 = Path(__file__).parents[2] / "value_set" / "v2027"


def _code_sets() -> list[tuple[str, str, set[str]]]:
    """``(class name, code system, codes)`` for every code set in every v2027 module."""
    found = []
    for path in sorted(V2027.glob("*.py")):
        for node in ast.parse(path.read_text()).body:
            if isinstance(node, ast.ClassDef):
                for statement in node.body:
                    if (
                        isinstance(statement, ast.Assign)
                        and isinstance(statement.targets[0], ast.Name)
                        and isinstance(statement.value, ast.Set)
                    ):
                        codes = ast.literal_eval(statement.value)
                        found.append((node.name, statement.targets[0].id, codes))
    return found


@pytest.mark.parametrize(
    ("value_set", "system", "added"),
    [
        (
            procedure.Colonoscopy,
            "SNOMEDCT",
            {"174171002", "311774002", "426699005", "773128008", "773129000", "1351202006"},
        ),
        (
            laboratory_test.FecalOccultBloodTestFobt,
            "LOINC",
            {"104738-0", "107189-3", "107190-1", "107191-9"},
        ),
        (encounter.OfficeVisit, "CPT", {f"9800{n}" for n in range(8)}),
        (encounter.TelephoneVisits, "CPT", {"98979", "98980", "98981", "99457", "99458", "99470"}),
        (
            no_qdm_category_assigned.TobaccoUser,
            "SNOMEDCT",
            {"881661000124108", "881721000124105", "881731000124108"},
        ),
        (
            no_qdm_category_assigned.TobaccoNonUser,
            "SNOMEDCT",
            {"881671000124101", "881681000124103"},
        ),
        (condition.AdvancedIllness, "ICD10CM", {"G35A", "G35B0", "G35D"}),
    ],
)
def test_carries_the_v15_additions(value_set: type[ValueSet], system: str, added: set[str]) -> None:
    """Codes the 2026-05-14 release (v15 measures) added are present."""
    assert added <= getattr(value_set, system)


def test_drops_the_v15_removals() -> None:
    """Codes the 2026-05-14 release removed are absent, though v2026 has them."""
    assert "E10A2" in condition_2026.Diabetes.ICD10CM
    assert "E10A2" not in condition.Diabetes.ICD10CM
    assert "94176003" not in condition.AdvancedIllness.SNOMEDCT
    assert "98000" not in encounter_2026.OfficeVisit.CPT


def test_hospice_value_sets_carry_their_own_oids() -> None:
    """Hospice Diagnosis and the hospice library's Hospice Care Ambulatory keep distinct OIDs."""
    assert condition.HospiceDiagnosis.OID == "2.16.840.1.113883.3.464.1003.1165"
    assert encounter.HospiceEncounter.OID == "2.16.840.1.113883.3.464.1003.1003"
    assert intervention.HospiceCareAmbulatory.OID == "2.16.840.1.113883.3.526.3.1584"


def test_icd10_codes_have_no_dots() -> None:
    """ICD-10 codes match how Canvas stores them, without the dot."""
    code_sets = _code_sets()
    assert any(system == "ICD10CM" for _, system, _ in code_sets)
    dotted = {
        (name, code)
        for name, system, codes in code_sets
        if system in ("ICD10CM", "ICD10PCS")
        for code in codes
        if "." in code
    }
    assert dotted == set()


def test_race_codes_keep_their_hyphen() -> None:
    """CDC race codes are stored as ``2054-5``, so the value set must use that form."""
    assert "2054-5" in Race.CDCREC


def test_every_module_exports_its_classes() -> None:
    """Each module's ``__exports__`` lists exactly its classes, as the sandbox allowlist expects."""
    for path in V2027.glob("*.py"):
        tree = ast.parse(path.read_text())
        classes = {node.name for node in tree.body if isinstance(node, ast.ClassDef)}
        exports = next(
            set(ast.literal_eval(node.value))
            for node in tree.body
            if isinstance(node, ast.Assign)
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "__exports__"
        )
        assert classes == exports, path.name
