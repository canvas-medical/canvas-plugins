from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ID(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class Patient(_message.Message):
    __slots__ = ("id", "first_name", "last_name", "birth_date")
    ID_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    BIRTH_DATE_FIELD_NUMBER: _ClassVar[int]
    id: str
    first_name: str
    last_name: str
    birth_date: str
    def __init__(self, id: _Optional[str] = ..., first_name: _Optional[str] = ..., last_name: _Optional[str] = ..., birth_date: _Optional[str] = ...) -> None: ...
