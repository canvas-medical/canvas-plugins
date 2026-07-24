from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ReloadPluginsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ReloadPluginsResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class ReloadPluginRequest(_message.Message):
    __slots__ = ("plugin",)
    PLUGIN_FIELD_NUMBER: _ClassVar[int]
    plugin: str
    def __init__(self, plugin: _Optional[str] = ...) -> None: ...

class ReloadPluginResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class UnloadPluginRequest(_message.Message):
    __slots__ = ("plugin",)
    PLUGIN_FIELD_NUMBER: _ClassVar[int]
    plugin: str
    def __init__(self, plugin: _Optional[str] = ...) -> None: ...

class UnloadPluginResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class GetRegisteredEventTypesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetRegisteredEventTypesResponse(_message.Message):
    __slots__ = ("event_types", "registry_version", "ready")
    EVENT_TYPES_FIELD_NUMBER: _ClassVar[int]
    REGISTRY_VERSION_FIELD_NUMBER: _ClassVar[int]
    READY_FIELD_NUMBER: _ClassVar[int]
    event_types: _containers.RepeatedScalarFieldContainer[str]
    registry_version: str
    ready: bool
    def __init__(self, event_types: _Optional[_Iterable[str]] = ..., registry_version: _Optional[str] = ..., ready: bool = ...) -> None: ...

class RunAgentRequest(_message.Message):
    __slots__ = ("agent_id", "scope_key", "run_id", "trigger_payload", "plugin_name", "handler_name", "actor", "source")
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    SCOPE_KEY_FIELD_NUMBER: _ClassVar[int]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    TRIGGER_PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    PLUGIN_NAME_FIELD_NUMBER: _ClassVar[int]
    HANDLER_NAME_FIELD_NUMBER: _ClassVar[int]
    ACTOR_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    agent_id: str
    scope_key: str
    run_id: str
    trigger_payload: str
    plugin_name: str
    handler_name: str
    actor: str
    source: str
    def __init__(self, agent_id: _Optional[str] = ..., scope_key: _Optional[str] = ..., run_id: _Optional[str] = ..., trigger_payload: _Optional[str] = ..., plugin_name: _Optional[str] = ..., handler_name: _Optional[str] = ..., actor: _Optional[str] = ..., source: _Optional[str] = ...) -> None: ...
