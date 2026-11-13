import io
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[3] / "tools"))

from generate_value_sets import (  # noqa: E402
    ValueSetData,
    class_name,
    code_system_attribute,
    code_value,
    place,
    reference_layout,
    render_class,
    rows,
)

HEADER = ["CMS ID", "Value Set Name", "Value Set OID", "Code", "Code System"]


def _xlsx(sheets: dict[str, list[list[str]]]) -> bytes:
    """A minimal xlsx: a title row, then a header row, then data, using shared strings."""
    strings: list[str] = []

    def index(text: str) -> int:
        if text not in strings:
            strings.append(text)
        return strings.index(text)

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        sheet_entries, rels = [], []
        for number, (title, table) in enumerate(sheets.items(), start=1):
            xml_rows = []
            for r, row in enumerate([["Title block"], HEADER, *table], start=1):
                cells = "".join(
                    f'<c r="{chr(65 + c)}{r}" t="s"><v>{index(value)}</v></c>'
                    for c, value in enumerate(row)
                )
                xml_rows.append(f'<row r="{r}">{cells}</row>')
            archive.writestr(
                f"xl/worksheets/sheet{number}.xml",
                '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                f"<sheetData>{''.join(xml_rows)}</sheetData></worksheet>",
            )
            sheet_entries.append(f'<sheet name="{title}" sheetId="{number}" r:id="rId{number}"/>')
            rels.append(
                f'<Relationship Id="rId{number}" Target="worksheets/sheet{number}.xml" '
                'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet"/>'
            )
        archive.writestr(
            "xl/workbook.xml",
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            f"<sheets>{''.join(sheet_entries)}</sheets></workbook>",
        )
        archive.writestr(
            "xl/_rels/workbook.xml.rels",
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            f"{''.join(rels)}</Relationships>",
        )
        archive.writestr(
            "xl/sharedStrings.xml",
            '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            + "".join(f"<si><t>{text}</t></si>" for text in strings)
            + "</sst>",
        )
    return buffer.getvalue()


def _value_set(oid: str, name: str, *categories: str) -> ValueSetData:
    return ValueSetData(
        oid=oid,
        name=name,
        definition_version="20200101",
        expansion_version="eCQM Update 2026-05-14",
        purpose={"Clinical Focus": "Focus."},
        categories=set(categories),
    )


def test_rows_reads_each_sheet_after_its_header() -> None:
    """Rows come from every sheet, skipping the title block above the header."""
    workbook = _xlsx(
        {
            "Encounter": [["CMS122v15", "Office Visit", "1.2.3", "99213", "CPT"]],
            "Laboratory Test": [["CMS122v15", "HbA1c Laboratory Test", "4.5.6", "4548-4", "LOINC"]],
        }
    )
    assert [(sheet, row["Value Set OID"], row["Code"]) for sheet, row in rows(workbook)] == [
        ("Encounter", "1.2.3", "99213"),
        ("Laboratory Test", "4.5.6", "4548-4"),
    ]


def test_naming_follows_earlier_packages() -> None:
    """Class names, code system attributes, and ICD-10 codes match the v2026 conventions."""
    assert class_name("HbA1c Laboratory Test") == "Hba1CLaboratoryTest"
    assert class_name("Fecal Occult Blood Test (FOBT)") == "FecalOccultBloodTestFobt"
    assert code_system_attribute("HCPCS Level II") == "HCPCSLEVELII"
    assert code_system_attribute("PresentOnAdmission") == "PresentOnAdmission"
    assert code_value("ICD10CM", "R26.2") == "R262"
    assert code_value("CDCREC", "2054-5") == "2054-5"


def test_place_keeps_reference_locations_and_names(tmp_path: Path) -> None:
    """Known value sets keep every module and name they had; new ones go to their category."""
    (tmp_path / "communication.py").write_text('class SeverityLevel(ValueSet):\n    OID = "1.1"\n')
    (tmp_path / "no_qdm_category_assigned.py").write_text(
        'class SeverityLevel(ValueSet):\n    OID = "1.1"\n'
    )
    placed = place(
        {
            "1.1": _value_set("1.1", "Severity Level", "No QDM Category Assigned"),
            "2.2": _value_set("2.2", "New Thing", "Procedure", "No QDM Category Assigned"),
        },
        reference_layout(tmp_path),
    )
    assert {module: [name for name, _ in entries] for module, entries in placed.items()} == {
        "communication": ["SeverityLevel"],
        "no_qdm_category_assigned": ["SeverityLevel"],
        "procedure": ["NewThing"],
    }


def test_place_ignores_a_reference_class_carrying_another_oid(tmp_path: Path) -> None:
    """A reference class that borrowed another value set's OID does not claim it."""
    (tmp_path / "encounter.py").write_text('class HospiceEncounter(ValueSet):\n    OID = "3.3"\n')
    (tmp_path / "condition.py").write_text('class HospiceDiagnosis(ValueSet):\n    OID = "3.3"\n')
    placed = place(
        {
            "3.3": _value_set("3.3", "Hospice Encounter", "Encounter"),
            "4.4": _value_set("4.4", "Hospice Diagnosis", "Condition-Diagnosis-Problem"),
        },
        reference_layout(tmp_path),
    )
    assert [(name, vs.oid) for name, vs in placed["encounter"]] == [("HospiceEncounter", "3.3")]
    assert [(name, vs.oid) for name, vs in placed["condition"]] == [("HospiceDiagnosis", "4.4")]


def test_place_disambiguates_value_sets_sharing_a_name() -> None:
    """Two value sets with the same name in one module get distinct class names."""
    placed = place(
        {
            "5.15": _value_set("5.15", "Hospice Care Ambulatory", "Intervention"),
            "6.1584": _value_set("6.1584", "Hospice Care Ambulatory", "Intervention"),
        },
        {},
    )
    assert sorted(name for name, _ in placed["intervention"]) == [
        "HospiceCareAmbulatory",
        "HospiceCareAmbulatory1584",
    ]


def test_render_class_is_valid_python() -> None:
    """A rendered class compiles and lists codes sorted with their descriptions."""
    value_set = _value_set("1.2", "Office Visit", "Encounter")
    value_set.measures = {"CMS125v15", "CMS122v15"}
    value_set.codes["CPT"] = {"99213": "Office visit", "99212": 'Visit with "quotes"'}
    source = render_class("OfficeVisit", value_set)
    namespace: dict[str, object] = {"ValueSet": object}
    exec(compile(source, "<rendered>", "exec"), namespace)
    assert {"99212", "99213"} == vars(namespace["OfficeVisit"])["CPT"]
    assert "**Used in:** CMS122v15, CMS125v15" in source
    assert source.index('"99212"') < source.index('"99213"')
