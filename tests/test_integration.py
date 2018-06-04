from PIL import Image
from src import binary_data_pb2
import unittest
import os


class TestIntergration(unittest.TestCase):
    def test_manipulating_cat_image(self):
        image_filename = 'tests/cat.png'

        # File size in bits
        blob_size = os.stat(image_filename).st_size * 8

        chunk_count = 10000
        blob_spec = binary_data_pb2.BlobSpec(size=blob_size, chunk_count=chunk_count)

        
        assert(False)

    def test_manipulating_puppy_image(self):
        # puppyIm = Image.open('puppy.png')
        return
