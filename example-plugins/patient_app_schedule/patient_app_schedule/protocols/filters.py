import json
from typing import Any

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler
from canvas_sdk.v1.data import Appointment, CareTeamMembership
from canvas_sdk.v1.data.care_team import CareTeamMembershipStatus
from logger import log


class Providers(BaseHandler):
    """
    Filters form providers to only show those in the patient's care team.

    This plugin listens to the PATIENT_PORTAL__APPOINTMENTS__FORM_PROVIDERS__POST_SEARCH
    event and returns a filtered list containing only providers who are members of the
    patient's care team.
    """

    # Name the event type you wish to run in response to
    RESPONDS_TO = EventType.Name(
        EventType.PATIENT_PORTAL__APPOINTMENTS__FORM_PROVIDERS__POST_SEARCH
    )

    def compute(self) -> list[Effect]:
        """Filters providers based on patient's care team membership.

        Returns:
            List[Effect]: A single effect containing the filtered provider list
        """
        # Extract providers from context
        context = self.event.context
        providers = context.get("providers", [])

        try:
            if not providers:
                log.info("No providers to filter")
                return []

            # Get patient ID
            patient_id = self.target

            if not patient_id:
                log.warning("No patient ID found, returning all providers")
                return self._create_effect(providers)

            # Get care team provider IDs for this patient
            care_team_provider_ids = self._get_care_team_provider_ids(patient_id)

            log.info(f"Patient {patient_id} care team provider IDs: {care_team_provider_ids}")
            log.info(f"Available providers: {[provider.get('id') for provider in providers]}")

            # Filter providers
            filtered_providers = [
                provider for provider in providers if provider.get("id") in care_team_provider_ids
            ]

            log.info(
                f"Filtered {len(providers)} providers to {len(filtered_providers)} "
                f"care team members for patient {patient_id}"
            )

            return self._create_effect(filtered_providers)

        except Exception as e:
            log.error(f"Error filtering providers by care team: {str(e)}")
            # Fail gracefully - return all providers on error
            return self._create_effect(providers)

    def _get_care_team_provider_ids(self, patient_id: str) -> set:
        """Retrieves all provider IDs in the patient's care team.

        Args:
            patient_id: The patient's identifier

        Returns:
            Set of provider IDs that are part of the patient's care team
        """
        try:
            care_team_members = CareTeamMembership.objects.filter(
                patient__id=patient_id, status=CareTeamMembershipStatus.ACTIVE
            ).values_list("staff__id", flat=True)

            return set(care_team_members)

        except Exception as e:
            log.error(f"Error fetching care team members: {str(e)}")
            return set()

    def _create_effect(self, providers: list[dict[str, Any]]) -> list[Effect]:
        """Creates the effect with the filtered provider list.

        Args:
            providers: List of provider dictionaries

        Returns:
            List containing a single effect with the provider data
        """
        payload = {"providers": providers}

        effect_type = EffectType.PATIENT_PORTAL__APPOINTMENTS__FORM_PROVIDERS__POST_SEARCH_RESULTS

        return [Effect(type=effect_type, payload=json.dumps(payload))]


class Locations(BaseHandler):
    """
    Filters form locations to only show those where the patient has had appointments.

    This plugin listens to the PATIENT_PORTAL__APPOINTMENTS__FORM_LOCATIONS__POST_SEARCH
    event and returns a filtered list containing only locations where the patient
    has previously had appointments.
    """

    # Name the event type you wish to run in response to
    RESPONDS_TO = EventType.Name(
        EventType.PATIENT_PORTAL__APPOINTMENTS__FORM_LOCATIONS__POST_SEARCH
    )

    def compute(self) -> list[Effect]:
        """Filters locations based on patient's appointment history.

        Returns:
            List[Effect]: A single effect containing the filtered location list
        """
        # Extract locations from context
        context = self.event.context
        locations = context.get("locations", [])

        try:
            if not locations:
                log.info("No locations to filter")
                return []

            # Get patient ID
            patient_id = self.target

            if not patient_id:
                log.warning("No patient ID found, returning all locations")
                return self._create_effect(locations)

            # Get location IDs where patient has had appointments
            patient_location_ids = self._get_patient_location_ids(patient_id)

            log.info(f"Patient {patient_id} has appointments at locations: {patient_location_ids}")
            log.info(f"Available locations: {[location.get('id') for location in locations]}")

            # Filter locations
            filtered_locations = [
                location for location in locations if location.get("id") in patient_location_ids
            ]

            log.info(
                f"Filtered {len(locations)} locations to {len(filtered_locations)} "
                f"locations with appointments for patient {patient_id}"
            )

            return self._create_effect(filtered_locations)

        except Exception as e:
            log.error(f"Error filtering locations by appointment history: {str(e)}")
            # Fail gracefully - return all locations on error
            return self._create_effect(locations)

    def _get_patient_location_ids(self, patient_id: str) -> set:
        """Retrieves all location IDs where the patient has had appointments.

        Args:
            patient_id: The patient's identifier

        Returns:
            Set of location IDs where the patient has had appointments
        """
        try:
            # Query distinct location IDs from patient's appointments
            # Using exclude to filter out appointments without locations
            location_ids = (
                Appointment.objects.filter(patient__id=patient_id)
                .exclude(location__isnull=True, location__active=False)
                .values_list("location__id", flat=True)
                .distinct()
            )

            return {str(location_id) for location_id in location_ids}

        except Exception as e:
            log.error(f"Error fetching patient appointment locations: {str(e)}")
            return set()

    def _create_effect(self, locations: list[dict[str, Any]]) -> list[Effect]:
        """Creates the effect with the filtered location list.

        Args:
            locations: List of location dictionaries

        Returns:
            List containing a single effect with the location data
        """
        payload = {"locations": locations}

        effect_type = EffectType.PATIENT_PORTAL__APPOINTMENTS__FORM_LOCATIONS__POST_SEARCH_RESULTS

        return [Effect(type=effect_type, payload=json.dumps(payload))]
