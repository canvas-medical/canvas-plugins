from generated.messages import effects_pb2 as _effects_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EventType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN: _ClassVar[EventType]
    ALLERGY_INTOLERANCE_CREATED: _ClassVar[EventType]
    ALLERGY_INTOLERANCE_UPDATED: _ClassVar[EventType]
    APPOINTMENT_BOOKED: _ClassVar[EventType]
    APPOINTMENT_CANCELED: _ClassVar[EventType]
    APPOINTMENT_CHECKED_IN: _ClassVar[EventType]
    APPOINTMENT_CREATED: _ClassVar[EventType]
    APPOINTMENT_NO_SHOWED: _ClassVar[EventType]
    APPOINTMENT_RESCHEDULED: _ClassVar[EventType]
    APPOINTMENT_RESTORED: _ClassVar[EventType]
    APPOINTMENT_UPDATED: _ClassVar[EventType]
    BILLING_LINE_ITEM_CREATED: _ClassVar[EventType]
    BILLING_LINE_ITEM_UPDATED: _ClassVar[EventType]
    CONDITION_ASSESSED: _ClassVar[EventType]
    CONDITION_CREATED: _ClassVar[EventType]
    CONDITION_RESOLVED: _ClassVar[EventType]
    CONDITION_UPDATED: _ClassVar[EventType]
    CONSENT_CREATED: _ClassVar[EventType]
    CONSENT_DELETED: _ClassVar[EventType]
    CONSENT_UPDATED: _ClassVar[EventType]
    COVERAGE_CREATED: _ClassVar[EventType]
    COVERAGE_UPDATED: _ClassVar[EventType]
    ENCOUNTER_CREATED: _ClassVar[EventType]
    ENCOUNTER_UPDATED: _ClassVar[EventType]
    EXTERNAL_EVENT_CREATED: _ClassVar[EventType]
    EXTERNAL_EVENT_UPDATED: _ClassVar[EventType]
    IMAGING_REPORT_CREATED: _ClassVar[EventType]
    IMAGING_REPORT_UPDATED: _ClassVar[EventType]
    IMMUNIZATION_CREATED: _ClassVar[EventType]
    IMMUNIZATION_STATEMENT_CREATED: _ClassVar[EventType]
    IMMUNIZATION_STATEMENT_UPDATED: _ClassVar[EventType]
    IMMUNIZATION_UPDATED: _ClassVar[EventType]
    INSTRUCTION_CREATED: _ClassVar[EventType]
    INSTRUCTION_UPDATED: _ClassVar[EventType]
    INTERVIEW_CREATED: _ClassVar[EventType]
    INTERVIEW_UPDATED: _ClassVar[EventType]
    LAB_ORDER_CREATED: _ClassVar[EventType]
    LAB_ORDER_UPDATED: _ClassVar[EventType]
    LAB_REPORT_CREATED: _ClassVar[EventType]
    LAB_REPORT_UPDATED: _ClassVar[EventType]
    MEDICATION_LIST_ITEM_CREATED: _ClassVar[EventType]
    MEDICATION_LIST_ITEM_UPDATED: _ClassVar[EventType]
    MESSAGE_CREATED: _ClassVar[EventType]
    PATIENT_CREATED: _ClassVar[EventType]
    PATIENT_UPDATED: _ClassVar[EventType]
    PRESCRIPTION_CREATED: _ClassVar[EventType]
    PRESCRIPTION_UPDATED: _ClassVar[EventType]
    REFERRAL_REPORT_CREATED: _ClassVar[EventType]
    REFERRAL_REPORT_UPDATED: _ClassVar[EventType]
    TASK_ASSIGNED: _ClassVar[EventType]
    TASK_CLOSED: _ClassVar[EventType]
    TASK_COMMENT_CREATED: _ClassVar[EventType]
    TASK_COMMENT_UPDATED: _ClassVar[EventType]
    TASK_COMPLETED: _ClassVar[EventType]
    TASK_CREATED: _ClassVar[EventType]
    TASK_LABELS_ADJUSTED: _ClassVar[EventType]
    TASK_UNASSIGNED: _ClassVar[EventType]
    TASK_UPDATED: _ClassVar[EventType]
    VITAL_SIGN_CREATED: _ClassVar[EventType]
    VITAL_SIGN_UPDATED: _ClassVar[EventType]
    CHART_OPENED: _ClassVar[EventType]
    COMMAND_ORIGINATED: _ClassVar[EventType]
UNKNOWN: EventType
ALLERGY_INTOLERANCE_CREATED: EventType
ALLERGY_INTOLERANCE_UPDATED: EventType
APPOINTMENT_BOOKED: EventType
APPOINTMENT_CANCELED: EventType
APPOINTMENT_CHECKED_IN: EventType
APPOINTMENT_CREATED: EventType
APPOINTMENT_NO_SHOWED: EventType
APPOINTMENT_RESCHEDULED: EventType
APPOINTMENT_RESTORED: EventType
APPOINTMENT_UPDATED: EventType
BILLING_LINE_ITEM_CREATED: EventType
BILLING_LINE_ITEM_UPDATED: EventType
CONDITION_ASSESSED: EventType
CONDITION_CREATED: EventType
CONDITION_RESOLVED: EventType
CONDITION_UPDATED: EventType
CONSENT_CREATED: EventType
CONSENT_DELETED: EventType
CONSENT_UPDATED: EventType
COVERAGE_CREATED: EventType
COVERAGE_UPDATED: EventType
ENCOUNTER_CREATED: EventType
ENCOUNTER_UPDATED: EventType
EXTERNAL_EVENT_CREATED: EventType
EXTERNAL_EVENT_UPDATED: EventType
IMAGING_REPORT_CREATED: EventType
IMAGING_REPORT_UPDATED: EventType
IMMUNIZATION_CREATED: EventType
IMMUNIZATION_STATEMENT_CREATED: EventType
IMMUNIZATION_STATEMENT_UPDATED: EventType
IMMUNIZATION_UPDATED: EventType
INSTRUCTION_CREATED: EventType
INSTRUCTION_UPDATED: EventType
INTERVIEW_CREATED: EventType
INTERVIEW_UPDATED: EventType
LAB_ORDER_CREATED: EventType
LAB_ORDER_UPDATED: EventType
LAB_REPORT_CREATED: EventType
LAB_REPORT_UPDATED: EventType
MEDICATION_LIST_ITEM_CREATED: EventType
MEDICATION_LIST_ITEM_UPDATED: EventType
MESSAGE_CREATED: EventType
PATIENT_CREATED: EventType
PATIENT_UPDATED: EventType
PRESCRIPTION_CREATED: EventType
PRESCRIPTION_UPDATED: EventType
REFERRAL_REPORT_CREATED: EventType
REFERRAL_REPORT_UPDATED: EventType
TASK_ASSIGNED: EventType
TASK_CLOSED: EventType
TASK_COMMENT_CREATED: EventType
TASK_COMMENT_UPDATED: EventType
TASK_COMPLETED: EventType
TASK_CREATED: EventType
TASK_LABELS_ADJUSTED: EventType
TASK_UNASSIGNED: EventType
TASK_UPDATED: EventType
VITAL_SIGN_CREATED: EventType
VITAL_SIGN_UPDATED: EventType
CHART_OPENED: EventType
COMMAND_ORIGINATED: EventType

class Event(_message.Message):
    __slots__ = ("type", "target")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    type: EventType
    target: str
    def __init__(self, type: _Optional[_Union[EventType, str]] = ..., target: _Optional[str] = ...) -> None: ...

class EventResponse(_message.Message):
    __slots__ = ("success", "effects")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    EFFECTS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    effects: _containers.RepeatedCompositeFieldContainer[_effects_pb2.Effect]
    def __init__(self, success: bool = ..., effects: _Optional[_Iterable[_Union[_effects_pb2.Effect, _Mapping]]] = ...) -> None: ...
