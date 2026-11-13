#!/usr/bin/env python3
"""Generate a ``canvas_sdk.value_set.v<year>`` package from a VSAC eCQM release.

Downloads the VSAC "eCQM Value Sets" spreadsheets for every program (eligible
clinicians plus hospital inpatient and outpatient) of one release, grouped by QDM
category and by CMS measure, and writes one module per QDM category.

A release published in May serves the following year's performance period, so the
2026-05-14 release (the v15 measures) generates ``v2027``.

Value sets that exist in the reference package keep its class name and module, so a
plugin upgrades by changing only the package in its import path.

Usage::

    UMLS_API_KEY=... tools/generate_value_sets.py --release 20260514 --year 2027

The API key comes from a UMLS Terminology Services account (https://uts.nlm.nih.gov).
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import zipfile
from collections import defaultdict
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from xml.etree import ElementTree

VSAC = "https://vsac.nlm.nih.gov/vsac"
XLSX = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
RELS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
CONTENT = "ec_hospip_hospop"

CATEGORY_MODULES = {
    "Adverse Event": "adverse_event",
    "Allergy-Intolerance": "allergy",
    "Assessment": "assessment",
    "Care Goal": "care_goal",
    "Communication": "communication",
    "Condition-Diagnosis-Problem": "condition",
    "Device": "device",
    "Diagnostic Study": "diagnostic_study",
    "Encounter": "encounter",
    "Family History": "family_history",
    "Immunization": "immunization",
    "Individual Characteristic": "individual_characteristic",
    "Intervention": "intervention",
    "Laboratory Test": "laboratory_test",
    "Medication": "medication",
    "No QDM Category Assigned": "no_qdm_category_assigned",
    "Participation": "participation",
    "Physical Exam": "physical_exam",
    "Procedure": "procedure",
    "Substance": "substance",
    "Symptom": "symptom",
}
NO_CATEGORY = "No QDM Category Assigned"

REPO_ROOT = Path(__file__).resolve().parent.parent
VALUE_SET_ROOT = REPO_ROOT / "canvas_sdk" / "value_set"


@dataclass
class ValueSetData:
    """Everything the generated class records about one value set."""

    oid: str
    name: str
    definition_version: str
    expansion_version: str
    purpose: dict[str, str]
    categories: set[str] = field(default_factory=set)
    measures: set[str] = field(default_factory=set)
    codes: dict[str, dict[str, str]] = field(default_factory=lambda: defaultdict(dict))


def login(api_key: str) -> str:
    """Exchange a UMLS API key for a VSAC session token."""
    request = urllib.request.Request(
        f"{VSAC}/login/byApikey",
        data=f"apikey={urllib.parse.quote(api_key)}".encode(),
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request) as response:
        body = json.load(response)
        token = response.headers.get("Authorization")
    if body.get("status") != "true" or not token:
        raise SystemExit(f"VSAC rejected the API key: {body}")
    return token


def download_workbook(token: str, group_by: str, release: str) -> bytes:
    """Download one release spreadsheet (zipped by VSAC) and return the xlsx bytes."""
    url = (
        f"{VSAC}/pc/measure/download/resource/ecqm/format/excel"
        f"/content/{CONTENT}/groupby/{group_by}/version/{release}"
    )
    request = urllib.request.Request(url, headers={"Authorization": token})
    with urllib.request.urlopen(request) as response:
        archive = zipfile.ZipFile(io.BytesIO(response.read()))
    (name,) = [n for n in archive.namelist() if n.endswith(".xlsx")]
    return archive.read(name)


def sheets(workbook_bytes: bytes) -> Iterator[tuple[str, list[list[str]]]]:
    """Yield ``(sheet title, rows of cell text)`` from an xlsx file, using only the stdlib."""
    archive = zipfile.ZipFile(io.BytesIO(workbook_bytes))
    names = set(archive.namelist())
    shared: list[str] = []
    if "xl/sharedStrings.xml" in names:
        for item in ElementTree.fromstring(archive.read("xl/sharedStrings.xml")).iter(f"{XLSX}si"):
            shared.append("".join(text.text or "" for text in item.iter(f"{XLSX}t")))
    targets = {
        rel.attrib["Id"]: rel.attrib["Target"].lstrip("/").removeprefix("xl/")
        for rel in ElementTree.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    }
    workbook = ElementTree.fromstring(archive.read("xl/workbook.xml"))
    for sheet in workbook.iter(f"{XLSX}sheet"):
        path = f"xl/{targets[sheet.attrib[f'{RELS}id']]}"
        table = []
        for row in ElementTree.fromstring(archive.read(path)).iter(f"{XLSX}row"):
            cells: dict[int, str] = {}
            for cell in row.iter(f"{XLSX}c"):
                kind = cell.get("t")
                if kind == "inlineStr":
                    text = "".join(t.text or "" for t in cell.iter(f"{XLSX}t"))
                else:
                    value = cell.find(f"{XLSX}v")
                    text = "" if value is None or value.text is None else value.text
                    if kind == "s":
                        text = shared[int(text)]
                cells[column_index(cell.attrib["r"])] = text
            table.append([cells.get(i, "") for i in range(max(cells, default=-1) + 1)])
        yield sheet.attrib["name"], table


def column_index(reference: str) -> int:
    """``C7`` -> 2: the zero-based column of a cell reference."""
    index = 0
    for letter in reference.rstrip("0123456789"):
        index = index * 26 + ord(letter) - ord("A") + 1
    return index - 1


def rows(workbook_bytes: bytes) -> Iterator[tuple[str, dict[str, str]]]:
    """Yield ``(sheet title, row dict)`` for every code row of a release spreadsheet.

    Each sheet starts with a title block; the header row is the one starting with ``CMS ID``.
    """
    for title, table in sheets(workbook_bytes):
        header = None
        for row in table:
            if header is None:
                if row and row[0] == "CMS ID":
                    header = row
                continue
            if row and row[0]:
                yield title, dict(zip(header, row, strict=False))


def parse(category_bytes: bytes, measure_bytes: bytes) -> dict[str, ValueSetData]:
    """Collect value sets, their QDM categories, measures, and codes from both workbooks."""
    value_sets: dict[str, ValueSetData] = {}
    for sheet, row in rows(category_bytes):
        oid = row["Value Set OID"]
        value_set = value_sets.get(oid)
        if value_set is None:
            value_set = value_sets[oid] = ValueSetData(
                oid=oid,
                name=row["Value Set Name"],
                definition_version=str(row["Definition Version"]),
                expansion_version=row["Expansion Version"],
                purpose={
                    "Clinical Focus": row["Purpose: Clinical Focus"] or "",
                    "Data Element Scope": row["Purpose: Data Element Scope"] or "",
                    "Inclusion Criteria": row["Purpose: Inclusion Criteria"] or "",
                    "Exclusion Criteria": row["Purpose: Exclusion Criteria"] or "",
                },
            )
        value_set.categories.add(sheet)
        value_set.measures.add(row["CMS ID"])
        system = code_system_attribute(row["Code System"])
        value_set.codes[system][code_value(system, row["Code"])] = clean(row["Description"] or "")
    for _, row in rows(measure_bytes):
        if row["Value Set OID"] in value_sets:
            value_sets[row["Value Set OID"]].measures.add(row["CMS ID"])
    return value_sets


def code_system_attribute(code_system: str) -> str:
    """The class attribute holding a code system's codes.

    Multi-word names are joined and uppercased (``HCPCS Level II`` -> ``HCPCSLEVELII``); single
    names are kept as VSAC spells them (``SNOMEDCT``, ``PresentOnAdmission``).
    """
    if " " in code_system:
        return re.sub(r"[^A-Z0-9]", "", code_system.upper())
    return code_system


def code_value(system: str, code: object) -> str:
    """ICD-10 codes are stored without the dot (``R26.2`` -> ``R262``), as Canvas records them."""
    value = str(code).strip()
    return value.replace(".", "") if system in ("ICD10CM", "ICD10PCS") else value


def clean(text: str) -> str:
    """Collapse whitespace so a description fits on one comment line."""
    return re.sub(r"\s+", " ", str(text)).strip()


def class_name(value_set_name: str) -> str:
    """``HbA1c Laboratory Test`` -> ``Hba1CLaboratoryTest``, the convention of earlier packages."""
    name = re.sub(r"[^A-Za-z0-9]", "", value_set_name.title())
    return f"VS{name}" if name[:1].isdigit() else name


def reference_layout(reference: Path | None) -> dict[str, list[tuple[str, str]]]:
    """Map each OID in the reference package to every ``(module, class name)`` it appears as."""
    layout: dict[str, list[tuple[str, str]]] = defaultdict(list)
    if reference is None:
        return layout
    class_pattern = re.compile(r"^class (\w+)\(ValueSet\):")
    oid_pattern = re.compile(r'^\s+OID = "([^"]+)"')
    for path in sorted(reference.glob("*.py")):
        current = None
        for line in path.read_text().splitlines():
            if match := class_pattern.match(line):
                current = match.group(1)
            elif current and (match := oid_pattern.match(line)):
                layout[match.group(1)].append((path.stem, current))
                current = None
    return layout


def place(
    value_sets: dict[str, ValueSetData],
    layout: dict[str, list[tuple[str, str]]],
) -> dict[str, list[tuple[str, ValueSetData]]]:
    """Assign every value set its modules and a class name unique within each module.

    Value sets in the reference package keep every module and class name they had there.
    When a reference OID appears under several class names, only the classes named after the
    value set keep it, so a reference class carrying another value set's OID by mistake does
    not claim it. New value sets go to their QDM category's module under a name derived from
    the value set name.
    """
    placed: dict[str, list[tuple[str, ValueSetData]]] = defaultdict(list)
    taken: dict[str, set[str]] = defaultdict(set)
    ordered = sorted(value_sets.values(), key=lambda vs: (vs.oid not in layout, vs.name, vs.oid))
    for value_set in ordered:
        locations = [
            (module, name)
            for module, name in layout.get(value_set.oid, [])
            if class_name(value_set.name) == name or len(layout[value_set.oid]) == 1
        ]
        if not locations:
            categories = sorted(value_set.categories - {NO_CATEGORY}) or [NO_CATEGORY]
            locations = [(CATEGORY_MODULES[categories[0]], class_name(value_set.name))]
        for module, name in locations:
            if name in taken[module]:
                name = f"{name}{value_set.oid.rsplit('.', 1)[-1]}"
            taken[module].add(name)
            placed[module].append((name, value_set))
    return placed


def render_class(name: str, value_set: ValueSetData) -> str:
    """Render one ValueSet subclass in the house format."""
    lines = [f"class {name}(ValueSet):", '    """']
    for label, text in value_set.purpose.items():
        lines += [f"    **{label}:** {clean(text)}", ""]
    lines += [
        f"    **Used in:** {', '.join(sorted(value_set.measures, key=measure_sort_key))}",
        '    """',
        "",
    ]
    lines += [
        f"    VALUE_SET_NAME = {json.dumps(value_set.name)}",
        f'    OID = "{value_set.oid}"',
        f'    DEFINITION_VERSION = "{value_set.definition_version}"',
        f'    EXPANSION_VERSION = "{value_set.expansion_version}"',
    ]
    for system in sorted(value_set.codes):
        lines += ["", f"    {system} = {{"]
        for code, description in sorted(value_set.codes[system].items()):
            comment = f"  # {description}" if description else ""
            lines.append(f"        {json.dumps(code)},{comment}")
        lines.append("    }")
    return "\n".join(lines)


def measure_sort_key(measure: str) -> tuple[int, int]:
    """Order ``CMS122v15`` before ``CMS1028v4`` numerically."""
    match = re.match(r"CMS(\d+)v(\d+)", measure)
    return (int(match.group(1)), int(match.group(2))) if match else (sys.maxsize, 0)


def write_package(output: Path, placed: dict[str, list[tuple[str, ValueSetData]]]) -> None:
    """Write ``__init__.py`` plus one module per QDM category."""
    output.mkdir(parents=True, exist_ok=True)
    (output / "__init__.py").write_text("__exports__ = ()\n")
    for module, entries in sorted(placed.items()):
        entries.sort(key=lambda entry: entry[0])
        body = "\n\n\n".join(render_class(name, value_set) for name, value_set in entries)
        exports = "".join(f'    "{name}",\n' for name, _ in entries)
        (output / f"{module}.py").write_text(
            f"from ..value_set import ValueSet\n\n\n{body}\n\n\n__exports__ = (\n{exports})\n"
        )


def main() -> None:
    """Parse arguments, download the release, and write the package."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--release", required=True, help="VSAC release date, e.g. 20260514")
    parser.add_argument("--year", required=True, type=int, help="performance year, e.g. 2027")
    parser.add_argument(
        "--reference",
        type=Path,
        help="package whose class names and modules to keep (default: the previous year's)",
    )
    parser.add_argument("--output", type=Path, help="default: canvas_sdk/value_set/v<year>")
    args = parser.parse_args()

    api_key = os.environ.get("UMLS_API_KEY")
    if not api_key:
        raise SystemExit("Set UMLS_API_KEY to a UMLS Terminology Services API key.")

    reference = args.reference or VALUE_SET_ROOT / f"v{args.year - 1}"
    output = args.output or VALUE_SET_ROOT / f"v{args.year}"

    token = login(api_key)
    value_sets = parse(
        download_workbook(token, "category", args.release),
        download_workbook(token, "cms", args.release),
    )
    placed = place(value_sets, reference_layout(reference if reference.is_dir() else None))
    write_package(output, placed)
    total = sum(len(entries) for entries in placed.values())
    print(f"Wrote {total} value sets in {len(placed)} modules to {output}")


if __name__ == "__main__":
    main()
