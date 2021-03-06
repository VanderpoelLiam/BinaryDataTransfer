import sys
from concurrent import futures

import binary_data_pb2
import binary_data_pb2_grpc
import file_server
import grpc

_TIMEOUT_IN_SECONDS = 10


def start_file_server(server, server_size, filename):
    binary_data_pb2_grpc.add_FileServerServicer_to_server(
        file_server.FileServerServicer(server_size, filename), server)
    server.add_insecure_port('[::]:50051')
    server.start()


def stop_server(server):
    server.stop(0)


def get_file_server_stub():
    channel = grpc.insecure_channel('localhost:50051')
    stub = binary_data_pb2_grpc.FileServerStub(channel)
    return stub


def get_grpc_server():
    return grpc.server(futures.ThreadPoolExecutor(max_workers=10))


def client_caller(method, arg, method_name, attempt_reconnection=True):
    # This ensures robustsness to connection losses
    while True:
        try:
            response = method(arg, timeout=_TIMEOUT_IN_SECONDS)
        except KeyboardInterrupt:
            sys.exit('')
            break
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                sys.exit(
                    '\nCould not reconnect to the server before the deadline was exceeded')
            elif e.code() == grpc.StatusCode.INTERNAL:
                print('\n%s failed unexpectedly' % method_name)
            elif e.code() == grpc.StatusCode.UNAVAILABLE:
                print('\nServer is unavailible')
            else:
                sys.exit(
                    '\n{0} failed with {1}: {2}'.format(method_name, e.code(),
                                                        e.details()))
        else:
            return response

        if not attempt_reconnection:
            sys.exit('\nNot attempting to reconnect to server')
            break


def type_check(actual_object, expected_type):
    temp = expected_type()
    try:
        temp.CopyFrom(actual_object)
    except TypeError:
        error = binary_data_pb2.Error(has_occured=True,
                                      description="Wrong input type")
        return binary_data_pb2.Response(error=error)
    else:
        return binary_data_pb2.Response()
