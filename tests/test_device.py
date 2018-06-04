import unittest

from google.protobuf.json_format import MessageToJson

from src import binary_data_pb2
from src import device
from src import file_server
import src.device.UploadServicer as UploadServicer
import src.device.DownloadServicer as DownloadServicer
from src.resources_files import wipe_json_file, read_db
from src.resources_server import start_file_server, get_file_server_stub, stop_server, get_grpc_server


class TestUploadMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = get_grpc_server()
        cls.server_size = 100
        cls.blob_spec = binary_data_pb2.BlobSpec(size=1, chunk_count=1)
        cls.context = None
        cls.device_filename = 'tests/test_store_blob_info.json'
        cls.default_filename = 'tests/test_empty.json'
        port = '50051'
        start_file_server(cls.server, cls.server_size, cls.default_filename, port)
        cls.servicer = UploadServicer(get_file_server_stub(port), cls.device_filename)
        cls.blob_id = binary_data_pb2.BlobId(id=42)
        cls.chunk_index = 0
        cls.payload = b"bag of bits"
        cls.chunk = binary_data_pb2.Chunk(blob_id=cls.blob_id,
                                           index=cls.chunk_index,
                                           payload=cls.payload)

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
        self.server = get_grpc_server()
        self.server_size = 100
        self.blob_spec = binary_data_pb2.BlobSpec(size=1, chunk_count=1)
        self.context = None
        self.default_filename = 'tests/test_empty.json'
        self.device_filename = 'tests/test_store_blob_info.json'
        port = '50051'
        start_file_server(self.server, self.server_size, self.default_filename, port)
        self.upload_servicer = UploadServicer(get_file_server_stub(port), self.device_filename)
        self.download_servicer = DownloadServicer(get_file_server_stub(port), self.device_filename)
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
        print(MessageToJson(expected_blob_info))
        print(MessageToJson(actual_blob_info))
        self.assertEqual(expected_blob_info.id, actual_blob_info.id)
        self.assertEqual(expected_blob_info.valid_until, actual_blob_info.valid_until)
        self.assertEqual(expected_blob_info.spec.size, actual_blob_info.spec.size)
        self.assertEqual(expected_blob_info.spec.chunk_count, actual_blob_info.spec.chunk_count)

    def test_GetMeasurementData_responds(self):
        response = self.download_servicer.GetMeasurementData(binary_data_pb2.Empty, self.context)
        blob_info = response.blob_info
        data, size = device.perform_measurement()
        self.assertEqual(blob_info.spec.size, size)
        self.assertEqual(blob_info.spec.chunk_count, 1)
        self.assertFalse(response.error.has_occured)
        self.assertEqual(response.valid_until, file_server.get_expiration_time())

    def test_GetMeasurementData_saves_to_server(self):
        measurement_response = self.download_servicer.GetMeasurementData(binary_data_pb2.Empty, self.context)
        data, size = device.perform_measurement()
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
