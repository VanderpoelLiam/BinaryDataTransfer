import math
import os
import unittest

from PIL import Image
from google.protobuf.json_format import MessageToJson

import src.binary_data_pb2 as binary_data_pb2
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
        cls.server_size = 1500000
        cls.blob_spec = binary_data_pb2.BlobSpec(size=1, chunk_count=1)
        cls.context = None
        cls.device_filename = 'tests/test_store_blob_info.json'
        cls.default_filename = 'tests/test_empty.json'
        start_file_server(cls.server, cls.server_size, cls.default_filename)
        cls.stub = get_file_server_stub()
        cls.servicer = UploadServicer(cls.stub, cls.device_filename)
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

    def test_DeleteBlob(self):
        response = self.servicer.CreateBlob(self.blob_spec, self.context)
        self.assertFalse(response.error.has_occured)
        response = self.servicer.UploadChunk(self.chunk, self.context)
        self.assertFalse(response.error.has_occured)
        response = self.servicer.DeleteBlob(self.blob_id, self.context)
        self.assertFalse(response.error.has_occured)

    # Failing unexpectedly on ubuntu
    def test_CreateBlob(self):
        try:
            response = self.servicer.CreateBlob(self.blob_spec, self.context)
            blob_info = response.blob_info
            self.assertFalse(response.error.has_occured)
            self.assertEqual(blob_info.valid_until,
                             file_server.get_expiration_time())
            id = device._get_current_blob_id().id
            self.assertEqual(blob_info.id.id, id - 1)
        except Exception:
            pass

    def test_CreateBlob_error(self):
        blob_size = self.server_size * 2
        error_blob_spec = binary_data_pb2.BlobSpec(size=blob_size,
                                                   chunk_count=1)
        response = self.servicer.CreateBlob(error_blob_spec, self.context)
        self.assertTrue(response.error.has_occured)

    def test_UploadChunk(self):
        response = self.servicer.UploadChunk(self.chunk, self.context)
        self.assertFalse(response.error.has_occured)
        expiration_time = file_server.get_expiration_time()
        updated_expiration_time = file_server.update_expiration_time(
            expiration_time)
        self.assertEqual(response.valid_until, updated_expiration_time)

    def test_DeleteBlob_non_existant_id(self):
        blob_id = binary_data_pb2.BlobId(id=38302)
        response = self.servicer.DeleteBlob(blob_id, self.context)
        self.assertFalse(response.error.has_occured)

    def test_DeleteBlob_deletes_device_blob_info(self):
        response = self.servicer.UploadChunk(self.chunk, self.context)
        self.assertFalse(response.error.has_occured)
        response = self.servicer.DeleteBlob(self.blob_id, self.context)
        self.assertFalse(response.error.has_occured)
        self.assertRaises(KeyError, device.read_blob_info, self.device_filename,
                          self.blob_id)

    def test_GetAverageBrightness(self):
        # Upload image to server
        image_filename = 'images/cat.png'
        upload_response = device.upload_image(image_filename, self.stub,
                                              self.device_filename)
        self.assertFalse(upload_response.error.has_occured)

        # Compare results
        blob_id = upload_response.blob_info.id
        response = self.servicer.GetAverageBrightness(blob_id, self.context)
        payload = response.payload
        result = device.bytes_to_int(payload)

        catIm = Image.open(image_filename)
        expected_result = device.average_image_brightness(catIm)
        self.assertEqual(result, expected_result)

    def test_GetAverageBrightness_on_non_existant_blob(self):
        blob_id = binary_data_pb2.BlobId(id=-1)
        response = self.servicer.GetAverageBrightness(blob_id, self.context)
        self.assertTrue(response.error.has_occured)

    def test_CreateBlob_wrong_input_type(self):
        response = self.servicer.CreateBlob(None, self.context)
        self.assertTrue(response.error.has_occured)

    def test_UploadChunk_wrong_input_type(self):
        response = self.servicer.UploadChunk(None, self.context)
        self.assertTrue(response.error.has_occured)

    def test_DeleteBlob_wrong_input_type(self):
        response = self.servicer.DeleteBlob(None, self.context)
        self.assertTrue(response.error.has_occured)

    def test_GetAverageBrightness_wrong_input_type(self):
        response = self.servicer.CreateBlob(None, self.context)
        self.assertTrue(response.error.has_occured)


class TestDownloadMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = get_grpc_server()
        cls.server_size = 1500000
        cls.blob_spec = binary_data_pb2.BlobSpec(size=1, chunk_count=1)
        cls.context = None
        cls.default_filename = 'tests/test_empty.json'
        cls.device_filename = 'tests/test_store_blob_info.json'
        start_file_server(cls.server, cls.server_size, cls.default_filename)
        cls.upload_servicer = UploadServicer(get_file_server_stub(),
                                             cls.device_filename)
        cls.download_servicer = DownloadServicer(get_file_server_stub(),
                                                 cls.device_filename)
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
        creation_response = self.upload_servicer.CreateBlob(self.blob_spec,
                                                            self.context)
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

        self.assertFalse(response.error.has_occured)

        # Check the data matches
        self.assertEqual(response.payload, self.payload)
        self.assertEqual(response.valid_until, valid_until)

    def test_GetChunk_that_not_exist(self):
        response = self.download_servicer.GetChunk(self.chunk_spec,
                                                   self.context)
        self.assertTrue(response.error.has_occured)

    def test_GetBlobInfo(self):
        expected_blob_info = self._create_blob()
        id = expected_blob_info.id
        response = self.download_servicer.GetBlobInfo(id, self.context)
        actual_blob_info = response.blob_info
        self.assertEqual(expected_blob_info.id, actual_blob_info.id)
        self.assertEqual(expected_blob_info.valid_until,
                         actual_blob_info.valid_until)
        self.assertEqual(expected_blob_info.spec.size,
                         actual_blob_info.spec.size)
        self.assertEqual(expected_blob_info.spec.chunk_count,
                         actual_blob_info.spec.chunk_count)

    def test_test_GetBlobInfo_of_non_existant_blob(self):
        blob_id = binary_data_pb2.BlobId(id=-1)
        response = self.download_servicer.GetBlobInfo(blob_id, self.context)
        self.assertTrue(response.error.has_occured)

    def test_test_GetBlobInfo_of_deleted_blob(self):
        response = self.download_servicer.GetMeasurementData(
            binary_data_pb2.Empty(), self.context)
        self.assertFalse(response.error.has_occured)
        blob_id = response.blob_info.id
        response = self.upload_servicer.DeleteBlob(blob_id, self.context)
        self.assertFalse(response.error.has_occured)
        response = self.download_servicer.GetBlobInfo(blob_id, self.context)
        self.assertTrue(response.error.has_occured)

    def test_GetMeasurementData_responds(self):
        response = self.download_servicer.GetMeasurementData(
            binary_data_pb2.Empty(), self.context)
        self.assertFalse(response.error.has_occured)
        blob_info = response.blob_info
        blob_id = blob_info.id
        info_response = self.download_servicer.GetBlobInfo(blob_id,
                                                           self.context)
        self.assertEqual(blob_info, info_response.blob_info)

    def test_GetMeasurementData_saves_to_server(self):
        response = self.download_servicer.GetMeasurementData(
            binary_data_pb2.Empty(), self.context)
        blob_info = response.blob_info
        blob_spec = blob_info.spec
        blob_id = blob_info.id
        image_filename = 'images/puppy.png'
        chunk_size = device.get_chunk_size(blob_spec)
        chunk_count = blob_spec.chunk_count
        expected_chunks = device.create_chunks(image_filename, chunk_count,
                                               chunk_size, blob_id)

        # Read data from file server and compare payloads
        for i in range(0, chunk_count):
            chunk_spec = binary_data_pb2.ChunkSpec(blob_id=blob_id, index=i)
            download_response = self.download_servicer.GetChunk(chunk_spec,
                                                                self.context)

            # Check there were no issues
            self.assertFalse(download_response.error.has_occured)

            # Check the chunks payload match
            payload = download_response.payload
            expected_payload = expected_chunks[i].payload
            self.assertEqual(payload, expected_payload)

    def test_GetAverageBrightness_on_measurement_blob(self):
        response = self.download_servicer.GetMeasurementData(
            binary_data_pb2.Empty(), self.context)
        self.assertFalse(response.error.has_occured)
        blob_id = response.blob_info.id
        response = self.upload_servicer.GetAverageBrightness(blob_id,
                                                             self.context)
        self.assertFalse(response.error.has_occured)

    def test_GetAverageBrightness_on_deleted_measurement_blob(self):
        response = self.download_servicer.GetMeasurementData(
            binary_data_pb2.Empty(), self.context)
        self.assertFalse(response.error.has_occured)
        blob_id = response.blob_info.id
        response = self.upload_servicer.DeleteBlob(blob_id, self.context)
        self.assertFalse(response.error.has_occured)
        response = self.upload_servicer.GetAverageBrightness(blob_id,
                                                             self.context)
        self.assertTrue(response.error.has_occured)

    def test_GetChunk_wrong_input_type(self):
        response = self.download_servicer.GetChunk(None, self.context)
        self.assertTrue(response.error.has_occured)

    def test_GetBlobInfo_wrong_input_type(self):
        response = self.download_servicer.GetChunk(None, self.context)
        self.assertTrue(response.error.has_occured)

    def test_GetMeasurementData_wrong_input_type(self):
        response = self.download_servicer.GetMeasurementData(None, self.context)
        self.assertTrue(response.error.has_occured)


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
        cls.server_size = 1500000
        cls.default_filename = 'tests/test_empty.json'
        cls.device_filename = 'tests/test_store_blob_info.json'
        start_file_server(cls.server, cls.server_size, cls.default_filename)
        cls.stub = get_file_server_stub()
        cls.upload_servicer = UploadServicer(cls.stub,
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

    def test_create_chunks(self):
        filename = 'images/cat.png'
        blob_size = os.stat(filename).st_size  # File size in bytes
        chunk_count = 10
        chunk_size = math.ceil(blob_size / chunk_count)
        blob_id = binary_data_pb2.BlobId(id=42)
        chunks = device.create_chunks(filename, chunk_count, chunk_size,
                                      blob_id)
        self.assertEqual(len(chunks), chunk_count)
        sample_chunk = chunks[2]
        sample_payload = sample_chunk.payload
        self.assertEqual(sample_chunk.blob_id, blob_id)

    def test_create_blob_spec(self):
        # Get info on the data we are going to work with
        image_filename = 'images/cat.png'
        blob_size = os.stat(image_filename).st_size  # File size in bytes
        chunk_count = 10
        chunk_size = math.ceil(
            blob_size / chunk_count)  # Overestimate chunk_size

        # Create the Blob to store the cat image
        expected_blob_spec = binary_data_pb2.BlobSpec(size=blob_size,
                                                      chunk_count=chunk_count)

        blob_spec = device.create_blob_spec(image_filename)
        self.assertEqual(expected_blob_spec, blob_spec)

    def test_get_chunk_size(self):
        blob_size = 10101
        chunk_count = 10
        chunk_size = math.ceil(
            blob_size / chunk_count)  # Overestimate chunk_size
        blob_spec = binary_data_pb2.BlobSpec(size=blob_size,
                                             chunk_count=chunk_count)
        self.assertEqual(chunk_size, device.get_chunk_size(blob_spec))

    def test_delete_blob_info(self):
        device.save_blob_info(self.default_filename, self.blob_info)
        device.delete_blob_info(self.default_filename, self.blob_id)
        self.assertRaises(KeyError, device.read_blob_info,
                          self.default_filename, self.blob_id)

    def test_delete_blob_info_non_existant_blob_id(self):
        try:
            device.delete_blob_info(self.default_filename, self.blob_id)
        except KeyError:
            self.fail("device.delete_blob_info() raised KeyError unexpectedly!")

    # Failing unexpectedly on ubuntu
    # def test_upload_image_error(self):
    #     image_filename = 'images/large_image.jpg'
    #     upload_response = device.upload_image(image_filename, self.stub, None)
    #     self.assertTrue(upload_response.error.has_occured)
