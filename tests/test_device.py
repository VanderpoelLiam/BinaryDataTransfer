from src.device import UploadServicer
from src import file_server
from src import device
from src import binary_data_pb2
from src import binary_data_pb2_grpc
from concurrent import futures
import unittest
import grpc

def start_server(server, server_size, filename):
    binary_data_pb2_grpc.add_FileServerServicer_to_server(
        file_server.FileServerServicer(server_size, filename), server)
    server.add_insecure_port('[::]:50051')
    server.start()

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
        start_server(self.server, self.server_size, 'tests/test_empty.json')
        self.servicer = UploadServicer(get_stub())
        self.blob_id = binary_data_pb2.BlobId(id=42)
        self.chunk_index = 0
        self.payload = b"bag of bits"
        self.chunk = binary_data_pb2.Chunk(blob_id=self.blob_id,
                                            index=self.chunk_index,
                                            payload=self.payload)

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

    def test_UploadChunk(self):
        response = self.servicer.UploadChunk(self.chunk, self.context)
        self.assertEqual(response.error.description, "")
        expiration_time = file_server.get_expiration_time()
        updated_expiration_time = file_server.update_expiration_time(expiration_time)
        self.assertEqual(response.valid_until, updated_expiration_time)

    def test_UploadChunk_error(self):
        # TODO what should occur if upload chunk fails
        return

    @classmethod
    def tearDownClass(self):
        stop_server(self.server)
