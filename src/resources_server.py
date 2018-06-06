from concurrent import futures

import binary_data_pb2_grpc
import file_server
import grpc


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
