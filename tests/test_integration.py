# import os
# import unittest
#
# from src import binary_data_pb2
#
#
# from src.device import UploadServicer
# from src import resources_server
# from src.resources_server import get_grpc_server, start_upload_server, stop_upload_server, get_file_server_stub
#
#
# class TestIntegration(unittest.TestCase):
#     @classmethod
#     def setUpClass(cls):
#         cls.server_files = get_grpc_server()
#         cls.server_device = get_grpc_server()
#         device_port = '50051'
#         file_port = '50052'
#         cls.device_database = 'tests/test_device_database.json'
#         cls.file_server_database = 'tests/test_file_server_database.json'
#         start_upload_server(cls.server_files, cls.server_device, cls.device_database, cls.file_server_database,
#                             device_port, file_port)
#         cls.upload_servicer = UploadServicer(get_file_server_stub(device_port), cls.device_database)
#
#     @classmethod
#     def tearDownClass(cls):
#         stop_upload_server(cls.server_files, cls.server_device)
#
#     def test_manipulating_cat_image(self):
#         image_filename = 'tests/cat.png'
#         # File size in bits
#         blob_size = os.stat(image_filename).st_size * 8
#         chunk_count = 10000
#         blob_spec = binary_data_pb2.BlobSpec(size=blob_size, chunk_count=chunk_count)
#         # TODO get the following line to work
#         # response = self.upload_servicer.CreateBlob(blob_spec, None)
#
#
#
#
#         assert (False)
#
#     def test_manipulating_puppy_image(self):
#         # puppyIm = Image.open('puppy.png')
#         return
