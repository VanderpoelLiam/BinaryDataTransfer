# from file_server import read_db
# import json
from src import binary_data_pb2
from src import file_server
from src.file_server import FileServerServicer
import unittest

# def test_read_expected():
#     data = {}
#     for i in range(1,4):
#         data[str(i)] = "Data for blob %i" % i
#     return data
#
# def wipe_json_file(filename):
#     data = {}
#     with open(filename, 'w') as fp:
#         json.dump(data, fp)

# class TestAcessingDatabase(unittest.TestCase):
#     @classmethod
#     def setUpClass(self):
#         # print("setUpClass TestAcessingDatabase")
#         self._id = 42
#         self._payload = b"bag of bits"
#         self._blob_id = binary_data_pb2.BlobId(id=self._id)
#         self._blob = binary_data_pb2.Blob(id=self._blob_id, payload=self._payload)
#
#     def test_read_db(self):
#         self.assertEqual(read_db('test_read.json'), test_read_expected())
#
#     def test_write_db(self):
#         # Setup
#         filename = 'test_empty.json'
#         expected_data = test_read_expected()
#         wipe_json_file(filename)
#         # Test
#         file_server.write_db(filename, expected_data)
#         self.assertEqual(file_server.read_db(filename), expected_data)
#         wipe_json_file(filename)
#
#     def test_read_blob_payload(self):
#         # Setup
#         filename = 'test_read_blob_payload.json'
#         # Test
#         actual = file_server.read_blob_payload(filename, self._blob_id)
#         self.assertIsInstance(actual, bytes)
#         self.assertEqual(actual, self._payload)
#
#     def test_read_blob_empty_payload(self):
#         # Setup
#         filename = 'test_empty.json'
#         # Test
#         actual = file_server.read_blob_payload(filename, self._blob_id)
#         self.assertIsNone(actual)
#
#     def test_write_blob(self):
#         # Setup
#         filename = 'test_empty.json'
#         # Test
#         file_server.write_blob(filename, self._blob)
#         actual_payload = file_server.read_blob_payload(filename, self._blob_id)
#         self.assertEqual(actual_payload, self._payload)
#         wipe_json_file(filename)
#
#     def test_remove_by_key_db(self):
#         # Setup
#         filename = 'test_empty.json'
#         key = "1"
#         input_data = test_read_expected()
#         file_server.write_db(filename, input_data)
#         expected = input_data
#         del expected[key]
#         # Test
#         file_server.remove_by_key_db(filename, key)
#         actual = file_server.read_db(filename)
#         self.assertEqual(actual, expected)
#         wipe_json_file(filename)
#
#     def test_remove_blob(self):
#         # Setup
#         filename = 'test_empty.json'
#         file_server.write_blob(filename, self._blob)
#         expected = None
#         # Test
#         file_server.remove_blob(filename, self._blob_id)
#         actual = file_server.read_blob_payload(filename, self._blob_id)
#         self.assertEqual(actual, expected)
#         wipe_json_file(filename)
# class TestAcessingBlobs(unittest.TestCase):
#     @classmethod
#     def setUpClass(self):
#         # print("setUpClass TestAcessingDatabase")
#         self._id = 42
#         self._payload = b"bag of bits"
#         self._blob_id = binary_data_pb2.BlobId(id=self._id)
#         self._blob = binary_data_pb2.Blob(id=self._blob_id, payload=self._payload)
#
#     def test_download_blob(self):
#         # Setup
#         filename = 'test_read_blob_payload.json'
#
#         # Test
#         actual_blob = file_server.download_blob(filename, self._blob_id)
#         self.assertIsInstance(actual_blob, binary_data_pb2.Blob)
#         # Blob id and payload determine equality
#         self.assertEqual(actual_blob.id, self._blob.id)
#         self.assertEqual(actual_blob.payload, self._blob.payload)
#
#     def test_download_blob_not_there(self):
#         # Setup
#         filename = 'test_empty.json'
#         # Test
#         actual_blob = file_server.download_blob(filename, self._blob_id)
#         self.assertIsNone(actual_blob)
#
#     def test_save_blob(self):
#         # Setup
#         filename = 'test_empty.json'
#         # Test
#         actual_status = file_server.save_blob(filename, self._blob)
#         self.assertIsInstance(actual_status, binary_data_pb2.ErrorStatus)
#         self.assertFalse(actual_status.wasError)
#         actual_blob = file_server.download_blob(filename, self._blob_id)
#         self.assertIsInstance(actual_blob, binary_data_pb2.Blob)
#         # Blob id and payload determine equality
#         self.assertEqual(actual_blob.id, self._blob.id)
#         self.assertEqual(actual_blob.payload, self._blob.payload)
#         wipe_json_file(filename)
#
#     def test_delete_blob(self):
#         # Setup
#         filename = 'test_empty.json'
#         file_server.save_blob(filename, self._blob)
#         # Test
#         actual_status = file_server.delete_blob(filename, self._blob_id)
#         self.assertIsInstance(actual_status, binary_data_pb2.ErrorStatus)
#         self.assertFalse(actual_status.wasError)
#         # Now check we cannot download the blob
#         actual_blob = file_server.download_blob(filename, self._blob_id)
#         self.assertIsNone(actual_blob)
#
#     def test_save_blob_error(self):
#         # Setup
#         filename = 'invalid_filename'
#         # Test
#         actual_status = file_server.save_blob(filename, self._blob)
#         self.assertIsInstance(actual_status, binary_data_pb2.ErrorStatus)
#         self.assertTrue(actual_status.wasError)
#
#     def test_delete_blob_error(self):
#         # Setup
#         filename = 'invalid_filename'
#         # Test
#         actual_status = file_server.delete_blob(filename, self._blob_id)
#         self.assertIsInstance(actual_status, binary_data_pb2.ErrorStatus)
#         self.assertTrue(actual_status.wasError)
#
#     def test_download_blob_error(self):
#         # Setup
#         filename = 'invalid_filename'
#         # Test
#         actual_blob = file_server.download_blob(filename, self._blob_id)
#         self.assertIsNone(actual_blob)

class TestServerMethods(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.blob_spec = binary_data_pb2.BlobSpec(size=1, chunk_count=1)
        self.context = None
        self.server = FileServerServicer()

    def test_ValidateFileServer_payload(self):
        response = self.server.ValidateFileServer(self.blob_spec, self.context)
        expiration_time = binary_data_pb2.ExpirationTime()
        expiration_time = response.payload.Unpack(expiration_time)
        self.assertEqual(expiration_time, file_server.get_expiration_time())

    def test_ValidateFileServer_error(self):
        response = self.server.ValidateFileServer(self.blob_spec, self.context)
        self.assertEqual(response.error, file_server.get_error())

if __name__ == '__main__':
    unittest.main()
