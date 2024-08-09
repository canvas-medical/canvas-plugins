from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

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

class Staff(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class Team(_message.Message):
    __slots__ = ("id", "name")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class Task(_message.Message):
    __slots__ = ("id", "assignee", "patient", "title", "due", "status", "created", "modified", "team", "task_type", "creator")
    ID_FIELD_NUMBER: _ClassVar[int]
    ASSIGNEE_FIELD_NUMBER: _ClassVar[int]
    PATIENT_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DUE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    MODIFIED_FIELD_NUMBER: _ClassVar[int]
    TEAM_FIELD_NUMBER: _ClassVar[int]
    TASK_TYPE_FIELD_NUMBER: _ClassVar[int]
    CREATOR_FIELD_NUMBER: _ClassVar[int]
    id: str
    assignee: Staff
    patient: Patient
    title: str
    due: str
    status: str
    created: str
    modified: str
    team: Team
    task_type: str
    creator: Staff
    def __init__(self, id: _Optional[str] = ..., assignee: _Optional[_Union[Staff, _Mapping]] = ..., patient: _Optional[_Union[Patient, _Mapping]] = ..., title: _Optional[str] = ..., due: _Optional[str] = ..., status: _Optional[str] = ..., created: _Optional[str] = ..., modified: _Optional[str] = ..., team: _Optional[_Union[Team, _Mapping]] = ..., task_type: _Optional[str] = ..., creator: _Optional[_Union[Staff, _Mapping]] = ...) -> None: ...

class TaskLabels(_message.Message):
    __slots__ = ("id", "labels")
    ID_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    id: str
    labels: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[str] = ..., labels: _Optional[_Iterable[str]] = ...) -> None: ...

class TaskComment(_message.Message):
    __slots__ = ("id", "created", "modified", "task", "creator", "body")
    ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    MODIFIED_FIELD_NUMBER: _ClassVar[int]
    TASK_FIELD_NUMBER: _ClassVar[int]
    CREATOR_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    id: str
    created: str
    modified: str
    task: Task
    creator: Staff
    body: str
    def __init__(self, id: _Optional[str] = ..., created: _Optional[str] = ..., modified: _Optional[str] = ..., task: _Optional[_Union[Task, _Mapping]] = ..., creator: _Optional[_Union[Staff, _Mapping]] = ..., body: _Optional[str] = ...) -> None: ...

class TaskComments(_message.Message):
    __slots__ = ("id", "comments")
    ID_FIELD_NUMBER: _ClassVar[int]
    COMMENTS_FIELD_NUMBER: _ClassVar[int]
    id: str
    comments: _containers.RepeatedCompositeFieldContainer[TaskComment]
    def __init__(self, id: _Optional[str] = ..., comments: _Optional[_Iterable[_Union[TaskComment, _Mapping]]] = ...) -> None: ...

class PatientTasks(_message.Message):
    __slots__ = ("id", "tasks")
    ID_FIELD_NUMBER: _ClassVar[int]
    TASKS_FIELD_NUMBER: _ClassVar[int]
    id: str
    tasks: _containers.RepeatedCompositeFieldContainer[Task]
    def __init__(self, id: _Optional[str] = ..., tasks: _Optional[_Iterable[_Union[Task, _Mapping]]] = ...) -> None: ...

class StaffAssignedTasks(_message.Message):
    __slots__ = ("id", "tasks")
    ID_FIELD_NUMBER: _ClassVar[int]
    TASKS_FIELD_NUMBER: _ClassVar[int]
    id: str
    tasks: _containers.RepeatedCompositeFieldContainer[Task]
    def __init__(self, id: _Optional[str] = ..., tasks: _Optional[_Iterable[_Union[Task, _Mapping]]] = ...) -> None: ...
