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
    SEND_PRESCRIBE_COMMAND: _ClassVar[EffectType]
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
    ORIGINATE_LAB_ORDER_COMMAND: _ClassVar[EffectType]
    EDIT_LAB_ORDER_COMMAND: _ClassVar[EffectType]
    DELETE_LAB_ORDER_COMMAND: _ClassVar[EffectType]
    COMMIT_LAB_ORDER_COMMAND: _ClassVar[EffectType]
    ENTER_IN_ERROR_LAB_ORDER_COMMAND: _ClassVar[EffectType]
    SEND_LAB_ORDER_COMMAND: _ClassVar[EffectType]
    ORIGINATE_FAMILY_HISTORY_COMMAND: _ClassVar[EffectType]
    EDIT_FAMILY_HISTORY_COMMAND: _ClassVar[EffectType]
    DELETE_FAMILY_HISTORY_COMMAND: _ClassVar[EffectType]
    COMMIT_FAMILY_HISTORY_COMMAND: _ClassVar[EffectType]
    ENTER_IN_ERROR_FAMILY_HISTORY_COMMAND: _ClassVar[EffectType]
    ORIGINATE_ALLERGY_COMMAND: _ClassVar[EffectType]
    EDIT_ALLERGY_COMMAND: _ClassVar[EffectType]
    DELETE_ALLERGY_COMMAND: _ClassVar[EffectType]
    COMMIT_ALLERGY_COMMAND: _ClassVar[EffectType]
    ENTER_IN_ERROR_ALLERGY_COMMAND: _ClassVar[EffectType]
    ORIGINATE_REMOVE_ALLERGY_COMMAND: _ClassVar[EffectType]
    EDIT_REMOVE_ALLERGY_COMMAND: _ClassVar[EffectType]
    DELETE_REMOVE_ALLERGY_COMMAND: _ClassVar[EffectType]
    COMMIT_REMOVE_ALLERGY_COMMAND: _ClassVar[EffectType]
    ENTER_IN_ERROR_REMOVE_ALLERGY_COMMAND: _ClassVar[EffectType]
    ORIGINATE_SURGICAL_HISTORY_COMMAND: _ClassVar[EffectType]
    EDIT_SURGICAL_HISTORY_COMMAND: _ClassVar[EffectType]
    DELETE_SURGICAL_HISTORY_COMMAND: _ClassVar[EffectType]
    COMMIT_SURGICAL_HISTORY_COMMAND: _ClassVar[EffectType]
    ENTER_IN_ERROR_SURGICAL_HISTORY_COMMAND: _ClassVar[EffectType]
    CREATE_TASK: _ClassVar[EffectType]
    UPDATE_TASK: _ClassVar[EffectType]
    CREATE_TASK_COMMENT: _ClassVar[EffectType]
    ORIGINATE_MEDICAL_HISTORY_COMMAND: _ClassVar[EffectType]
    EDIT_MEDICAL_HISTORY_COMMAND: _ClassVar[EffectType]
    DELETE_MEDICAL_HISTORY_COMMAND: _ClassVar[EffectType]
    COMMIT_MEDICAL_HISTORY_COMMAND: _ClassVar[EffectType]
    ENTER_IN_ERROR_MEDICAL_HISTORY_COMMAND: _ClassVar[EffectType]
    ADD_OR_UPDATE_PROTOCOL_CARD: _ClassVar[EffectType]
    ORIGINATE_TASK_COMMAND: _ClassVar[EffectType]
    EDIT_TASK_COMMAND: _ClassVar[EffectType]
    DELETE_TASK_COMMAND: _ClassVar[EffectType]
    COMMIT_TASK_COMMAND: _ClassVar[EffectType]
    ENTER_IN_ERROR_TASK_COMMAND: _ClassVar[EffectType]
    ORIGINATE_REFILL_COMMAND: _ClassVar[EffectType]
    EDIT_REFILL_COMMAND: _ClassVar[EffectType]
    DELETE_REFILL_COMMAND: _ClassVar[EffectType]
    COMMIT_REFILL_COMMAND: _ClassVar[EffectType]
    ENTER_IN_ERROR_REFILL_COMMAND: _ClassVar[EffectType]
    SEND_REFILL_COMMAND: _ClassVar[EffectType]
    ORIGINATE_VITALS_COMMAND: _ClassVar[EffectType]
    EDIT_VITALS_COMMAND: _ClassVar[EffectType]
    DELETE_VITALS_COMMAND: _ClassVar[EffectType]
    COMMIT_VITALS_COMMAND: _ClassVar[EffectType]
    ENTER_IN_ERROR_VITALS_COMMAND: _ClassVar[EffectType]
    ORIGINATE_UPDATE_DIAGNOSIS_COMMAND: _ClassVar[EffectType]
    EDIT_UPDATE_DIAGNOSIS_COMMAND: _ClassVar[EffectType]
    DELETE_UPDATE_DIAGNOSIS_COMMAND: _ClassVar[EffectType]
    COMMIT_UPDATE_DIAGNOSIS_COMMAND: _ClassVar[EffectType]
    ENTER_IN_ERROR_UPDATE_DIAGNOSIS_COMMAND: _ClassVar[EffectType]
    ORIGINATE_CLOSE_GOAL_COMMAND: _ClassVar[EffectType]
    EDIT_CLOSE_GOAL_COMMAND: _ClassVar[EffectType]
    DELETE_CLOSE_GOAL_COMMAND: _ClassVar[EffectType]
    COMMIT_CLOSE_GOAL_COMMAND: _ClassVar[EffectType]
    ENTER_IN_ERROR_CLOSE_GOAL_COMMAND: _ClassVar[EffectType]
    ORIGINATE_REFER_COMMAND: _ClassVar[EffectType]
    EDIT_REFER_COMMAND: _ClassVar[EffectType]
    DELETE_REFER_COMMAND: _ClassVar[EffectType]
    COMMIT_REFER_COMMAND: _ClassVar[EffectType]
    ENTER_IN_ERROR_REFER_COMMAND: _ClassVar[EffectType]
    ORIGINATE_CHANGE_MEDICATION_COMMAND: _ClassVar[EffectType]
    EDIT_CHANGE_MEDICATION_COMMAND: _ClassVar[EffectType]
    DELETE_CHANGE_MEDICATION_COMMAND: _ClassVar[EffectType]
    COMMIT_CHANGE_MEDICATION_COMMAND: _ClassVar[EffectType]
    ENTER_IN_ERROR_CHANGE_MEDICATION_COMMAND: _ClassVar[EffectType]
    CREATE_QUESTIONNAIRE_RESULT: _ClassVar[EffectType]
    ANNOTATE_PATIENT_CHART_CONDITION_RESULTS: _ClassVar[EffectType]
    ANNOTATE_CLAIM_CONDITION_RESULTS: _ClassVar[EffectType]
    SHOW_PATIENT_CHART_SUMMARY_SECTIONS: _ClassVar[EffectType]
    SHOW_PATIENT_PROFILE_SECTIONS: _ClassVar[EffectType]
    PATIENT_PROFILE__ADD_PHARMACY__POST_SEARCH_RESULTS: _ClassVar[EffectType]
    SEND_SURESCRIPTS_ELIGIBILITY_REQUEST: _ClassVar[EffectType]
    SEND_SURESCRIPTS_MEDICATION_HISTORY_REQUEST: _ClassVar[EffectType]
    SEND_SURESCRIPTS_BENEFITS_REQUEST: _ClassVar[EffectType]
    ORIGINATE_EXAM_COMMAND: _ClassVar[EffectType]
    EDIT_EXAM_COMMAND: _ClassVar[EffectType]
    DELETE_EXAM_COMMAND: _ClassVar[EffectType]
    COMMIT_EXAM_COMMAND: _ClassVar[EffectType]
    ENTER_IN_ERROR_EXAM_COMMAND: _ClassVar[EffectType]
    ORIGINATE_ROS_COMMAND: _ClassVar[EffectType]
    EDIT_ROS_COMMAND: _ClassVar[EffectType]
    DELETE_ROS_COMMAND: _ClassVar[EffectType]
    COMMIT_ROS_COMMAND: _ClassVar[EffectType]
    ENTER_IN_ERROR_ROS_COMMAND: _ClassVar[EffectType]
    ORIGINATE_STRUCTURED_ASSESSMENT_COMMAND: _ClassVar[EffectType]
    EDIT_STRUCTURED_ASSESSMENT_COMMAND: _ClassVar[EffectType]
    DELETE_STRUCTURED_ASSESSMENT_COMMAND: _ClassVar[EffectType]
    COMMIT_STRUCTURED_ASSESSMENT_COMMAND: _ClassVar[EffectType]
    ENTER_IN_ERROR_STRUCTURED_ASSESSMENT_COMMAND: _ClassVar[EffectType]
    ORIGINATE_FOLLOW_UP_COMMAND: _ClassVar[EffectType]
    EDIT_FOLLOW_UP_COMMAND: _ClassVar[EffectType]
    DELETE_FOLLOW_UP_COMMAND: _ClassVar[EffectType]
    COMMIT_FOLLOW_UP_COMMAND: _ClassVar[EffectType]
    ENTER_IN_ERROR_FOLLOW_UP_COMMAND: _ClassVar[EffectType]
    ORIGINATE_IMAGING_ORDER_COMMAND: _ClassVar[EffectType]
    EDIT_IMAGING_ORDER_COMMAND: _ClassVar[EffectType]
    DELETE_IMAGING_ORDER_COMMAND: _ClassVar[EffectType]
    COMMIT_IMAGING_ORDER_COMMAND: _ClassVar[EffectType]
    ENTER_IN_ERROR_IMAGING_ORDER_COMMAND: _ClassVar[EffectType]
    ORIGINATE_RESOLVE_CONDITION_COMMAND: _ClassVar[EffectType]
    EDIT_RESOLVE_CONDITION_COMMAND: _ClassVar[EffectType]
    DELETE_RESOLVE_CONDITION_COMMAND: _ClassVar[EffectType]
    COMMIT_RESOLVE_CONDITION_COMMAND: _ClassVar[EffectType]
    ENTER_IN_ERROR_RESOLVE_CONDITION_COMMAND: _ClassVar[EffectType]
    ORIGINATE_ADJUST_PRESCRIPTION_COMMAND: _ClassVar[EffectType]
    EDIT_ADJUST_PRESCRIPTION_COMMAND: _ClassVar[EffectType]
    DELETE_ADJUST_PRESCRIPTION_COMMAND: _ClassVar[EffectType]
    COMMIT_ADJUST_PRESCRIPTION_COMMAND: _ClassVar[EffectType]
    ENTER_IN_ERROR_ADJUST_PRESCRIPTION_COMMAND: _ClassVar[EffectType]
    SEND_ADJUST_PRESCRIPTION_COMMAND: _ClassVar[EffectType]
    ORIGINATE_CHART_SECTION_REVIEW_COMMAND: _ClassVar[EffectType]
    ORIGINATE_IMMUNIZATION_STATEMENT_COMMAND: _ClassVar[EffectType]
    EDIT_IMMUNIZATION_STATEMENT_COMMAND: _ClassVar[EffectType]
    DELETE_IMMUNIZATION_STATEMENT_COMMAND: _ClassVar[EffectType]
    COMMIT_IMMUNIZATION_STATEMENT_COMMAND: _ClassVar[EffectType]
    ENTER_IN_ERROR_IMMUNIZATION_STATEMENT_COMMAND: _ClassVar[EffectType]
    COMMAND_AVAILABLE_ACTIONS_RESULTS: _ClassVar[EffectType]
    SHOW_ACTION_BUTTON: _ClassVar[EffectType]
    PATIENT_PORTAL__FORM_RESULT: _ClassVar[EffectType]
    PATIENT_PORTAL__APPOINTMENT_IS_CANCELABLE: _ClassVar[EffectType]
    PATIENT_PORTAL__APPOINTMENT_IS_RESCHEDULABLE: _ClassVar[EffectType]
    PATIENT_PORTAL__APPOINTMENT_SHOW_MEETING_LINK: _ClassVar[EffectType]
    PATIENT_PORTAL__SEND_INVITE: _ClassVar[EffectType]
    PATIENT_PORTAL__APPOINTMENTS__SLOTS__POST_SEARCH_RESULTS: _ClassVar[EffectType]
    PATIENT_PORTAL__APPOINTMENTS__FORM_APPOINTMENT_TYPES__PRE_SEARCH_RESULTS: _ClassVar[EffectType]
    PATIENT_PORTAL__APPOINTMENTS__FORM_APPOINTMENT_TYPES__POST_SEARCH_RESULTS: _ClassVar[EffectType]
    PATIENT_PORTAL__APPOINTMENTS__FORM_LOCATIONS__PRE_SEARCH_RESULTS: _ClassVar[EffectType]
    PATIENT_PORTAL__APPOINTMENTS__FORM_LOCATIONS__POST_SEARCH_RESULTS: _ClassVar[EffectType]
    PATIENT_PORTAL__APPOINTMENTS__FORM_PROVIDERS__PRE_SEARCH_RESULTS: _ClassVar[EffectType]
    PATIENT_PORTAL__APPOINTMENTS__FORM_PROVIDERS__POST_SEARCH_RESULTS: _ClassVar[EffectType]
    PATIENT_PORTAL__APPLICATION_CONFIGURATION: _ClassVar[EffectType]
    ADD_BILLING_LINE_ITEM: _ClassVar[EffectType]
    UPDATE_BILLING_LINE_ITEM: _ClassVar[EffectType]
    REMOVE_BILLING_LINE_ITEM: _ClassVar[EffectType]
    SHOW_PATIENT_PORTAL_MENU_ITEMS: _ClassVar[EffectType]
    PORTAL_WIDGET: _ClassVar[EffectType]
    LAUNCH_MODAL: _ClassVar[EffectType]
    SIMPLE_API_RESPONSE: _ClassVar[EffectType]
    SIMPLE_API_WEBSOCKET_ACCEPT: _ClassVar[EffectType]
    SIMPLE_API_WEBSOCKET_DENY: _ClassVar[EffectType]
    SIMPLE_API_WEBSOCKET_BROADCAST: _ClassVar[EffectType]
    UPDATE_USER: _ClassVar[EffectType]
    CREATE_NOTE: _ClassVar[EffectType]
    UPDATE_NOTE: _ClassVar[EffectType]
    CREATE_APPOINTMENT: _ClassVar[EffectType]
    UPDATE_APPOINTMENT: _ClassVar[EffectType]
    CANCEL_APPOINTMENT: _ClassVar[EffectType]
    CREATE_SCHEDULE_EVENT: _ClassVar[EffectType]
    UPDATE_SCHEDULE_EVENT: _ClassVar[EffectType]
    DELETE_SCHEDULE_EVENT: _ClassVar[EffectType]
    CREATE_PATIENT: _ClassVar[EffectType]
    CREATE_MESSAGE: _ClassVar[EffectType]
    SEND_MESSAGE: _ClassVar[EffectType]
    CREATE_AND_SEND_MESSAGE: _ClassVar[EffectType]
    EDIT_MESSAGE: _ClassVar[EffectType]
    PATIENT_METADATA__CREATE_ADDITIONAL_FIELDS: _ClassVar[EffectType]
    UPSERT_PATIENT_METADATA: _ClassVar[EffectType]
    CREATE_PATIENT_EXTERNAL_IDENTIFIER: _ClassVar[EffectType]
    CREATE_COMPOUND_MEDICATION: _ClassVar[EffectType]
    UPDATE_COMPOUND_MEDICATION: _ClassVar[EffectType]
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
SEND_PRESCRIBE_COMMAND: EffectType
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
ORIGINATE_LAB_ORDER_COMMAND: EffectType
EDIT_LAB_ORDER_COMMAND: EffectType
DELETE_LAB_ORDER_COMMAND: EffectType
COMMIT_LAB_ORDER_COMMAND: EffectType
ENTER_IN_ERROR_LAB_ORDER_COMMAND: EffectType
SEND_LAB_ORDER_COMMAND: EffectType
ORIGINATE_FAMILY_HISTORY_COMMAND: EffectType
EDIT_FAMILY_HISTORY_COMMAND: EffectType
DELETE_FAMILY_HISTORY_COMMAND: EffectType
COMMIT_FAMILY_HISTORY_COMMAND: EffectType
ENTER_IN_ERROR_FAMILY_HISTORY_COMMAND: EffectType
ORIGINATE_ALLERGY_COMMAND: EffectType
EDIT_ALLERGY_COMMAND: EffectType
DELETE_ALLERGY_COMMAND: EffectType
COMMIT_ALLERGY_COMMAND: EffectType
ENTER_IN_ERROR_ALLERGY_COMMAND: EffectType
ORIGINATE_REMOVE_ALLERGY_COMMAND: EffectType
EDIT_REMOVE_ALLERGY_COMMAND: EffectType
DELETE_REMOVE_ALLERGY_COMMAND: EffectType
COMMIT_REMOVE_ALLERGY_COMMAND: EffectType
ENTER_IN_ERROR_REMOVE_ALLERGY_COMMAND: EffectType
ORIGINATE_SURGICAL_HISTORY_COMMAND: EffectType
EDIT_SURGICAL_HISTORY_COMMAND: EffectType
DELETE_SURGICAL_HISTORY_COMMAND: EffectType
COMMIT_SURGICAL_HISTORY_COMMAND: EffectType
ENTER_IN_ERROR_SURGICAL_HISTORY_COMMAND: EffectType
CREATE_TASK: EffectType
UPDATE_TASK: EffectType
CREATE_TASK_COMMENT: EffectType
ORIGINATE_MEDICAL_HISTORY_COMMAND: EffectType
EDIT_MEDICAL_HISTORY_COMMAND: EffectType
DELETE_MEDICAL_HISTORY_COMMAND: EffectType
COMMIT_MEDICAL_HISTORY_COMMAND: EffectType
ENTER_IN_ERROR_MEDICAL_HISTORY_COMMAND: EffectType
ADD_OR_UPDATE_PROTOCOL_CARD: EffectType
ORIGINATE_TASK_COMMAND: EffectType
EDIT_TASK_COMMAND: EffectType
DELETE_TASK_COMMAND: EffectType
COMMIT_TASK_COMMAND: EffectType
ENTER_IN_ERROR_TASK_COMMAND: EffectType
ORIGINATE_REFILL_COMMAND: EffectType
EDIT_REFILL_COMMAND: EffectType
DELETE_REFILL_COMMAND: EffectType
COMMIT_REFILL_COMMAND: EffectType
ENTER_IN_ERROR_REFILL_COMMAND: EffectType
SEND_REFILL_COMMAND: EffectType
ORIGINATE_VITALS_COMMAND: EffectType
EDIT_VITALS_COMMAND: EffectType
DELETE_VITALS_COMMAND: EffectType
COMMIT_VITALS_COMMAND: EffectType
ENTER_IN_ERROR_VITALS_COMMAND: EffectType
ORIGINATE_UPDATE_DIAGNOSIS_COMMAND: EffectType
EDIT_UPDATE_DIAGNOSIS_COMMAND: EffectType
DELETE_UPDATE_DIAGNOSIS_COMMAND: EffectType
COMMIT_UPDATE_DIAGNOSIS_COMMAND: EffectType
ENTER_IN_ERROR_UPDATE_DIAGNOSIS_COMMAND: EffectType
ORIGINATE_CLOSE_GOAL_COMMAND: EffectType
EDIT_CLOSE_GOAL_COMMAND: EffectType
DELETE_CLOSE_GOAL_COMMAND: EffectType
COMMIT_CLOSE_GOAL_COMMAND: EffectType
ENTER_IN_ERROR_CLOSE_GOAL_COMMAND: EffectType
ORIGINATE_REFER_COMMAND: EffectType
EDIT_REFER_COMMAND: EffectType
DELETE_REFER_COMMAND: EffectType
COMMIT_REFER_COMMAND: EffectType
ENTER_IN_ERROR_REFER_COMMAND: EffectType
ORIGINATE_CHANGE_MEDICATION_COMMAND: EffectType
EDIT_CHANGE_MEDICATION_COMMAND: EffectType
DELETE_CHANGE_MEDICATION_COMMAND: EffectType
COMMIT_CHANGE_MEDICATION_COMMAND: EffectType
ENTER_IN_ERROR_CHANGE_MEDICATION_COMMAND: EffectType
CREATE_QUESTIONNAIRE_RESULT: EffectType
ANNOTATE_PATIENT_CHART_CONDITION_RESULTS: EffectType
ANNOTATE_CLAIM_CONDITION_RESULTS: EffectType
SHOW_PATIENT_CHART_SUMMARY_SECTIONS: EffectType
SHOW_PATIENT_PROFILE_SECTIONS: EffectType
PATIENT_PROFILE__ADD_PHARMACY__POST_SEARCH_RESULTS: EffectType
SEND_SURESCRIPTS_ELIGIBILITY_REQUEST: EffectType
SEND_SURESCRIPTS_MEDICATION_HISTORY_REQUEST: EffectType
SEND_SURESCRIPTS_BENEFITS_REQUEST: EffectType
ORIGINATE_EXAM_COMMAND: EffectType
EDIT_EXAM_COMMAND: EffectType
DELETE_EXAM_COMMAND: EffectType
COMMIT_EXAM_COMMAND: EffectType
ENTER_IN_ERROR_EXAM_COMMAND: EffectType
ORIGINATE_ROS_COMMAND: EffectType
EDIT_ROS_COMMAND: EffectType
DELETE_ROS_COMMAND: EffectType
COMMIT_ROS_COMMAND: EffectType
ENTER_IN_ERROR_ROS_COMMAND: EffectType
ORIGINATE_STRUCTURED_ASSESSMENT_COMMAND: EffectType
EDIT_STRUCTURED_ASSESSMENT_COMMAND: EffectType
DELETE_STRUCTURED_ASSESSMENT_COMMAND: EffectType
COMMIT_STRUCTURED_ASSESSMENT_COMMAND: EffectType
ENTER_IN_ERROR_STRUCTURED_ASSESSMENT_COMMAND: EffectType
ORIGINATE_FOLLOW_UP_COMMAND: EffectType
EDIT_FOLLOW_UP_COMMAND: EffectType
DELETE_FOLLOW_UP_COMMAND: EffectType
COMMIT_FOLLOW_UP_COMMAND: EffectType
ENTER_IN_ERROR_FOLLOW_UP_COMMAND: EffectType
ORIGINATE_IMAGING_ORDER_COMMAND: EffectType
EDIT_IMAGING_ORDER_COMMAND: EffectType
DELETE_IMAGING_ORDER_COMMAND: EffectType
COMMIT_IMAGING_ORDER_COMMAND: EffectType
ENTER_IN_ERROR_IMAGING_ORDER_COMMAND: EffectType
ORIGINATE_RESOLVE_CONDITION_COMMAND: EffectType
EDIT_RESOLVE_CONDITION_COMMAND: EffectType
DELETE_RESOLVE_CONDITION_COMMAND: EffectType
COMMIT_RESOLVE_CONDITION_COMMAND: EffectType
ENTER_IN_ERROR_RESOLVE_CONDITION_COMMAND: EffectType
ORIGINATE_ADJUST_PRESCRIPTION_COMMAND: EffectType
EDIT_ADJUST_PRESCRIPTION_COMMAND: EffectType
DELETE_ADJUST_PRESCRIPTION_COMMAND: EffectType
COMMIT_ADJUST_PRESCRIPTION_COMMAND: EffectType
ENTER_IN_ERROR_ADJUST_PRESCRIPTION_COMMAND: EffectType
SEND_ADJUST_PRESCRIPTION_COMMAND: EffectType
ORIGINATE_CHART_SECTION_REVIEW_COMMAND: EffectType
ORIGINATE_IMMUNIZATION_STATEMENT_COMMAND: EffectType
EDIT_IMMUNIZATION_STATEMENT_COMMAND: EffectType
DELETE_IMMUNIZATION_STATEMENT_COMMAND: EffectType
COMMIT_IMMUNIZATION_STATEMENT_COMMAND: EffectType
ENTER_IN_ERROR_IMMUNIZATION_STATEMENT_COMMAND: EffectType
COMMAND_AVAILABLE_ACTIONS_RESULTS: EffectType
SHOW_ACTION_BUTTON: EffectType
PATIENT_PORTAL__FORM_RESULT: EffectType
PATIENT_PORTAL__APPOINTMENT_IS_CANCELABLE: EffectType
PATIENT_PORTAL__APPOINTMENT_IS_RESCHEDULABLE: EffectType
PATIENT_PORTAL__APPOINTMENT_SHOW_MEETING_LINK: EffectType
PATIENT_PORTAL__SEND_INVITE: EffectType
PATIENT_PORTAL__APPOINTMENTS__SLOTS__POST_SEARCH_RESULTS: EffectType
PATIENT_PORTAL__APPOINTMENTS__FORM_APPOINTMENT_TYPES__PRE_SEARCH_RESULTS: EffectType
PATIENT_PORTAL__APPOINTMENTS__FORM_APPOINTMENT_TYPES__POST_SEARCH_RESULTS: EffectType
PATIENT_PORTAL__APPOINTMENTS__FORM_LOCATIONS__PRE_SEARCH_RESULTS: EffectType
PATIENT_PORTAL__APPOINTMENTS__FORM_LOCATIONS__POST_SEARCH_RESULTS: EffectType
PATIENT_PORTAL__APPOINTMENTS__FORM_PROVIDERS__PRE_SEARCH_RESULTS: EffectType
PATIENT_PORTAL__APPOINTMENTS__FORM_PROVIDERS__POST_SEARCH_RESULTS: EffectType
PATIENT_PORTAL__APPLICATION_CONFIGURATION: EffectType
ADD_BILLING_LINE_ITEM: EffectType
UPDATE_BILLING_LINE_ITEM: EffectType
REMOVE_BILLING_LINE_ITEM: EffectType
SHOW_PATIENT_PORTAL_MENU_ITEMS: EffectType
PORTAL_WIDGET: EffectType
LAUNCH_MODAL: EffectType
SIMPLE_API_RESPONSE: EffectType
SIMPLE_API_WEBSOCKET_ACCEPT: EffectType
SIMPLE_API_WEBSOCKET_DENY: EffectType
SIMPLE_API_WEBSOCKET_BROADCAST: EffectType
UPDATE_USER: EffectType
CREATE_NOTE: EffectType
UPDATE_NOTE: EffectType
CREATE_APPOINTMENT: EffectType
UPDATE_APPOINTMENT: EffectType
CANCEL_APPOINTMENT: EffectType
CREATE_SCHEDULE_EVENT: EffectType
UPDATE_SCHEDULE_EVENT: EffectType
DELETE_SCHEDULE_EVENT: EffectType
CREATE_PATIENT: EffectType
CREATE_MESSAGE: EffectType
SEND_MESSAGE: EffectType
CREATE_AND_SEND_MESSAGE: EffectType
EDIT_MESSAGE: EffectType
PATIENT_METADATA__CREATE_ADDITIONAL_FIELDS: EffectType
UPSERT_PATIENT_METADATA: EffectType
CREATE_PATIENT_EXTERNAL_IDENTIFIER: EffectType
CREATE_COMPOUND_MEDICATION: EffectType
UPDATE_COMPOUND_MEDICATION: EffectType

class Effect(_message.Message):
    __slots__ = ("type", "payload", "plugin_name", "classname", "handler_name")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    PLUGIN_NAME_FIELD_NUMBER: _ClassVar[int]
    CLASSNAME_FIELD_NUMBER: _ClassVar[int]
    HANDLER_NAME_FIELD_NUMBER: _ClassVar[int]
    type: EffectType
    payload: str
    plugin_name: str
    classname: str
    handler_name: str
    def __init__(self, type: _Optional[_Union[EffectType, str]] = ..., payload: _Optional[str] = ..., plugin_name: _Optional[str] = ..., classname: _Optional[str] = ..., handler_name: _Optional[str] = ...) -> None: ...
