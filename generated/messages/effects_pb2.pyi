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
    NEW_EFFECT: _ClassVar[EffectType]
    ANOTHER_EFFECT: _ClassVar[EffectType]
UNKNOWN_EFFECT: EffectType
LOG: EffectType
ADD_PLAN_COMMAND: EffectType
AUTOCOMPLETE_SEARCH_RESULTS: EffectType
NEW_EFFECT: EffectType
ANOTHER_EFFECT: EffectType

class Effect(_message.Message):
    __slots__ = ("type", "payload")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    type: EffectType
    payload: str
    def __init__(self, type: _Optional[_Union[EffectType, str]] = ..., payload: _Optional[str] = ...) -> None: ...
