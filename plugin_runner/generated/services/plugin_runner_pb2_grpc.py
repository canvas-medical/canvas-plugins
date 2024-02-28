# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from generated.messages import events_pb2 as generated_dot_messages_dot_events__pb2


class PluginRunnerStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.HandleEvent = channel.unary_stream(
                '/canvas.PluginRunner/HandleEvent',
                request_serializer=generated_dot_messages_dot_events__pb2.Event.SerializeToString,
                response_deserializer=generated_dot_messages_dot_events__pb2.EventResponse.FromString,
                )


class PluginRunnerServicer(object):
    """Missing associated documentation comment in .proto file."""

    def HandleEvent(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_PluginRunnerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'HandleEvent': grpc.unary_stream_rpc_method_handler(
                    servicer.HandleEvent,
                    request_deserializer=generated_dot_messages_dot_events__pb2.Event.FromString,
                    response_serializer=generated_dot_messages_dot_events__pb2.EventResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'canvas.PluginRunner', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class PluginRunner(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def HandleEvent(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/canvas.PluginRunner/HandleEvent',
            generated_dot_messages_dot_events__pb2.Event.SerializeToString,
            generated_dot_messages_dot_events__pb2.EventResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)