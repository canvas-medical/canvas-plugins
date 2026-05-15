import json

import pytest
from pydantic import ValidationError

from canvas_sdk.effects.base import EffectType
from canvas_sdk.effects.patient_chart_summary_configuration import PatientChartSummaryConfiguration

Section = PatientChartSummaryConfiguration.Section
CustomSection = PatientChartSummaryConfiguration.CustomSection


def test_effect_type() -> None:
    """Effect type must be SHOW_PATIENT_CHART_SUMMARY_SECTIONS."""
    assert (
        PatientChartSummaryConfiguration.Meta.effect_type
        == EffectType.SHOW_PATIENT_CHART_SUMMARY_SECTIONS
    )


def test_section_enum_values() -> None:
    """Section enum must have the expected string values."""
    assert Section.SOCIAL_DETERMINANTS.value == "social_determinants"
    assert Section.GOALS.value == "goals"
    assert Section.CONDITIONS.value == "conditions"
    assert Section.MEDICATIONS.value == "medications"
    assert Section.ALLERGIES.value == "allergies"
    assert Section.CARE_TEAMS.value == "care_teams"
    assert Section.VITALS.value == "vitals"
    assert Section.IMMUNIZATIONS.value == "immunizations"
    assert Section.SURGICAL_HISTORY.value == "surgical_history"
    assert Section.FAMILY_HISTORY.value == "family_history"
    assert Section.CODING_GAPS.value == "coding_gaps"


def test_custom_section_stores_name() -> None:
    """CustomSection must store its name."""
    section = CustomSection(name="my_section")
    assert section.name == "my_section"


def test_empty_sections_raises() -> None:
    """An empty sections list must raise a ValidationError."""
    with pytest.raises(ValidationError, match="at least 1"):
        PatientChartSummaryConfiguration(sections=[])


def test_single_builtin_section_payload() -> None:
    """A single built-in section must serialize with custom=False."""
    config = PatientChartSummaryConfiguration(sections=[Section.MEDICATIONS])
    assert config.values == {"sections": [{"custom": False, "key": "medications"}]}


def test_multiple_builtin_sections_payload() -> None:
    """Multiple built-in sections must serialize in order."""
    config = PatientChartSummaryConfiguration(
        sections=[Section.ALLERGIES, Section.CONDITIONS, Section.VITALS]
    )
    payload = json.loads(config.apply().payload)
    assert payload == {
        "data": {
            "sections": [
                {"custom": False, "key": "allergies"},
                {"custom": False, "key": "conditions"},
                {"custom": False, "key": "vitals"},
            ]
        }
    }


def test_single_custom_section_payload() -> None:
    """A custom section must serialize with custom=True and its name as key."""
    config = PatientChartSummaryConfiguration(sections=[CustomSection(name="my_section")])
    assert config.values == {"sections": [{"custom": True, "key": "my_section"}]}


def test_multiple_custom_sections_payload() -> None:
    """Multiple custom sections must all serialize correctly."""
    config = PatientChartSummaryConfiguration(
        sections=[CustomSection(name="section_a"), CustomSection(name="section_b")]
    )
    assert config.values == {
        "sections": [
            {"custom": True, "key": "section_a"},
            {"custom": True, "key": "section_b"},
        ]
    }


def test_mixed_sections_preserve_order() -> None:
    """Built-in and custom sections must appear in the declared order."""
    config = PatientChartSummaryConfiguration(
        sections=[
            CustomSection(name="my_section"),
            Section.MEDICATIONS,
            Section.CONDITIONS,
            CustomSection(name="another_section"),
        ]
    )
    assert config.values == {
        "sections": [
            {"custom": True, "key": "my_section"},
            {"custom": False, "key": "medications"},
            {"custom": False, "key": "conditions"},
            {"custom": True, "key": "another_section"},
        ]
    }


def test_mixed_sections_apply_payload() -> None:
    """apply() must wrap mixed sections correctly under data key."""
    config = PatientChartSummaryConfiguration(
        sections=[Section.VITALS, CustomSection(name="my_section")]
    )
    payload = json.loads(config.apply().payload)
    assert payload == {
        "data": {
            "sections": [
                {"custom": False, "key": "vitals"},
                {"custom": True, "key": "my_section"},
            ]
        }
    }
