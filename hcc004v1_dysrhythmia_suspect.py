from typing import TYPE_CHECKING, Any

import arrow
from django.db.models import Q

from canvas_sdk.effects import Effect
from canvas_sdk.effects.protocol_card import ProtocolCard, Recommendation
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from canvas_sdk.v1.data.condition import Condition
from canvas_sdk.v1.data.medication import Medication
from canvas_sdk.v1.data.patient import Patient
from canvas_sdk.value_set.value_set import ValueSet

if TYPE_CHECKING:
    from canvas_sdk.effects import Effect


# TODO: Find a home for this
class DysrhythmiaClassConditionSuspect(ValueSet):
    """Dysrhythmia Class Condition suspect."""

    VALUE_SET_NAME = "Dysrhythmia Class Condition suspect"
    EXPANSION_VERSION = "CanvasHCC Update 2018-10-18"

    ICD10CM = {
        "I420",
        "I421",
        "I422",
        "I423",
        "I424",
        "I425",
        "I426",
        "I427",
        "I428",
        "I429",
        "I470",
        "I471",
        "I4710",
        "I4711",
        "I4719",
        "I472",
        "I4720",
        "I4721",
        "I4729",
        "I479",
        "I480",
        "I481",
        "I4811",
        "I4819",
        "I482",
        "I4820",
        "I4821",
        "I483",
        "I484",
        "I4891",
        "I4892",
        "I4901",
        "I4902",
        "I491",
        "I492",
        "I493",
        "I4940",
        "I4949",
        "I495",
        "I498",
        "I499",
    }


# TODO: Find a home for this
class Antiarrhythmics(ValueSet):
    """Antiarrhythmics."""

    VALUE_SET_NAME = "Antiarrhythmics"
    EXPANSION_VERSION = "ClassPath Update 18-10-15"

    FDB = {
        "150358",
        "151807",
        "152779",
        "155773",
        "157601",
        "160121",
        "165621",
        "166591",
        "169107",
        "169508",
        "170461",
        "174429",
        "175363",
        "175494",
        "178251",
        "183239",
        "184929",
        "185830",
        "189377",
        "189730",
        "190878",
        "193821",
        "194412",
        "195187",
        "196380",
        "198310",
        "199400",
        "203114",
        "205183",
        "206598",
        "208686",
        "210260",
        "210732",
        "212898",
        "221901",
        "222092",
        "223459",
        "224332",
        "228864",
        "230155",
        "237183",
        "243776",
        "243776",
        "248491",
        "248829",
        "250272",
        "251530",
        "251766",
        "260972",
        "261266",
        "261929",
        "262594",
        "265464",
        "265785",
        "274471",
        "278255",
        "278255",
        "278255",
        "278255",
        "280333",
        "281153",
        "283306",
        "288964",
        "291187",
        "296991",
        "444249",
        "444249",
        "444944",
        "444944",
        "449494",
        "449496",
        "451558",
        "451559",
        "451560",
        "453457",
        "453462",
        "454178",
        "454180",
        "454181",
        "454205",
        "454206",
        "454207",
        "454371",
        "545231",
        "545231",
        "545232",
        "545233",
        "545238",
        "545239",
        "545239",
        "558741",
        "558745",
        "559416",
        "560050",
        "563304",
        "563305",
        "563306",
        "563310",
        "564459",
        "564460",
        "565068",
        "565069",
        "573523",
        "583982",
        "583982",
        "583985",
        "583985",
        "590326",
        "590375",
        "590376",
        "591479",
        "592349",
        "592421",
        "594710",
        "594714",
    }


class Protocol(BaseProtocol):
    """Dysrhythmia Suspects."""

    # TODO: Add ProtocolOverride event types
    RESPONDS_TO = [
        EventType.Name(EventType.CONDITION_CREATED),
        EventType.Name(EventType.CONDITION_UPDATED),
        EventType.Name(EventType.MEDICATION_LIST_ITEM_CREATED),
        EventType.Name(EventType.MEDICATION_LIST_ITEM_UPDATED),
    ]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.patient_id = self.patient_id_from_event()

    # TODO: Getting the patient or patient ID from an objects seems like something that will happen
    #  a lot. Should this be standardized in a base class? On the flip side, the fields needed from
    #  a patient may not be standard. Maybe a simple, standard, efficient way to get a patient ID
    #  from a target is a good place to start.
    def patient_id_from_event(self) -> str:
        """Get the patient ID from the event target."""
        # TODO: Add cases for ProtocolOverride
        match self.event.type:
            case EventType.CONDITION_CREATED | EventType.CONDITION_UPDATED:
                model = Condition
            case EventType.MEDICATION_LIST_ITEM_CREATED | EventType.MEDICATION_LIST_ITEM_UPDATED:
                model = Medication
            case _:
                raise AssertionError(
                    f"Event type {self.event.type} not supported by 'patient_id_from_event'"
                )

        return (
            model.objects.select_related("patient")
            .values_list("patient__id")
            .get(id=self.event.target)[0]
        )

    def in_denominator(self) -> bool:
        """
        Patients with any active medication in Antiarrhythmics Drug Class.
        """
        # TODO: Settable time frame is not currently supported — where would it come from?
        time_frame_provided = False
        if not time_frame_provided:
            # TODO: Should these datetimes be based on local time or UTC time?
            time_frame_end = arrow.get()
            time_frame_start = time_frame_end.shift(years=-1)
        else:
            raise RuntimeError("Time frame is not settable")

        # TODO: Is the status field used at all for medications, or is filtering done just with start/end dates?
        qs = Medication.objects.filter(patient__id=self.patient_id, start_date__lte=time_frame_end)

        # TODO: still_active=False is not currently supported — where would the value come from?
        still_active = True
        if still_active:
            return qs.filter(Q(end_date__isnull=True) | Q(end_date__gte=time_frame_end)).exists()
        else:
            return qs.filter(Q(end_date__isnull=True) | Q(end_date__gte=time_frame_start)).exists()

    def in_numerator(self) -> bool:
        """
        Patients without active conditions within the list with ICD 10 I42.* I47.*, I48.*, I49.*.
        """
        # TODO: Settable time frame is not currently supported — where would it come from?
        time_frame_provided = False
        if not time_frame_provided:
            # TODO: Should these datetimes be based on local time or UTC time?
            time_frame_end = arrow.get()
            time_frame_start = time_frame_end.shift(years=-1)
        else:
            raise RuntimeError("Time frame is not settable")

        # TODO: Is the status field used at all for conditions, or is filtering done just with start/end dates?
        qs = Condition.objects.filter(patient__id=self.patient_id, onset_date__lte=time_frame_end)

        # TODO: still_active=False is not currently supported — where would the value come from?
        still_active = True
        if still_active:
            return qs.filter(
                Q(resolution_date__isnull=True) | Q(resolution__gte=time_frame_end)
            ).exists()
        else:
            return qs.filter(
                Q(resolution_date__isnull=True) | Q(resolution_date__gte=time_frame_start)
            ).exists()

    def compute(self) -> list[Effect]:
        """Return a ProtocolCard effect if the patient is in both the denominator and numerator."""
        if self.in_denominator():
            if self.in_numerator():
                first_name = Patient.objects.values_list("first_name").get(id=self.patient_id)[0]

                title = "Consider updating the Conditions List to include Dysrhythmia related problem as clinically appropriate."
                narrative = f"{first_name} has an active medication on the Medication List commonly used for Dysrhythmia. There is no associated condition on the Conditions List."

                card = ProtocolCard(
                    patient_id=self.patient_id,
                    key="HCC004v1_RECOMMEND_DIAGNOSE_DYSRHYTHMIA",
                    title=title,
                    narrative=narrative,
                    recommendations=[
                        Recommendation(
                            title=title,
                            button="Diagnose",
                            # TODO: Is the HREF value needed?
                            # href=None,
                            command={"key": "diagnose"},
                            # TODO: Is the context value needed?
                            # context=None
                        )
                    ],
                    status=ProtocolCard.Status.DUE,
                )

                return [card.apply()]
            else:
                # TODO: Is an effect required if patient is in denominator but not in numerator?
                pass

        return []
