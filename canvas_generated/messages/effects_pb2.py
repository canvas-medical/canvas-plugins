# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: canvas_generated/messages/effects.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\'canvas_generated/messages/effects.proto\x12\x06\x63\x61nvas\"c\n\x06\x45\x66\x66\x65\x63t\x12 \n\x04type\x18\x01 \x01(\x0e\x32\x12.canvas.EffectType\x12\x0f\n\x07payload\x18\x02 \x01(\t\x12\x13\n\x0bplugin_name\x18\x03 \x01(\t\x12\x11\n\tclassname\x18\x04 \x01(\t*\xa8.\n\nEffectType\x12\x12\n\x0eUNKNOWN_EFFECT\x10\x00\x12\x07\n\x03LOG\x10\x01\x12\x14\n\x10\x41\x44\x44_PLAN_COMMAND\x10\x02\x12\x1f\n\x1b\x41UTOCOMPLETE_SEARCH_RESULTS\x10\x03\x12\x14\n\x10\x41\x44\x44_BANNER_ALERT\x10\x04\x12\x17\n\x13REMOVE_BANNER_ALERT\x10\x05\x12\x1c\n\x18ORIGINATE_ASSESS_COMMAND\x10\x06\x12\x17\n\x13\x45\x44IT_ASSESS_COMMAND\x10\x07\x12\x19\n\x15\x44\x45LETE_ASSESS_COMMAND\x10\x08\x12\x19\n\x15\x43OMMIT_ASSESS_COMMAND\x10\t\x12!\n\x1d\x45NTER_IN_ERROR_ASSESS_COMMAND\x10\n\x12\x1e\n\x1aORIGINATE_DIAGNOSE_COMMAND\x10\x0b\x12\x19\n\x15\x45\x44IT_DIAGNOSE_COMMAND\x10\x0c\x12\x1b\n\x17\x44\x45LETE_DIAGNOSE_COMMAND\x10\r\x12\x1b\n\x17\x43OMMIT_DIAGNOSE_COMMAND\x10\x0e\x12#\n\x1f\x45NTER_IN_ERROR_DIAGNOSE_COMMAND\x10\x0f\x12\x1a\n\x16ORIGINATE_GOAL_COMMAND\x10\x10\x12\x15\n\x11\x45\x44IT_GOAL_COMMAND\x10\x11\x12\x17\n\x13\x44\x45LETE_GOAL_COMMAND\x10\x12\x12\x17\n\x13\x43OMMIT_GOAL_COMMAND\x10\x13\x12\x1f\n\x1b\x45NTER_IN_ERROR_GOAL_COMMAND\x10\x14\x12\x19\n\x15ORIGINATE_HPI_COMMAND\x10\x15\x12\x14\n\x10\x45\x44IT_HPI_COMMAND\x10\x16\x12\x16\n\x12\x44\x45LETE_HPI_COMMAND\x10\x17\x12\x16\n\x12\x43OMMIT_HPI_COMMAND\x10\x18\x12\x1e\n\x1a\x45NTER_IN_ERROR_HPI_COMMAND\x10\x19\x12*\n&ORIGINATE_MEDICATION_STATEMENT_COMMAND\x10\x1a\x12%\n!EDIT_MEDICATION_STATEMENT_COMMAND\x10\x1b\x12\'\n#DELETE_MEDICATION_STATEMENT_COMMAND\x10\x1c\x12\'\n#COMMIT_MEDICATION_STATEMENT_COMMAND\x10\x1d\x12/\n+ENTER_IN_ERROR_MEDICATION_STATEMENT_COMMAND\x10\x1e\x12\x1a\n\x16ORIGINATE_PLAN_COMMAND\x10\x1f\x12\x15\n\x11\x45\x44IT_PLAN_COMMAND\x10 \x12\x17\n\x13\x44\x45LETE_PLAN_COMMAND\x10!\x12\x17\n\x13\x43OMMIT_PLAN_COMMAND\x10\"\x12\x1f\n\x1b\x45NTER_IN_ERROR_PLAN_COMMAND\x10#\x12\x1f\n\x1bORIGINATE_PRESCRIBE_COMMAND\x10$\x12\x1a\n\x16\x45\x44IT_PRESCRIBE_COMMAND\x10%\x12\x1c\n\x18\x44\x45LETE_PRESCRIBE_COMMAND\x10&\x12\x1c\n\x18\x43OMMIT_PRESCRIBE_COMMAND\x10\'\x12$\n ENTER_IN_ERROR_PRESCRIBE_COMMAND\x10(\x12#\n\x1fORIGINATE_QUESTIONNAIRE_COMMAND\x10)\x12\x1e\n\x1a\x45\x44IT_QUESTIONNAIRE_COMMAND\x10*\x12 \n\x1c\x44\x45LETE_QUESTIONNAIRE_COMMAND\x10+\x12 \n\x1c\x43OMMIT_QUESTIONNAIRE_COMMAND\x10,\x12(\n$ENTER_IN_ERROR_QUESTIONNAIRE_COMMAND\x10-\x12&\n\"ORIGINATE_REASON_FOR_VISIT_COMMAND\x10.\x12!\n\x1d\x45\x44IT_REASON_FOR_VISIT_COMMAND\x10/\x12#\n\x1f\x44\x45LETE_REASON_FOR_VISIT_COMMAND\x10\x30\x12#\n\x1f\x43OMMIT_REASON_FOR_VISIT_COMMAND\x10\x31\x12+\n\'ENTER_IN_ERROR_REASON_FOR_VISIT_COMMAND\x10\x32\x12%\n!ORIGINATE_STOP_MEDICATION_COMMAND\x10\x33\x12 \n\x1c\x45\x44IT_STOP_MEDICATION_COMMAND\x10\x34\x12\"\n\x1e\x44\x45LETE_STOP_MEDICATION_COMMAND\x10\x35\x12\"\n\x1e\x43OMMIT_STOP_MEDICATION_COMMAND\x10\x36\x12*\n&ENTER_IN_ERROR_STOP_MEDICATION_COMMAND\x10\x37\x12!\n\x1dORIGINATE_UPDATE_GOAL_COMMAND\x10\x38\x12\x1c\n\x18\x45\x44IT_UPDATE_GOAL_COMMAND\x10\x39\x12\x1e\n\x1a\x44\x45LETE_UPDATE_GOAL_COMMAND\x10:\x12\x1e\n\x1a\x43OMMIT_UPDATE_GOAL_COMMAND\x10;\x12&\n\"ENTER_IN_ERROR_UPDATE_GOAL_COMMAND\x10<\x12\x1d\n\x19ORIGINATE_PERFORM_COMMAND\x10=\x12\x18\n\x14\x45\x44IT_PERFORM_COMMAND\x10>\x12\x1a\n\x16\x44\x45LETE_PERFORM_COMMAND\x10?\x12\x1a\n\x16\x43OMMIT_PERFORM_COMMAND\x10@\x12\"\n\x1e\x45NTER_IN_ERROR_PERFORM_COMMAND\x10\x41\x12\x1e\n\x1aORIGINATE_INSTRUCT_COMMAND\x10\x42\x12\x19\n\x15\x45\x44IT_INSTRUCT_COMMAND\x10\x43\x12\x1b\n\x17\x44\x45LETE_INSTRUCT_COMMAND\x10\x44\x12\x1b\n\x17\x43OMMIT_INSTRUCT_COMMAND\x10\x45\x12#\n\x1f\x45NTER_IN_ERROR_INSTRUCT_COMMAND\x10\x46\x12\x1f\n\x1bORIGINATE_LAB_ORDER_COMMAND\x10G\x12\x1a\n\x16\x45\x44IT_LAB_ORDER_COMMAND\x10H\x12\x1c\n\x18\x44\x45LETE_LAB_ORDER_COMMAND\x10I\x12\x1c\n\x18\x43OMMIT_LAB_ORDER_COMMAND\x10J\x12$\n ENTER_IN_ERROR_LAB_ORDER_COMMAND\x10K\x12$\n ORIGINATE_FAMILY_HISTORY_COMMAND\x10L\x12\x1f\n\x1b\x45\x44IT_FAMILY_HISTORY_COMMAND\x10M\x12!\n\x1d\x44\x45LETE_FAMILY_HISTORY_COMMAND\x10N\x12!\n\x1d\x43OMMIT_FAMILY_HISTORY_COMMAND\x10O\x12)\n%ENTER_IN_ERROR_FAMILY_HISTORY_COMMAND\x10P\x12\x1d\n\x19ORIGINATE_ALLERGY_COMMAND\x10Q\x12\x18\n\x14\x45\x44IT_ALLERGY_COMMAND\x10R\x12\x1a\n\x16\x44\x45LETE_ALLERGY_COMMAND\x10S\x12\x1a\n\x16\x43OMMIT_ALLERGY_COMMAND\x10T\x12\"\n\x1e\x45NTER_IN_ERROR_ALLERGY_COMMAND\x10U\x12$\n ORIGINATE_REMOVE_ALLERGY_COMMAND\x10V\x12\x1f\n\x1b\x45\x44IT_REMOVE_ALLERGY_COMMAND\x10W\x12!\n\x1d\x44\x45LETE_REMOVE_ALLERGY_COMMAND\x10X\x12!\n\x1d\x43OMMIT_REMOVE_ALLERGY_COMMAND\x10Y\x12)\n%ENTER_IN_ERROR_REMOVE_ALLERGY_COMMAND\x10Z\x12&\n\"ORIGINATE_SURGICAL_HISTORY_COMMAND\x10[\x12!\n\x1d\x45\x44IT_SURGICAL_HISTORY_COMMAND\x10\\\x12#\n\x1f\x44\x45LETE_SURGICAL_HISTORY_COMMAND\x10]\x12#\n\x1f\x43OMMIT_SURGICAL_HISTORY_COMMAND\x10^\x12+\n\'ENTER_IN_ERROR_SURGICAL_HISTORY_COMMAND\x10_\x12\x0f\n\x0b\x43REATE_TASK\x10\x64\x12\x0f\n\x0bUPDATE_TASK\x10\x65\x12\x17\n\x13\x43REATE_TASK_COMMENT\x10\x66\x12%\n!ORIGINATE_MEDICAL_HISTORY_COMMAND\x10g\x12 \n\x1c\x45\x44IT_MEDICAL_HISTORY_COMMAND\x10h\x12\"\n\x1e\x44\x45LETE_MEDICAL_HISTORY_COMMAND\x10i\x12\"\n\x1e\x43OMMIT_MEDICAL_HISTORY_COMMAND\x10j\x12*\n&ENTER_IN_ERROR_MEDICAL_HISTORY_COMMAND\x10k\x12\x1f\n\x1b\x41\x44\x44_OR_UPDATE_PROTOCOL_CARD\x10n\x12\x1b\n\x16ORIGINATE_TASK_COMMAND\x10\x85\x01\x12\x16\n\x11\x45\x44IT_TASK_COMMAND\x10\x86\x01\x12\x18\n\x13\x44\x45LETE_TASK_COMMAND\x10\x87\x01\x12\x18\n\x13\x43OMMIT_TASK_COMMAND\x10\x88\x01\x12 \n\x1b\x45NTER_IN_ERROR_TASK_COMMAND\x10\x89\x01\x12\x1c\n\x18ORIGINATE_REFILL_COMMAND\x10q\x12\x17\n\x13\x45\x44IT_REFILL_COMMAND\x10r\x12\x19\n\x15\x44\x45LETE_REFILL_COMMAND\x10s\x12\x19\n\x15\x43OMMIT_REFILL_COMMAND\x10t\x12!\n\x1d\x45NTER_IN_ERROR_REFILL_COMMAND\x10u\x12\x1c\n\x18ORIGINATE_VITALS_COMMAND\x10v\x12\x17\n\x13\x45\x44IT_VITALS_COMMAND\x10w\x12\x19\n\x15\x44\x45LETE_VITALS_COMMAND\x10x\x12\x19\n\x15\x43OMMIT_VITALS_COMMAND\x10y\x12!\n\x1d\x45NTER_IN_ERROR_VITALS_COMMAND\x10z\x12&\n\"ORIGINATE_UPDATE_DIAGNOSIS_COMMAND\x10{\x12!\n\x1d\x45\x44IT_UPDATE_DIAGNOSIS_COMMAND\x10|\x12#\n\x1f\x44\x45LETE_UPDATE_DIAGNOSIS_COMMAND\x10}\x12#\n\x1f\x43OMMIT_UPDATE_DIAGNOSIS_COMMAND\x10~\x12+\n\'ENTER_IN_ERROR_UPDATE_DIAGNOSIS_COMMAND\x10\x7f\x12!\n\x1cORIGINATE_CLOSE_GOAL_COMMAND\x10\x80\x01\x12\x1c\n\x17\x45\x44IT_CLOSE_GOAL_COMMAND\x10\x81\x01\x12\x1e\n\x19\x44\x45LETE_CLOSE_GOAL_COMMAND\x10\x82\x01\x12\x1e\n\x19\x43OMMIT_CLOSE_GOAL_COMMAND\x10\x83\x01\x12&\n!ENTER_IN_ERROR_CLOSE_GOAL_COMMAND\x10\x84\x01\x12 \n\x1b\x43REATE_QUESTIONNAIRE_RESULT\x10\x8a\x01\x12-\n(ANNOTATE_PATIENT_CHART_CONDITION_RESULTS\x10\xc8\x01\x12%\n ANNOTATE_CLAIM_CONDITION_RESULTS\x10\xac\x02\x12(\n#SHOW_PATIENT_CHART_SUMMARY_SECTIONS\x10\x90\x03\x12\"\n\x1dSHOW_PATIENT_PROFILE_SECTIONS\x10\xf4\x03\x12\x37\n2PATIENT_PROFILE__ADD_PHARMACY__POST_SEARCH_RESULTS\x10\xf5\x03\x12)\n$SEND_SURESCRIPTS_ELIGIBILITY_REQUEST\x10\xd8\x04\x12\x30\n+SEND_SURESCRIPTS_MEDICATION_HISTORY_REQUEST\x10\xd9\x04\x12&\n!SEND_SURESCRIPTS_BENEFITS_REQUEST\x10\xda\x04\x12\x1b\n\x16ORIGINATE_EXAM_COMMAND\x10\xbc\x05\x12\x16\n\x11\x45\x44IT_EXAM_COMMAND\x10\xbd\x05\x12\x18\n\x13\x44\x45LETE_EXAM_COMMAND\x10\xbe\x05\x12\x18\n\x13\x43OMMIT_EXAM_COMMAND\x10\xbf\x05\x12 \n\x1b\x45NTER_IN_ERROR_EXAM_COMMAND\x10\xc0\x05\x12\x1a\n\x15ORIGINATE_ROS_COMMAND\x10\xa0\x06\x12\x15\n\x10\x45\x44IT_ROS_COMMAND\x10\xa1\x06\x12\x17\n\x12\x44\x45LETE_ROS_COMMAND\x10\xa2\x06\x12\x17\n\x12\x43OMMIT_ROS_COMMAND\x10\xa3\x06\x12\x1f\n\x1a\x45NTER_IN_ERROR_ROS_COMMAND\x10\xa4\x06\x12,\n\'ORIGINATE_STRUCTURED_ASSESSMENT_COMMAND\x10\x84\x07\x12\'\n\"EDIT_STRUCTURED_ASSESSMENT_COMMAND\x10\x85\x07\x12)\n$DELETE_STRUCTURED_ASSESSMENT_COMMAND\x10\x86\x07\x12)\n$COMMIT_STRUCTURED_ASSESSMENT_COMMAND\x10\x87\x07\x12\x31\n,ENTER_IN_ERROR_STRUCTURED_ASSESSMENT_COMMAND\x10\x88\x07\x12 \n\x1bORIGINATE_FOLLOW_UP_COMMAND\x10\x89\x07\x12\x1b\n\x16\x45\x44IT_FOLLOW_UP_COMMAND\x10\x8a\x07\x12\x1d\n\x18\x44\x45LETE_FOLLOW_UP_COMMAND\x10\x8b\x07\x12\x1d\n\x18\x43OMMIT_FOLLOW_UP_COMMAND\x10\x8c\x07\x12%\n ENTER_IN_ERROR_FOLLOW_UP_COMMAND\x10\x8d\x07\x12\x17\n\x12SHOW_ACTION_BUTTON\x10\xe8\x07\x12(\n#PATIENT_PORTAL__INTAKE_FORM_RESULTS\x10\xd0\x0f\x12.\n)PATIENT_PORTAL__APPOINTMENT_IS_CANCELABLE\x10\xd1\x0f\x12\x31\n,PATIENT_PORTAL__APPOINTMENT_IS_RESCHEDULABLE\x10\xd2\x0f\x12=\n8PATIENT_PORTAL__APPOINTMENTS__SLOTS__POST_SEARCH_RESULTS\x10\xd5\x0f\x12M\nHPATIENT_PORTAL__APPOINTMENTS__FORM_APPOINTMENT_TYPES__PRE_SEARCH_RESULTS\x10\xd6\x0f\x12N\nIPATIENT_PORTAL__APPOINTMENTS__FORM_APPOINTMENT_TYPES__POST_SEARCH_RESULTS\x10\xd7\x0f\x12\x45\n@PATIENT_PORTAL__APPOINTMENTS__FORM_LOCATIONS__PRE_SEARCH_RESULTS\x10\xd8\x0f\x12\x46\nAPATIENT_PORTAL__APPOINTMENTS__FORM_LOCATIONS__POST_SEARCH_RESULTS\x10\xd9\x0f\x12\x45\n@PATIENT_PORTAL__APPOINTMENTS__FORM_PROVIDERS__PRE_SEARCH_RESULTS\x10\xda\x0f\x12\x46\nAPATIENT_PORTAL__APPOINTMENTS__FORM_PROVIDERS__POST_SEARCH_RESULTS\x10\xdb\x0f\x12\x11\n\x0cLAUNCH_MODAL\x10\xb8\x17\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'canvas_generated.messages.effects_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_EFFECTTYPE']._serialized_start=153
  _globals['_EFFECTTYPE']._serialized_end=6081
  _globals['_EFFECT']._serialized_start=51
  _globals['_EFFECT']._serialized_end=150
# @@protoc_insertion_point(module_scope)
