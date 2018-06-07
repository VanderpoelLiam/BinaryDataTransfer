import unittest

from src import binary_data_pb2
from src import file_server
from src.file_server import FileServerServicer
from src.resources_files import wipe_json_file


class TestAcessingDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.id = 42
        cls.payload = b"bag of bits"
        cls.blob_id = binary_data_pb2.BlobId(id=cls.id)
        cls.index = 2
        cls.test_path = "tests/"
        cls.chunk = binary_data_pb2.Chunk(blob_id=cls.blob_id,
                                          index=cls.index,
                                          payload=cls.payload)
        cls.chunk1 = binary_data_pb2.Chunk(blob_id=cls.blob_id,
                                           index=cls.index + 1,
                                           payload=cls.payload)

    def test_read_chunk_payload(self):
        # Setup
        filename = self.test_path + 'test_read_chunk_payload.json'
        # Test
        actual = file_server.read_chunk_payload(filename, self.blob_id,
                                                self.index)
        self.assertIsInstance(actual, bytes)
        self.assertEqual(actual, self.payload)

    def test_read_missing_blob_id(self):
        # Setup
        filename = self.test_path + 'test_empty.json'
        # Test
        self.assertRaises(KeyError, file_server.read_chunk_payload, filename,
                          self.blob_id, self.index)

    def test_read_missing_index(self):
        # Setup
        filename = self.test_path + 'test_read_chunk_payload.json'
        # Test
        self.assertRaises(KeyError, file_server.read_chunk_payload, filename,
                          self.blob_id, self.index - 1)

    def test_write_chunk(self):
        # Setup
        filename = self.test_path + 'test_empty.json'
        # Test
        file_server.write_chunk(filename, self.chunk)
        actual_payload = file_server.read_chunk_payload(filename, self.blob_id,
                                                        self.index)
        self.assertEqual(actual_payload, self.payload)
        file_server.write_chunk(filename, self.chunk1)
        actual_payload = file_server.read_chunk_payload(filename, self.blob_id,
                                                        self.index)
        self.assertEqual(actual_payload, self.payload)
        actual_payload = file_server.read_chunk_payload(filename, self.blob_id,
                                                        self.index + 1)
        self.assertEqual(actual_payload, self.payload)
        wipe_json_file(filename)

    def test_remove_blob(self):
        # Setup
        filename = self.test_path + 'test_empty.json'
        file_server.write_chunk(filename, self.chunk)
        # Test
        file_server.remove_blob(filename, self.blob_id)
        self.assertRaises(KeyError, file_server.read_chunk_payload, filename,
                          self.blob_id, self.index)
        wipe_json_file(filename)

    def test_remove_blob_non_existant_blob_id(self):
        # Setup
        filename = self.test_path + 'test_empty.json'
        # Test
        self.assertRaises(file_server.BlobNotFoundException,
                          file_server.remove_blob, filename, self.blob_id)
        wipe_json_file(filename)


class TestServerMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server_size = 100
        cls.blob_spec = binary_data_pb2.BlobSpec(size=1, chunk_count=1)
        cls.context = None
        cls.default_filename = 'tests/test_empty.json'
        cls.server = FileServerServicer(cls.server_size, cls.default_filename)
        cls.blob_id = binary_data_pb2.BlobId(id=42)
        cls.chunk_index = 0
        cls.payload = b"bag of bits"
        cls.chunk_spec = binary_data_pb2.ChunkSpec(blob_id=cls.blob_id,
                                                   index=cls.chunk_index)
        cls.chunk = binary_data_pb2.Chunk(blob_id=cls.blob_id,
                                          index=cls.chunk_index,
                                          payload=cls.payload)

    def test_ValidateFileServer_payload(self):
        response = self.server.ValidateFileServer(self.blob_spec, self.context)
        self.assertEqual(response.valid_until,
                         file_server.get_expiration_time())

    def test_ValidateFileServer_error(self):
        blob_size = self.server_size * 2
        error_blob_spec = binary_data_pb2.BlobSpec(size=blob_size,
                                                   chunk_count=1)
        response = self.server.ValidateFileServer(error_blob_spec, self.context)
        self.assertTrue(response.error.has_occured)

    def test_Save(self):
        response = self.server.Save(self.chunk, self.context)
        self.assertFalse(response.error.has_occured)
        expiration_time = file_server.get_expiration_time()
        updated_expiration_time = file_server.update_expiration_time(
            expiration_time)
        self.assertEqual(response.valid_until, updated_expiration_time)

    def test_Delete(self):
        self.server.Save(self.chunk, self.context)
        error = self.server.Delete(self.blob_id, self.context)
        self.assertFalse(error.has_occured)

    def test_Delete_on_non_existant_blob(self):
        blob_id = binary_data_pb2.BlobId(id=23892)
        error = self.server.Delete(blob_id, self.context)
        self.assertFalse(error.has_occured)

    def test_Delete_on_wrong_input(self):
        error = self.server.Delete(self.chunk, self.context)
        self.assertTrue(error.has_occured)

    def test_Dowload(self):
        self.server.Save(self.chunk, self.context)
        response = self.server.Download(self.chunk_spec, self.context)
        self.assertEqual(response.valid_until,
                         file_server.get_expiration_time())
        self.assertEqual(response.payload, self.payload)

    def test_Dowload_chunk_not_exist(self):
        response = self.server.Download(self.chunk_spec, self.context)
        self.assertTrue(response.error.has_occured)

    def test_Dowload_after_delete(self):
        self.server.Save(self.chunk, self.context)
        self.server.Delete(self.blob_id, self.context)
        response = self.server.Download(self.chunk_spec, self.context)
        self.assertTrue(response.error.has_occured)

    def test_ValidateFileServer_wrong_input_type(self):
        response = self.server.ValidateFileServer(None, self.context)
        self.assertTrue(response.error.has_occured)

    def test_Save_wrong_input_type(self):
        response = self.server.Save(None, self.context)
        self.assertTrue(response.error.has_occured)

    def test_Download_wrong_input_type(self):
        response = self.server.Download(None, self.context)
        self.assertTrue(response.error.has_occured)

    def test_Delete_wrong_input_type(self):
        error = self.server.Delete(None, self.context)
        self.assertTrue(error.has_occured)

    def setUp(self):
        wipe_json_file(self.default_filename)

    def tearDown(self):
        wipe_json_file(self.default_filename)


if __name__ == '__main__':
    unittest.main()
