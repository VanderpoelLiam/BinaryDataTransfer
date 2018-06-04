from concurrent import futures

import grpc

import binary_data_pb2_grpc
import device
import file_server


def start_file_server(server, server_size, filename, port):
    binary_data_pb2_grpc.add_FileServerServicer_to_server(
        file_server.FileServerServicer(server_size, filename), server)
    server.add_insecure_port('[::]:' + port)
    server.start()


def start_upload_server(server_files, server_device, device_filename, file_server_filename, device_port, file_port):
    # Start a file server
    file_server_size = 10 ** 6  # Size in bits
    start_file_server(server_files, file_server_size, file_server_filename, file_port)
    # Start an upload server
    file_server_stub = get_file_server_stub(file_port)
    binary_data_pb2_grpc.add_UploadServicer_to_server(
        device.UploadServicer(file_server_stub, device_filename), server_device)
    server_device.add_insecure_port('[::]:' + device_port)
    server_device.start()


def stop_server(server):
    server.stop(0)


def stop_upload_server(server_files, server_device):
    server_files.stop(0)
    server_device.stop(0)


def get_file_server_stub(port):
    channel = grpc.insecure_channel('localhost:' + port)
    stub = binary_data_pb2_grpc.FileServerStub(channel)
    return stub


def get_upload_stub(port):
    channel = grpc.insecure_channel('localhost:' + port)
    stub = binary_data_pb2_grpc.UploadStub(channel)
    return stub


def get_grpc_server():
    return grpc.server(futures.ThreadPoolExecutor(max_workers=10))