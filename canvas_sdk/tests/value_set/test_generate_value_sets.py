import io
import sys
import zipfile
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).parents[3] / "tools"))

import generate_value_sets  # noqa: E402
from generate_value_sets import (  # noqa: E402
    ValueSetData,
    class_name,
    code_system_attribute,
    code_value,
    download_workbook,
    login,
    main,
    measure_sort_key,
    parse,
    place,
    reference_layout,
    render_class,
    rows,
    sheets,
    write_package,
)

HEADER = ["CMS ID", "Value Set Name", "Value Set OID", "Code", "Code System"]


def _xlsx(sheets: dict[str, list[list[str]]], header: list[str] = HEADER) -> bytes:
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
            for r, row in enumerate([["Title block"], header, *table], start=1):
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


CATEGORY_HEADER = [
    "CMS ID",
    "Value Set Name",
    "Value Set OID",
    "Definition Version",
    "Expansion Version",
    "Purpose: Clinical Focus",
    "Purpose: Data Element Scope",
    "Purpose: Inclusion Criteria",
    "Purpose: Exclusion Criteria",
    "Code",
    "Description",
    "Code System",
]


class _Response(io.BytesIO):
    """A stand-in for the object ``urllib.request.urlopen`` returns."""

    def __init__(self, body: bytes, headers: dict[str, str] | None = None) -> None:
        super().__init__(body)
        self.headers = headers or {}


def _category_row(oid: str, name: str, code: str, description: str, system: str) -> list[str]:
    return [
        "CMS122v15",
        name,
        oid,
        "20250101",
        "eCQM Update 2026-05-14",
        "Focus.",
        "Scope.",
        "",
        "",
        code,
        description,
        system,
    ]


def test_sheets_reads_inline_strings_numbers_and_gaps() -> None:
    """Inline strings, raw values, and empty cells are read; skipped columns become blanks."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(
            "xl/worksheets/sheet1.xml",
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<sheetData><row r="1">'
            '<c r="A1" t="inlineStr"><is><t>inline</t></is></c>'
            '<c r="C1"><v>42</v></c>'
            '<c r="D1"/>'
            '</row><row r="2"/></sheetData></worksheet>',
        )
        archive.writestr(
            "xl/workbook.xml",
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            '<sheets><sheet name="Only" sheetId="1" r:id="rId1"/></sheets></workbook>',
        )
        archive.writestr(
            "xl/_rels/workbook.xml.rels",
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Target="/xl/worksheets/sheet1.xml"/></Relationships>',
        )
    assert list(sheets(buffer.getvalue())) == [("Only", [["inline", "", "42", ""], []])]


def test_parse_collects_categories_measures_and_codes() -> None:
    """Both workbooks feed one value set; measure rows for unknown OIDs are ignored."""
    category = _xlsx(
        {
            "Encounter": [
                _category_row("1.2", "Office Visit", "99213", "Office  visit\n", "CPT"),
                [],
            ],
            "No QDM Category Assigned": [
                _category_row("1.2", "Office Visit", "R26.2", "", "ICD10CM"),
            ],
        },
        header=CATEGORY_HEADER,
    )
    measures = _xlsx(
        {
            "CMS125v15": [
                ["CMS125v15", "Office Visit", "1.2", "99213", "CPT"],
                ["CMS125v15", "Unknown", "9.9", "1", "CPT"],
            ]
        }
    )
    value_sets = parse(category, measures)
    assert list(value_sets) == ["1.2"]
    office_visit = value_sets["1.2"]
    assert office_visit.categories == {"Encounter", "No QDM Category Assigned"}
    assert office_visit.measures == {"CMS122v15", "CMS125v15"}
    assert office_visit.codes == {"CPT": {"99213": "Office visit"}, "ICD10CM": {"R262": ""}}
    assert office_visit.purpose["Clinical Focus"] == "Focus."
    assert office_visit.purpose["Exclusion Criteria"] == ""


def test_login_returns_the_session_token(monkeypatch: pytest.MonkeyPatch) -> None:
    """A successful login hands back the Authorization header VSAC returns."""
    requests: list[Any] = []

    def urlopen(request: Any) -> _Response:
        requests.append(request)
        return _Response(b'{"status": "true"}', {"Authorization": "token-1"})

    monkeypatch.setattr(generate_value_sets.urllib.request, "urlopen", urlopen)
    assert login("key with space") == "token-1"
    assert requests[0].data == b"apikey=key%20with%20space"
    assert requests[0].get_method() == "POST"


def test_login_rejects_a_bad_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """A rejected key stops the script with VSAC's response."""
    monkeypatch.setattr(
        generate_value_sets.urllib.request,
        "urlopen",
        lambda request: _Response(b'{"status": "false"}'),
    )
    with pytest.raises(SystemExit, match="VSAC rejected the API key"):
        login("bad")


def test_download_workbook_unzips_the_spreadsheet(monkeypatch: pytest.MonkeyPatch) -> None:
    """The xlsx inside VSAC's zip is returned, fetched with the session token."""
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w") as zipped:
        zipped.writestr("readme.txt", "ignored")
        zipped.writestr("value_sets.xlsx", b"xlsx-bytes")
    requests: list[Any] = []

    def urlopen(request: Any) -> _Response:
        requests.append(request)
        return _Response(archive.getvalue())

    monkeypatch.setattr(generate_value_sets.urllib.request, "urlopen", urlopen)
    assert download_workbook("token-1", "category", "20260514") == b"xlsx-bytes"
    assert requests[0].full_url.endswith("/groupby/category/version/20260514")
    assert requests[0].get_header("Authorization") == "token-1"


def test_write_package_writes_importable_modules(tmp_path: Path) -> None:
    """Each module is valid Python whose ``__exports__`` lists its classes in order."""
    first = _value_set("1.1", "Office Visit", "Encounter")
    first.codes["CPT"] = {"99213": "Office visit"}
    second = _value_set("2.2", "Annual Wellness Visit", "Encounter")
    write_package(
        tmp_path / "v2099",
        {"encounter": [("OfficeVisit", first), ("AnnualWellnessVisit", second)]},
    )
    assert (tmp_path / "v2099" / "__init__.py").read_text() == "__exports__ = ()\n"
    source = (tmp_path / "v2099" / "encounter.py").read_text()
    namespace: dict[str, Any] = {}
    runnable = source.replace("from ..value_set import ValueSet", "ValueSet = object")
    exec(compile(runnable, "<encounter>", "exec"), namespace)
    assert namespace["__exports__"] == ("AnnualWellnessVisit", "OfficeVisit")
    assert namespace["OfficeVisit"].CPT == {"99213"}


def test_naming_edge_cases() -> None:
    """Digit-led names get a prefix, unknown measure ids sort last, no reference maps nothing."""
    assert class_name("2 Hour Glucose") == "VS2HourGlucose"
    assert sorted(["Other", "CMS1028v4", "CMS122v15"], key=measure_sort_key) == [
        "CMS122v15",
        "CMS1028v4",
        "Other",
    ]
    assert reference_layout(None) == {}


def test_main_requires_an_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Without UMLS_API_KEY the script exits before touching the network."""
    monkeypatch.delenv("UMLS_API_KEY", raising=False)
    monkeypatch.setattr(
        sys, "argv", ["generate_value_sets.py", "--release", "20260514", "--year", "2027"]
    )
    with pytest.raises(SystemExit, match="UMLS_API_KEY"):
        main()


def test_main_downloads_parses_and_writes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The script logs in, downloads both groupings, and writes the package to ``--output``."""
    category = _xlsx(
        {"Encounter": [_category_row("1.2", "Office Visit", "99213", "Office visit", "CPT")]},
        header=CATEGORY_HEADER,
    )
    measures = _xlsx({"CMS125v15": [["CMS125v15", "Office Visit", "1.2", "99213", "CPT"]]})
    downloads: list[tuple[str, str, str]] = []

    def download(token: str, group_by: str, release: str) -> bytes:
        downloads.append((token, group_by, release))
        return category if group_by == "category" else measures

    monkeypatch.setenv("UMLS_API_KEY", "key")
    monkeypatch.setattr(generate_value_sets, "login", lambda api_key: f"token-for-{api_key}")
    monkeypatch.setattr(generate_value_sets, "download_workbook", download)
    output = tmp_path / "v2099"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "generate_value_sets.py",
            "--release",
            "20260514",
            "--year",
            "2099",
            "--reference",
            str(tmp_path / "missing"),
            "--output",
            str(output),
        ],
    )
    main()
    assert downloads == [
        ("token-for-key", "category", "20260514"),
        ("token-for-key", "cms", "20260514"),
    ]
    assert "class OfficeVisit(ValueSet):" in (output / "encounter.py").read_text()
    assert capsys.readouterr().out == f"Wrote 1 value sets in 1 modules to {output}\n"
