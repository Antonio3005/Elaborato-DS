# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import flight_pb2 as api__service_dot_flight__pb2


class FlightDataServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.SendFlightData = channel.unary_unary(
                '/flightdata.FlightDataService/SendFlightData',
                request_serializer=api__service_dot_flight__pb2.FlightDataRequest.SerializeToString,
                response_deserializer=api__service_dot_flight__pb2.NotifyFlightDataSuccess.FromString,
                )


class FlightDataServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def SendFlightData(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_FlightDataServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'SendFlightData': grpc.unary_unary_rpc_method_handler(
                    servicer.SendFlightData,
                    request_deserializer=api__service_dot_flight__pb2.FlightDataRequest.FromString,
                    response_serializer=api__service_dot_flight__pb2.NotifyFlightDataSuccess.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'flightdata.FlightDataService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class FlightDataService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def SendFlightData(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/flightdata.FlightDataService/SendFlightData',
            api__service_dot_flight__pb2.FlightDataRequest.SerializeToString,
            api__service_dot_flight__pb2.NotifyFlightDataSuccess.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)