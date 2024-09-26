from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EffectType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_EFFECT: _ClassVar[EffectType]
    LOG: _ClassVar[EffectType]
    ADD_PLAN_COMMAND: _ClassVar[EffectType]
    AUTOCOMPLETE_SEARCH_RESULTS: _ClassVar[EffectType]
    ADD_BANNER_ALERT: _ClassVar[EffectType]
    REMOVE_BANNER_ALERT: _ClassVar[EffectType]
    ORIGINATE_ASSESS_COMMAND: _ClassVar[EffectType]
    EDIT_ASSESS_COMMAND: _ClassVar[EffectType]
    DELETE_ASSESS_COMMAND: _ClassVar[EffectType]
    COMMIT_ASSESS_COMMAND: _ClassVar[EffectType]
    ENTER_IN_ERROR_ASSESS_COMMAND: _ClassVar[EffectType]
    ORIGINATE_DIAGNOSE_COMMAND: _ClassVar[EffectType]
    EDIT_DIAGNOSE_COMMAND: _ClassVar[EffectType]
    DELETE_DIAGNOSE_COMMAND: _ClassVar[EffectType]
    COMMIT_DIAGNOSE_COMMAND: _ClassVar[EffectType]
    ENTER_IN_ERROR_DIAGNOSE_COMMAND: _ClassVar[EffectType]
    ORIGINATE_GOAL_COMMAND: _ClassVar[EffectType]
    EDIT_GOAL_COMMAND: _ClassVar[EffectType]
    DELETE_GOAL_COMMAND: _ClassVar[EffectType]
    COMMIT_GOAL_COMMAND: _ClassVar[EffectType]
    ENTER_IN_ERROR_GOAL_COMMAND: _ClassVar[EffectType]
    ORIGINATE_HPI_COMMAND: _ClassVar[EffectType]
    EDIT_HPI_COMMAND: _ClassVar[EffectType]
    DELETE_HPI_COMMAND: _ClassVar[EffectType]
    COMMIT_HPI_COMMAND: _ClassVar[EffectType]
    ENTER_IN_ERROR_HPI_COMMAND: _ClassVar[EffectType]
    ORIGINATE_MEDICATION_STATEMENT_COMMAND: _ClassVar[EffectType]
    EDIT_MEDICATION_STATEMENT_COMMAND: _ClassVar[EffectType]
    DELETE_MEDICATION_STATEMENT_COMMAND: _ClassVar[EffectType]
    COMMIT_MEDICATION_STATEMENT_COMMAND: _ClassVar[EffectType]
    ENTER_IN_ERROR_MEDICATION_STATEMENT_COMMAND: _ClassVar[EffectType]
    ORIGINATE_PLAN_COMMAND: _ClassVar[EffectType]
    EDIT_PLAN_COMMAND: _ClassVar[EffectType]
    DELETE_PLAN_COMMAND: _ClassVar[EffectType]
    COMMIT_PLAN_COMMAND: _ClassVar[EffectType]
    ENTER_IN_ERROR_PLAN_COMMAND: _ClassVar[EffectType]
    ORIGINATE_PRESCRIBE_COMMAND: _ClassVar[EffectType]
    EDIT_PRESCRIBE_COMMAND: _ClassVar[EffectType]
    DELETE_PRESCRIBE_COMMAND: _ClassVar[EffectType]
    COMMIT_PRESCRIBE_COMMAND: _ClassVar[EffectType]
    ENTER_IN_ERROR_PRESCRIBE_COMMAND: _ClassVar[EffectType]
    ORIGINATE_QUESTIONNAIRE_COMMAND: _ClassVar[EffectType]
    EDIT_QUESTIONNAIRE_COMMAND: _ClassVar[EffectType]
    DELETE_QUESTIONNAIRE_COMMAND: _ClassVar[EffectType]
    COMMIT_QUESTIONNAIRE_COMMAND: _ClassVar[EffectType]
    ENTER_IN_ERROR_QUESTIONNAIRE_COMMAND: _ClassVar[EffectType]
    ORIGINATE_REASON_FOR_VISIT_COMMAND: _ClassVar[EffectType]
    EDIT_REASON_FOR_VISIT_COMMAND: _ClassVar[EffectType]
    DELETE_REASON_FOR_VISIT_COMMAND: _ClassVar[EffectType]
    COMMIT_REASON_FOR_VISIT_COMMAND: _ClassVar[EffectType]
    ENTER_IN_ERROR_REASON_FOR_VISIT_COMMAND: _ClassVar[EffectType]
    ORIGINATE_STOP_MEDICATION_COMMAND: _ClassVar[EffectType]
    EDIT_STOP_MEDICATION_COMMAND: _ClassVar[EffectType]
    DELETE_STOP_MEDICATION_COMMAND: _ClassVar[EffectType]
    COMMIT_STOP_MEDICATION_COMMAND: _ClassVar[EffectType]
    ENTER_IN_ERROR_STOP_MEDICATION_COMMAND: _ClassVar[EffectType]
    ORIGINATE_UPDATE_GOAL_COMMAND: _ClassVar[EffectType]
    EDIT_UPDATE_GOAL_COMMAND: _ClassVar[EffectType]
    DELETE_UPDATE_GOAL_COMMAND: _ClassVar[EffectType]
    COMMIT_UPDATE_GOAL_COMMAND: _ClassVar[EffectType]
    ENTER_IN_ERROR_UPDATE_GOAL_COMMAND: _ClassVar[EffectType]
    ORIGINATE_PERFORM_COMMAND: _ClassVar[EffectType]
    EDIT_PERFORM_COMMAND: _ClassVar[EffectType]
    DELETE_PERFORM_COMMAND: _ClassVar[EffectType]
    COMMIT_PERFORM_COMMAND: _ClassVar[EffectType]
    ENTER_IN_ERROR_PERFORM_COMMAND: _ClassVar[EffectType]
    ORIGINATE_INSTRUCT_COMMAND: _ClassVar[EffectType]
    EDIT_INSTRUCT_COMMAND: _ClassVar[EffectType]
    DELETE_INSTRUCT_COMMAND: _ClassVar[EffectType]
    COMMIT_INSTRUCT_COMMAND: _ClassVar[EffectType]
    ENTER_IN_ERROR_INSTRUCT_COMMAND: _ClassVar[EffectType]
    CREATE_TASK: _ClassVar[EffectType]
    UPDATE_TASK: _ClassVar[EffectType]
    CREATE_TASK_COMMENT: _ClassVar[EffectType]
    ADD_OR_UPDATE_PROTOCOL_CARD: _ClassVar[EffectType]
    ANNOTATE_PATIENT_CHART_CONDITION_RESULTS: _ClassVar[EffectType]
    ANNOTATE_CLAIM_CONDITION_RESULTS: _ClassVar[EffectType]
    SHOW_PATIENT_CHART_SUMMARY_SECTIONS: _ClassVar[EffectType]
UNKNOWN_EFFECT: EffectType
LOG: EffectType
ADD_PLAN_COMMAND: EffectType
AUTOCOMPLETE_SEARCH_RESULTS: EffectType
ADD_BANNER_ALERT: EffectType
REMOVE_BANNER_ALERT: EffectType
ORIGINATE_ASSESS_COMMAND: EffectType
EDIT_ASSESS_COMMAND: EffectType
DELETE_ASSESS_COMMAND: EffectType
COMMIT_ASSESS_COMMAND: EffectType
ENTER_IN_ERROR_ASSESS_COMMAND: EffectType
ORIGINATE_DIAGNOSE_COMMAND: EffectType
EDIT_DIAGNOSE_COMMAND: EffectType
DELETE_DIAGNOSE_COMMAND: EffectType
COMMIT_DIAGNOSE_COMMAND: EffectType
ENTER_IN_ERROR_DIAGNOSE_COMMAND: EffectType
ORIGINATE_GOAL_COMMAND: EffectType
EDIT_GOAL_COMMAND: EffectType
DELETE_GOAL_COMMAND: EffectType
COMMIT_GOAL_COMMAND: EffectType
ENTER_IN_ERROR_GOAL_COMMAND: EffectType
ORIGINATE_HPI_COMMAND: EffectType
EDIT_HPI_COMMAND: EffectType
DELETE_HPI_COMMAND: EffectType
COMMIT_HPI_COMMAND: EffectType
ENTER_IN_ERROR_HPI_COMMAND: EffectType
ORIGINATE_MEDICATION_STATEMENT_COMMAND: EffectType
EDIT_MEDICATION_STATEMENT_COMMAND: EffectType
DELETE_MEDICATION_STATEMENT_COMMAND: EffectType
COMMIT_MEDICATION_STATEMENT_COMMAND: EffectType
ENTER_IN_ERROR_MEDICATION_STATEMENT_COMMAND: EffectType
ORIGINATE_PLAN_COMMAND: EffectType
EDIT_PLAN_COMMAND: EffectType
DELETE_PLAN_COMMAND: EffectType
COMMIT_PLAN_COMMAND: EffectType
ENTER_IN_ERROR_PLAN_COMMAND: EffectType
ORIGINATE_PRESCRIBE_COMMAND: EffectType
EDIT_PRESCRIBE_COMMAND: EffectType
DELETE_PRESCRIBE_COMMAND: EffectType
COMMIT_PRESCRIBE_COMMAND: EffectType
ENTER_IN_ERROR_PRESCRIBE_COMMAND: EffectType
ORIGINATE_QUESTIONNAIRE_COMMAND: EffectType
EDIT_QUESTIONNAIRE_COMMAND: EffectType
DELETE_QUESTIONNAIRE_COMMAND: EffectType
COMMIT_QUESTIONNAIRE_COMMAND: EffectType
ENTER_IN_ERROR_QUESTIONNAIRE_COMMAND: EffectType
ORIGINATE_REASON_FOR_VISIT_COMMAND: EffectType
EDIT_REASON_FOR_VISIT_COMMAND: EffectType
DELETE_REASON_FOR_VISIT_COMMAND: EffectType
COMMIT_REASON_FOR_VISIT_COMMAND: EffectType
ENTER_IN_ERROR_REASON_FOR_VISIT_COMMAND: EffectType
ORIGINATE_STOP_MEDICATION_COMMAND: EffectType
EDIT_STOP_MEDICATION_COMMAND: EffectType
DELETE_STOP_MEDICATION_COMMAND: EffectType
COMMIT_STOP_MEDICATION_COMMAND: EffectType
ENTER_IN_ERROR_STOP_MEDICATION_COMMAND: EffectType
ORIGINATE_UPDATE_GOAL_COMMAND: EffectType
EDIT_UPDATE_GOAL_COMMAND: EffectType
DELETE_UPDATE_GOAL_COMMAND: EffectType
COMMIT_UPDATE_GOAL_COMMAND: EffectType
ENTER_IN_ERROR_UPDATE_GOAL_COMMAND: EffectType
ORIGINATE_PERFORM_COMMAND: EffectType
EDIT_PERFORM_COMMAND: EffectType
DELETE_PERFORM_COMMAND: EffectType
COMMIT_PERFORM_COMMAND: EffectType
ENTER_IN_ERROR_PERFORM_COMMAND: EffectType
ORIGINATE_INSTRUCT_COMMAND: EffectType
EDIT_INSTRUCT_COMMAND: EffectType
DELETE_INSTRUCT_COMMAND: EffectType
COMMIT_INSTRUCT_COMMAND: EffectType
ENTER_IN_ERROR_INSTRUCT_COMMAND: EffectType
CREATE_TASK: EffectType
UPDATE_TASK: EffectType
CREATE_TASK_COMMENT: EffectType
ADD_OR_UPDATE_PROTOCOL_CARD: EffectType
ANNOTATE_PATIENT_CHART_CONDITION_RESULTS: EffectType
ANNOTATE_CLAIM_CONDITION_RESULTS: EffectType
SHOW_PATIENT_CHART_SUMMARY_SECTIONS: EffectType

class Effect(_message.Message):
    __slots__ = ("type", "payload", "plugin_name")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    PLUGIN_NAME_FIELD_NUMBER: _ClassVar[int]
    type: EffectType
    payload: str
    plugin_name: str
    def __init__(self, type: _Optional[_Union[EffectType, str]] = ..., payload: _Optional[str] = ..., plugin_name: _Optional[str] = ...) -> None: ...
