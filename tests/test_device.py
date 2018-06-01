from src.device import UploadServicer
from src import file_server
from src import device
from src import binary_data_pb2
from src import binary_data_pb2_grpc
from concurrent import futures
import unittest
import grpc

def start_server(server, server_size):
    binary_data_pb2_grpc.add_FileServerServicer_to_server(
        file_server.FileServerServicer(server_size, ''), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    # try:
    #     while True:
    #         print("\nServer is ready...")
    #         time.sleep(_ONE_DAY_IN_SECONDS)
    # except KeyboardInterrupt:
    #     server.stop(0)

def stop_server(server):
    server.stop(0)

def get_stub():
    channel = grpc.insecure_channel('localhost:50051')
    stub = binary_data_pb2_grpc.FileServerStub(channel)
    return stub

class TestServerMethods(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        self.server_size = 100
        self.blob_spec = binary_data_pb2.BlobSpec(size=1, chunk_count=1)
        self.context = None
        start_server(self.server, self.server_size)
        self.servicer = UploadServicer(get_stub())

    def test_CreateBlob(self):
        response = self.servicer.CreateBlob(self.blob_spec, self.context)
        blob_info = response.blob_info
        self.assertEqual(blob_info.valid_until, file_server.get_expiration_time())
        id = self.servicer._get_current_blob_id().id
        self.assertEqual(blob_info.id.id, id - 1)

    def test_CreateBlob_error(self):
        blob_size = self.server_size * 2
        error_blob_spec = binary_data_pb2.BlobSpec(size=blob_size, chunk_count=1)
        response = self.servicer.CreateBlob(error_blob_spec, self.context)
        self.assertEqual(response.error, file_server.get_error())

    @classmethod
    def tearDownClass(self):
        stop_server(self.server)
