import unittest
import math
import os

from google.protobuf.json_format import MessageToJson

from src import binary_data_pb2
from src import device
from src import file_server
from src.device import DownloadServicer
from src.device import UploadServicer
from src.resources_files import wipe_json_file, read_db
from src.resources_server import start_file_server, get_file_server_stub, \
    stop_server, get_grpc_server


class TestUploadMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = get_grpc_server()
        cls.server_size = 100
        cls.blob_spec = binary_data_pb2.BlobSpec(size=10, chunk_count=2)
        cls.context = None
        cls.device_filename = 'tests/test_store_blob_info.json'
        cls.default_filename = 'tests/test_empty.json'
        start_file_server(cls.server, cls.server_size, cls.default_filename)
        cls.servicer = UploadServicer(get_file_server_stub(),
                                      cls.device_filename)
        cls.blob_id = binary_data_pb2.BlobId(id=42)
        cls.chunk_index = 0
        cls.payload = b"bag of bits"
        cls.chunk = binary_data_pb2.Chunk(blob_id=cls.blob_id,
                                          index=cls.chunk_index,
                                          payload=cls.payload)

    @classmethod
    def tearDownClass(cls):
        stop_server(cls.server)

    def setUp(self):
        wipe_json_file(self.default_filename)
        wipe_json_file(self.device_filename)

    def tearDown(self):
        wipe_json_file(self.default_filename)
        wipe_json_file(self.device_filename)

    def test_CreateBlob(self):
        # TODO fix issue with below response line
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
        response = self.servicer.DeleteBlob(self.blob_id, self.context)
        self.assertFalse(response.error.has_occured)

    def test_DeleteBlob_non_existant_id(self):
        blob_id = binary_data_pb2.BlobId(id=38302)
        response = self.servicer.DeleteBlob(blob_id, self.context)
        self.assertFalse(response.error.has_occured)

    def test_DeleteBlob_wrong_input(self):
        response = self.servicer.DeleteBlob(self.blob_spec, self.context)
        self.assertTrue(response.error.has_occured)

    def test_GetAverageBrightness(self):
        # TODO write a proper tests that uploads an image first

        # self.server_size = math.inf
        # blob_id = binary_data_pb2.BlobId(id=0) # THIS IS A HACK
        # response = self.servicer.GetAverageBrightness(blob_id, self.context)
        # payload = response.payload
        # result = device.bytes_to_int(payload)
        # image_filename = 'images/cat.png'
        # catIm = Image.open(image_filename)
        # expected_result = device.average_image_brightness(catIm)
        # self.assertEqual(result, expected_result)
        return


class TestDownloadMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = get_grpc_server()
        cls.server_size = 100
        cls.blob_spec = binary_data_pb2.BlobSpec(size=1, chunk_count=1)
        cls.context = None
        cls.default_filename = 'tests/test_empty.json'
        cls.device_filename = 'tests/test_store_blob_info.json'
        start_file_server(cls.server, cls.server_size, cls.default_filename)
        cls.upload_servicer = UploadServicer(get_file_server_stub(), cls.device_filename)
        cls.download_servicer = DownloadServicer(get_file_server_stub(), cls.device_filename)
        cls.blob_id = binary_data_pb2.BlobId(id=42)
        cls.chunk_index = 0
        cls.payload = b"bag of bits"
        cls.chunk_spec = binary_data_pb2.ChunkSpec(blob_id=cls.blob_id,
                                                    index=cls.chunk_index)
        cls.chunk = binary_data_pb2.Chunk(blob_id=cls.blob_id,
                                           index=cls.chunk_index,
                                           payload=cls.payload)

    @classmethod
    def tearDownClass(cls):
        stop_server(cls.server)

    def setUp(self):
        wipe_json_file(self.default_filename)
        wipe_json_file(self.device_filename)

    def tearDown(self):
        wipe_json_file(self.default_filename)
        wipe_json_file(self.device_filename)

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
        # response = self.download_servicer.GetMeasurementData(binary_data_pb2.Empty(), self.context)
        # blob_info = response.blob_info
        # data, size = device.perform_measurement()
        # self.assertEqual(blob_info.spec.size, size)
        # self.assertEqual(blob_info.spec.chunk_count, 1)
        # self.assertFalse(response.error.has_occured)
        # self.assertEqual(response.valid_until, file_server.get_expiration_time())
        # TODO
        return

    def test_GetMeasurementData_saves_to_server(self):
        # measurement_response = self.download_servicer.GetMeasurementData(binary_data_pb2.Empty(), self.context)
        # data, size = device.perform_measurement()
        # id = measurement_response.blob_info.id
        # chunk_spec = binary_data_pb2.ChunkSpec(blob_id=id, index=0)
        # chunk_response = self.download_servicer.GetChunk(chunk_spec, self.context)
        # self.assertEqual(data, chunk_response.payload)
        # # TODO:
        return

    def test_GetMeasurementData_stores_blob_info(self):
        # measurement_response = self.download_servicer.GetMeasurementData(binary_data_pb2.Empty(), self.context)
        # id = measurement_response.blob_info.id
        # blob_info = measurement_response.blob_info
        # expected = device.read_blob_info(self.device_filename, id)
        # self.assertEqual(blob_info, expected)
        # # TODO:
        return


class TestHelperMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blob_spec = binary_data_pb2.BlobSpec(size=1, chunk_count=1)
        cls.default_filename = 'tests/test_empty.json'
        cls.blob_id = binary_data_pb2.BlobId(id=42)
        cls.valid_until = file_server.get_expiration_time()
        cls.blob_info = binary_data_pb2.BlobInfo(id=cls.blob_id,
                                                  valid_until=cls.valid_until,
                                                  spec=cls.blob_spec)

        cls.server = get_grpc_server()
        cls.server_size = math.inf
        cls.default_filename = 'tests/test_empty.json'
        cls.device_filename = 'tests/test_store_blob_info.json'
        start_file_server(cls.server, cls.server_size, cls.default_filename)
        cls.upload_servicer = UploadServicer(get_file_server_stub(),
                                             cls.device_filename)
        cls.download_servicer = DownloadServicer(get_file_server_stub(),
                                                 cls.device_filename)

    @classmethod
    def tearDownClass(cls):
        stop_server(cls.server)

    def setUp(self):
        wipe_json_file(self.default_filename)
        wipe_json_file(self.device_filename)

    def tearDown(self):
        wipe_json_file(self.default_filename)
        wipe_json_file(self.device_filename)

    def test_save_blob_info(self):
        device.save_blob_info(self.default_filename, self.blob_info)
        id = str(self.blob_id.id)
        data = read_db(self.default_filename)[id]
        self.assertEqual(data, MessageToJson(self.blob_info))

    def test_save_and_read_blob_info(self):
        device.save_blob_info(self.default_filename, self.blob_info)
        blob_info = device.read_blob_info(self.default_filename, self.blob_id)
        self.assertEqual(blob_info, self.blob_info)

    def test_upload_image(self):
        image_filename = 'images/puppy.jpg'
        size = os.stat(image_filename).st_size  # File size in bytes
        chunk_count = 10
        chunk_size = math.ceil(size / chunk_count)

        # Define spec and create a blob to store this data on the server
        blob_spec = binary_data_pb2.BlobSpec(size=size, chunk_count=chunk_count)
        creation_response = self.upload_servicer.CreateBlob(blob_spec, None)

        blob_id = creation_response.blob_info.id

        upload_response = device.upload_image(self.upload_servicer,
                                              image_filename, blob_id,
                                              chunk_count, chunk_size)
        self.assertFalse(upload_response.error.has_occured)

    def test_upload_image_error(self):
        # TODO
        return

    def test_perform_measurement(self):
        blob_info = device.perform_measurement()
        blob_id = blob_info.id
        self.assertEqual(blob_info, self.download_servicer.GetBlobInfo(blob_id))

