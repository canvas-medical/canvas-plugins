"""
Data Access Layer client.

This module is primarily responsible for executing calls to the gRPC service so that such details
are abstracted away from callers. The return values of the methods on the client class are protobufs
which must be mapped to user-facing objects.
"""

import functools
from collections.abc import Callable
from types import FunctionType
from typing import Any

import grpc
from grpc import StatusCode

from canvas_generated.data_access_layer.data_access_layer_pb2 import ID, Patient
from canvas_generated.data_access_layer.data_access_layer_pb2_grpc import (
    DataAccessLayerStub,
)
from settings import DAL_TARGET

from . import exceptions
from .exceptions import DataModuleError


class _DataAccessLayerClientMeta(type):
    """
    Metaclass for the Data Access Layer client class.

    Wraps all methods of a class with a gRPC error handler.
    """

    def __new__(cls, name: str, bases: tuple, attrs: dict) -> type:
        for attr_name, attr_value in attrs.items():
            if isinstance(attr_value, FunctionType):
                attrs[attr_name] = cls.handle_grpc_errors(attr_value)
        return super().__new__(cls, name, bases, attrs)

    @classmethod
    def handle_grpc_errors(cls, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Decorator that wraps a try-except block around all class methods. gRPC errors are mapped to
        a defined set of exceptions from a Data Access Layer exception hierarchy.
        """

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except grpc.RpcError as error:
                # gRPC exceptions aren't tightly defined, so we'll try to get a status code and
                # error details, and handle it if we can't
                try:
                    status_code = error.code()
                except Exception:
                    status_code = None

                try:
                    error_details = error.details()
                except Exception:
                    error_details = ""

                # Map more gRPC status codes to exception types as needed
                match status_code:
                    case StatusCode.NOT_FOUND:
                        raise exceptions.DataModuleNotFoundError(error_details) from error
                    case _:
                        raise exceptions.DataModuleError from error
            except Exception as exception:
                raise DataModuleError from exception

        return wrapper


class _DataAccessLayerClient(metaclass=_DataAccessLayerClientMeta):
    """
    Data Access Layer client.

    Do not instantiate -- just import the global variable DAL_CLIENT.
    """

    def __init__(self) -> None:
        self._channel = grpc.insecure_channel(DAL_TARGET)
        self._stub = DataAccessLayerStub(self._channel)

    def get_patient(self, id: str) -> Patient:
        """Given an ID, get the Patient from the Data Access Layer."""
        return self._stub.GetPatient(ID(id=id))


# There should only be one instantiation of the client, so this global will act as a singleton in a
# way. This is the value that should be imported; no one should be instantiating the DAL client
# (hence the underscore notation indicating that the class is "private").
DAL_CLIENT = _DataAccessLayerClient()
