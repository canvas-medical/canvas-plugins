"""
Data Access Layer client.

This module is primarily responsible for executing calls to the gRPC service so that such details
are abstracted away from callers. The results of the functions in this module are protobufs which
must be mapped to user-facing objects.
"""

import grpc

from canvas_generated.data_access_layer.data_access_layer_pb2 import ID, Patient
from canvas_generated.data_access_layer.data_access_layer_pb2_grpc import (
    DataAccessLayerStub,
)
from settings import DAL_TARGET

_CHANNEL = grpc.insecure_channel(DAL_TARGET)
_STUB = DataAccessLayerStub(_CHANNEL)


def get_patient(id: str) -> Patient:
    """Given an ID, get the Patient from the Data Access Layer."""
    return _STUB.GetPatient(ID(id=id))
