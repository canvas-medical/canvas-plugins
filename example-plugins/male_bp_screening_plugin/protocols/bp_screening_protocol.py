from datetime import datetime, timedelta
from typing import List

from canvas_sdk.effects import Effect
from canvas_sdk.effects.protocol_card import ProtocolCard
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler


class MaleBPScreeningProtocol(BaseHandler):
    """
    Blood pressure screening protocol for male patients aged 18-39.
    
    This protocol follows USPSTF guidelines for blood pressure screening:
    - Recommends screening every 2-3 years for men aged 18-39
    - Displays protocol card when screening is due
    - Provides recommendations for blood pressure measurement
    
    Triggers on: PATIENT_CREATED, PATIENT_UPDATED events
    Effects: ProtocolCard with blood pressure screening recommendations
    """

    RESPONDS_TO = [
        EventType.Name(EventType.PATIENT_CREATED),
        EventType.Name(EventType.PATIENT_UPDATED)
    ]

    def compute(self) -> List[Effect]:
        """Generate protocol card for eligible male patients needing BP screening."""
        
        # Get patient data from context
        patient = self.context.get("patient", {})
        patient_id = patient.get("id")
        
        if not patient_id:
            return []
        
        # Check if patient is eligible for screening
        if not self._is_eligible_for_screening(patient):
            return []
        
        # Check if screening is due
        if not self._is_screening_due(patient):
            return []
        
        # Create protocol card for blood pressure screening
        protocol_card = ProtocolCard(
            patient_id=patient_id,
            key="male-bp-screening-18-39",
            title="Blood Pressure Screening Recommended",
            narrative=(
                "This male patient (age 18-39) is due for blood pressure screening "
                "per USPSTF guidelines. Regular screening helps identify hypertension "
                "early for timely intervention."
            ),
            status=ProtocolCard.Status.DUE
        )
        
        # Add recommendations
        protocol_card.add_recommendation(
            title="Measure Blood Pressure",
            button="Document BP",
            command="vitalsign",
            context={
                "vital_sign_type": "blood_pressure",
                "note": "Screening per USPSTF guidelines for men 18-39"
            }
        )
        
        protocol_card.add_recommendation(
            title="USPSTF Guidelines",
            button="View Guidelines",
            href="https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/hypertension-in-adults-screening"
        )
        
        return [protocol_card.apply()]
    
    def _is_eligible_for_screening(self, patient: dict) -> bool:
        """
        Check if patient is eligible for blood pressure screening.
        
        Criteria:
        - Male gender
        - Age between 18-39 years
        """
        # Check gender
        gender = patient.get("gender", "").lower()
        if gender != "male":
            return False
        
        # Check age
        birth_date = patient.get("birth_date")
        if not birth_date:
            return False
        
        try:
            # Parse birth date and calculate age
            if isinstance(birth_date, str):
                birth_date = datetime.fromisoformat(birth_date.replace('Z', '+00:00'))
            elif hasattr(birth_date, 'date'):
                birth_date = birth_date.date()
            
            today = datetime.now().date()
            if hasattr(birth_date, 'date'):
                birth_date = birth_date.date()
            
            age = today.year - birth_date.year - (
                (today.month, today.day) < (birth_date.month, birth_date.day)
            )
            
            return 18 <= age <= 39
            
        except (ValueError, AttributeError):
            return False
    
    def _is_screening_due(self, patient: dict) -> bool:
        """
        Check if blood pressure screening is due.
        
        USPSTF recommends screening every 2-3 years for adults 18-39.
        This method checks if it's been more than 2 years since last screening.
        """
        # In a real implementation, this would check:
        # 1. Last blood pressure measurement date
        # 2. Previous screening dates
        # 3. Risk factors that might require more frequent screening
        
        # For this example, we'll assume screening is due if:
        # - No recent vital signs recorded, OR
        # - Last BP measurement was > 2 years ago
        
        # This is a simplified implementation
        # In production, you would query the patient's vital signs history
        last_bp_date = patient.get("last_bp_screening_date")
        
        if not last_bp_date:
            # No previous screening recorded, so screening is due
            return True
        
        try:
            if isinstance(last_bp_date, str):
                last_bp_date = datetime.fromisoformat(last_bp_date.replace('Z', '+00:00'))
            
            # Check if more than 2 years since last screening
            cutoff_date = datetime.now() - timedelta(days=730)  # 2 years
            return last_bp_date < cutoff_date
            
        except (ValueError, AttributeError):
            # If we can't parse the date, assume screening is due
            return True


class MaleBPScreeningEncounterProtocol(BaseHandler):
    """
    Blood pressure screening protocol triggered during encounters.
    
    This protocol activates when a new encounter is created for eligible male patients,
    providing an opportunity to remind clinicians about blood pressure screening.
    """
    
    RESPONDS_TO = EventType.Name(EventType.ENCOUNTER_CREATED)
    
    def compute(self) -> List[Effect]:
        """Generate protocol card during encounters for eligible patients."""
        
        # Get patient ID from encounter context
        patient_id = self.context.get("patient", {}).get("id")
        if not patient_id:
            return []
        
        # For encounter-based protocol, we would typically:
        # 1. Look up the full patient record
        # 2. Apply the same eligibility checks
        # 3. Generate the protocol card if needed
        
        # This would require additional data access permissions
        # For now, we'll create a simplified version
        
        protocol_card = ProtocolCard(
            patient_id=patient_id,
            key="male-bp-screening-encounter",
            title="Consider Blood Pressure Screening",
            narrative=(
                "For male patients aged 18-39, consider blood pressure screening "
                "per USPSTF guidelines if not done within the past 2-3 years."
            ),
            status=ProtocolCard.Status.PENDING
        )
        
        protocol_card.add_recommendation(
            title="Check BP Screening History",
            button="Review History",
            command="assessment",
            context={
                "type": "bp_screening_assessment",
                "note": "Review blood pressure screening history"
            }
        )
        
        return [protocol_card.apply()]