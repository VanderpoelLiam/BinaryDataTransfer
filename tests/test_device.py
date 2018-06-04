from src.device import UploadServicer, DownloadServicer
from google.protobuf.json_format import MessageToJson
from src import file_server
from src import device
from src import binary_data_pb2
from src import binary_data_pb2_grpc
from concurrent import futures
from resources import wipe_json_file, read_db
import unittest
import grpc
import json

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


class TestUploadMethods(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        self.server_size = 100
        self.blob_spec = binary_data_pb2.BlobSpec(size=1, chunk_count=1)
        self.context = None
        self.default_filename = 'tests/test_empty.json'
        start_server(self.server, self.server_size, self.default_filename)
        self.servicer = UploadServicer(get_stub())
        self.blob_id = binary_data_pb2.BlobId(id=42)
        self.chunk_index = 0
        self.payload = b"bag of bits"
        self.chunk = binary_data_pb2.Chunk(blob_id=self.blob_id,
                                            index=self.chunk_index,
                                            payload=self.payload)

    @classmethod
    def tearDownClass(self):
        stop_server(self.server)

    def setUp(self):
        wipe_json_file(self.default_filename)

    def tearDown(self):
        wipe_json_file(self.default_filename)

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
        self.assertTrue(response.error.has_occured)

    def test_UploadChunk(self):
        response = self.servicer.UploadChunk(self.chunk, self.context)
        self.assertEqual(response.error.description, "")
        expiration_time = file_server.get_expiration_time()
        updated_expiration_time = file_server.update_expiration_time(expiration_time)
        self.assertEqual(response.valid_until, updated_expiration_time)

    def test_UploadChunk_error(self):
        # TODO what should occur if upload chunk fails
        return

    def test_DeleteBlob(self):
        error = self.servicer.DeleteBlob(self.blob_id, self.context)
        self.assertFalse(error.has_occured)

    def test_DeleteBlob_non_existant_id(self):
        blob_id = binary_data_pb2.BlobId(id=38302)
        error = self.servicer.DeleteBlob(blob_id, self.context)
        self.assertFalse(error.has_occured)

    def test_DeleteBlob_wrong_input(self):
        error = self.servicer.DeleteBlob(self.blob_spec, self.context)
        self.assertTrue(error.has_occured)

    def test_GetAverageBrightness(self):
        response = self.servicer.GetAverageBrightness(self.blob_id, self.context)
        self.assertEqual(response, binary_data_pb2.Empty())


class TestDownloadMethods(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        self.server_size = 100
        self.blob_spec = binary_data_pb2.BlobSpec(size=1, chunk_count=1)
        self.context = None
        self.default_filename = 'tests/test_empty.json'
        self.device_filename = 'tests/test_store_blob_info.json'
        start_server(self.server, self.server_size, self.default_filename)
        self.upload_servicer = UploadServicer(get_stub())
        self.download_servicer = DownloadServicer(get_stub(), self.device_filename)
        self.blob_id = binary_data_pb2.BlobId(id=42)
        self.chunk_index = 0
        self.payload = b"bag of bits"
        self.chunk_spec = binary_data_pb2.ChunkSpec(blob_id=self.blob_id,
                                            index=self.chunk_index)
        self.chunk = binary_data_pb2.Chunk(blob_id=self.blob_id,
                                            index=self.chunk_index,
                                            payload=self.payload)
    @classmethod
    def tearDownClass(self):
        stop_server(self.server)

    def setUp(self):
        wipe_json_file(self.default_filename)

    def tearDown(self):
        wipe_json_file(self.default_filename)

    def _create_blob(self):
        # Create a blob on the server and upload a chunk to this blob
        creation_response = self.upload_servicer.CreateBlob(self.blob_spec, self.context)
        blob_info = creation_response.blob_info
        chunk = binary_data_pb2.Chunk(blob_id=blob_info.id,
                                            index=self.chunk_index,
                                            payload=self.payload)
        self.upload_servicer.UploadChunk(chunk, self.context)
        return blob_info

    def test_GetChunk(self):
        # Create a blob on the server, upload a chunk to this blob and get the
        # resulting blob_info
        blob_info = self._create_blob()
        id = blob_info.id
        valid_until = blob_info.valid_until

        # Specify the chunk spec and download the chunk
        chunk_spec = binary_data_pb2.ChunkSpec(blob_id=id,
                                            index=self.chunk_index)
        response = self.download_servicer.GetChunk(chunk_spec, self.context)

        # Check the data matches
        self.assertEqual(response.payload, self.payload)
        self.assertEqual(response.valid_until, valid_until)

    def test_GetChunk_that_not_exist(self):
        response = self.download_servicer.GetChunk(self.chunk_spec, self.context)
        self.assertTrue(response.error.has_occured)

    def test_GetBlobInfo(self):
        expected_blob_info = self._create_blob()
        id = expected_blob_info.id
        actual_blob_info = self.download_servicer.GetBlobInfo(id, self.context)
        self.assertEqual(expected_blob_info.id, actual_blob_info.id)
        self.assertEqual(expected_blob_info.valid_until, actual_blob_info.valid_until)
        self.assertEqual(expected_blob_info.spec.size, actual_blob_info.spec.size)
        self.assertEqual(expected_blob_info.spec.chunk_count, actual_blob_info.spec.chunk_count)

    def test_GetMeasurementData_responds(self):
        response = self.download_servicer.GetMeasurementData(binary_data_pb2.Empty, self.context)
        blob_info = response.blob_info
        data, size = device.performMeasurement()
        self.assertEqual(blob_info.spec.size, size)
        self.assertEqual(blob_info.spec.chunk_count, 1)
        self.assertFalse(response.error.has_occured)
        self.assertEqual(response.valid_until, file_server.get_expiration_time())

    def test_GetMeasurementData_saves_to_server(self):
        measurement_response = self.download_servicer.GetMeasurementData(binary_data_pb2.Empty, self.context)
        data, size = device.performMeasurement()
        id = measurement_response.blob_info.id
        chunk_spec = binary_data_pb2.ChunkSpec(blob_id=id, index=0)
        chunk_response = self.download_servicer.GetChunk(chunk_spec, self.context)
        self.assertEqual(data, chunk_response.payload)

    def test_GetMeasurementData_stores_blob_info(self):
        measurement_response = self.download_servicer.GetMeasurementData(binary_data_pb2.Empty, self.context)
        id = measurement_response.blob_info.id
        blob_info = measurement_response.blob_info
        expected = device.read_blob_info(self.device_filename, id)
        self.assertEqual(blob_info, expected)

class TestHelperMethods(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.blob_spec = binary_data_pb2.BlobSpec(size=1, chunk_count=1)
        self.default_filename = 'tests/test_empty.json'
        self.blob_id = binary_data_pb2.BlobId(id=42)
        self.valid_until = file_server.get_expiration_time()
        self.blob_info = binary_data_pb2.BlobInfo(id=self.blob_id,
                                                valid_until=self.valid_until,
                                                spec=self.blob_spec)

    def setUp(self):
        wipe_json_file(self.default_filename)

    def tearDown(self):
        wipe_json_file(self.default_filename)

    def test_save_blob_info(self):
        device.save_blob_info(self.default_filename, self.blob_info)
        id = str(self.blob_id.id)
        data = read_db(self.default_filename)[id]
        self.assertEqual(data, MessageToJson(self.blob_info))

    def test_save_and_read_blob_info(self):
        device.save_blob_info(self.default_filename, self.blob_info)
        blob_info = device.read_blob_info(self.default_filename, self.blob_id)
        self.assertEqual(blob_info, self.blob_info)
