from typing import ClassVar as _ClassVar
from typing import Optional as _Optional
from typing import Union as _Union

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper

DESCRIPTOR: _descriptor.FileDescriptor

class EffectType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_EFFECT: _ClassVar[EffectType]
    LOG: _ClassVar[EffectType]
    ADD_PLAN_COMMAND: _ClassVar[EffectType]
    AUTOCOMPLETE_SEARCH_RESULTS: _ClassVar[EffectType]
    ADD_BANNER_ALERT: _ClassVar[EffectType]
    REMOVE_BANNER_ALERT: _ClassVar[EffectType]

UNKNOWN_EFFECT: EffectType
LOG: EffectType
ADD_PLAN_COMMAND: EffectType
AUTOCOMPLETE_SEARCH_RESULTS: EffectType
ADD_BANNER_ALERT: EffectType
REMOVE_BANNER_ALERT: EffectType

class Effect(_message.Message):
    __slots__ = ("type", "payload", "plugin_name")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    PLUGIN_NAME_FIELD_NUMBER: _ClassVar[int]
    type: EffectType
    payload: str
    plugin_name: str
    def __init__(
        self,
        type: _Optional[_Union[EffectType, str]] = ...,
        payload: _Optional[str] = ...,
        plugin_name: _Optional[str] = ...,
    ) -> None: ...
