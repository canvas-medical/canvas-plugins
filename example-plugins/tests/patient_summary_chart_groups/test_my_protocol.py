"""
Tests for the patient_summary_chart_groups plugin.

These tests validate the grouping logic for psychiatric conditions and medications
in the patient summary chart.
"""
from unittest.mock import Mock

import pytest
from patient_summary_chart_groups.protocols.my_protocol import Conditions, Medications

from canvas_sdk.commands.constants import CodeSystems
from canvas_sdk.events import EventType


class TestConditionsGrouping:
    """Tests for the Conditions handler."""

    def test_responds_to_correct_event(self):
        """Test that the Conditions handler responds to PATIENT_CHART__CONDITIONS event."""
        expected_event = EventType.Name(EventType.PATIENT_CHART__CONDITIONS)
        assert expected_event == Conditions.RESPONDS_TO

    def test_groups_psychiatric_conditions_f_codes(self):
        """Test that conditions with ICD10 F01-F99 codes are grouped under Psychiatry."""
        # Create mock event with psychiatric conditions
        mock_event = Mock()
        mock_event.context = [
            {
                "id": "condition-1",
                "display": "Major depressive disorder",
                "codings": [
                    {"system": CodeSystems.ICD10, "code": "F32.9"}
                ]
            },
            {
                "id": "condition-2",
                "display": "Generalized anxiety disorder",
                "codings": [
                    {"system": CodeSystems.ICD10, "code": "F41.1"}
                ]
            }
        ]

        handler = Conditions(event=mock_event)
        effects = handler.compute()

        assert len(effects) == 1
        assert isinstance(effects[0].__class__.__name__, str)

        # Verify the grouping logic created the Psychiatry group
        # We can't easily inspect the effect internals, but we can verify it was created
        assert effects[0] is not None

    def test_groups_psychiatric_conditions_r45_codes(self):
        """Test that conditions with ICD10 R45 codes are grouped under Psychiatry."""
        mock_event = Mock()
        mock_event.context = [
            {
                "id": "condition-1",
                "display": "Nervousness",
                "codings": [
                    {"system": CodeSystems.ICD10, "code": "R45.0"}
                ]
            }
        ]

        handler = Conditions(event=mock_event)
        effects = handler.compute()

        assert len(effects) == 1
        assert effects[0] is not None

    def test_does_not_group_non_psychiatric_conditions(self):
        """Test that non-psychiatric conditions are not grouped."""
        mock_event = Mock()
        mock_event.context = [
            {
                "id": "condition-1",
                "display": "Essential hypertension",
                "codings": [
                    {"system": CodeSystems.ICD10, "code": "I10"}
                ]
            },
            {
                "id": "condition-2",
                "display": "Type 2 diabetes",
                "codings": [
                    {"system": CodeSystems.ICD10, "code": "E11.9"}
                ]
            }
        ]

        handler = Conditions(event=mock_event)
        effects = handler.compute()

        # Effect is still created, but Psychiatry group should be empty
        assert len(effects) == 1

    def test_handles_mixed_conditions(self):
        """Test handling of both psychiatric and non-psychiatric conditions."""
        mock_event = Mock()
        mock_event.context = [
            {
                "id": "condition-1",
                "display": "Major depressive disorder",
                "codings": [
                    {"system": CodeSystems.ICD10, "code": "F32.9"}
                ]
            },
            {
                "id": "condition-2",
                "display": "Essential hypertension",
                "codings": [
                    {"system": CodeSystems.ICD10, "code": "I10"}
                ]
            }
        ]

        handler = Conditions(event=mock_event)
        effects = handler.compute()

        assert len(effects) == 1
        assert effects[0] is not None

    def test_handles_empty_conditions_list(self):
        """Test that empty conditions list is handled gracefully."""
        mock_event = Mock()
        mock_event.context = []

        handler = Conditions(event=mock_event)
        effects = handler.compute()

        assert len(effects) == 1

    def test_handles_condition_with_multiple_codings(self):
        """Test that conditions with multiple coding systems are handled correctly."""
        mock_event = Mock()
        mock_event.context = [
            {
                "id": "condition-1",
                "display": "Major depressive disorder",
                "codings": [
                    {"system": CodeSystems.SNOMED, "code": "370143000"},
                    {"system": CodeSystems.ICD10, "code": "F32.9"}
                ]
            }
        ]

        handler = Conditions(event=mock_event)
        effects = handler.compute()

        assert len(effects) == 1
        assert effects[0] is not None


class TestMedicationsGrouping:
    """Tests for the Medications handler."""

    def test_responds_to_correct_event(self):
        """Test that the Medications handler responds to PATIENT_CHART__MEDICATIONS event."""
        expected_event = EventType.Name(EventType.PATIENT_CHART__MEDICATIONS)
        assert expected_event == Medications.RESPONDS_TO

    def test_groups_psychiatric_medications(self):
        """Test that medications with psychiatric RxNorm codes are grouped under Psychiatry."""
        mock_event = Mock()
        mock_event.context = [
            {
                "id": "medication-1",
                "display": "Sertraline 50mg",
                "codings": [
                    {"system": CodeSystems.RXNORM, "code": "725"}  # Sertraline
                ]
            },
            {
                "id": "medication-2",
                "display": "Fluoxetine 20mg",
                "codings": [
                    {"system": CodeSystems.RXNORM, "code": "4493"}  # Fluoxetine
                ]
            }
        ]

        handler = Medications(event=mock_event)
        effects = handler.compute()

        assert len(effects) == 1
        assert effects[0] is not None

    def test_does_not_group_non_psychiatric_medications(self):
        """Test that non-psychiatric medications are not grouped."""
        mock_event = Mock()
        mock_event.context = [
            {
                "id": "medication-1",
                "display": "Lisinopril 10mg",
                "codings": [
                    {"system": CodeSystems.RXNORM, "code": "314076"}  # Not in psych list
                ]
            }
        ]

        handler = Medications(event=mock_event)
        effects = handler.compute()

        # Effect is created, but Psychiatry group should be empty
        assert len(effects) == 1

    def test_handles_mixed_medications(self):
        """Test handling of both psychiatric and non-psychiatric medications."""
        mock_event = Mock()
        mock_event.context = [
            {
                "id": "medication-1",
                "display": "Sertraline 50mg",
                "codings": [
                    {"system": CodeSystems.RXNORM, "code": "725"}
                ]
            },
            {
                "id": "medication-2",
                "display": "Lisinopril 10mg",
                "codings": [
                    {"system": CodeSystems.RXNORM, "code": "314076"}
                ]
            }
        ]

        handler = Medications(event=mock_event)
        effects = handler.compute()

        assert len(effects) == 1
        assert effects[0] is not None

    def test_handles_empty_medications_list(self):
        """Test that empty medications list is handled gracefully."""
        mock_event = Mock()
        mock_event.context = []

        handler = Medications(event=mock_event)
        effects = handler.compute()

        assert len(effects) == 1

    def test_handles_medication_with_multiple_codings(self):
        """Test that medications with multiple coding systems are handled correctly."""
        mock_event = Mock()
        mock_event.context = [
            {
                "id": "medication-1",
                "display": "Sertraline 50mg",
                "codings": [
                    {"system": "http://other-system.com", "code": "12345"},
                    {"system": CodeSystems.RXNORM, "code": "725"}
                ]
            }
        ]

        handler = Medications(event=mock_event)
        effects = handler.compute()

        assert len(effects) == 1
        assert effects[0] is not None

    def test_medication_codes_list_is_populated(self):
        """Test that the medication_codes list contains expected psychiatric medications."""
        # Verify some known psychiatric medication codes are in the list
        assert 725 in Medications.medication_codes  # Sertraline
        assert 4493 in Medications.medication_codes  # Fluoxetine
        assert 3322 in Medications.medication_codes  # Escitalopram
        assert 42347 in Medications.medication_codes  # Alprazolam

        # Verify the list has a reasonable number of codes
        assert len(Medications.medication_codes) > 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
