import unittest

from src.resources_files import read_db, write_db, remove_by_key_db, wipe_json_file


def test_read_expected():
    data = {}
    for i in range(1, 4):
        data[str(i)] = "Data for blob %i" % i
    return data


class TestBasicMethods(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.payload = b"bag of bits"
        self.test_path = "tests/"
        self.default_filename = self.test_path + 'test_empty.json'

    def test_read_db(self):
        self.assertEqual(read_db(self.test_path + "test_read.json"), test_read_expected())

    def test_write_db(self):
        # Setup
        expected_data = test_read_expected()
        # Test
        write_db(self.default_filename, expected_data)
        self.assertEqual(read_db(self.default_filename), expected_data)
        actual = read_db(self.default_filename)
        wipe_json_file(self.default_filename)

    def test_remove_by_key_db(self):
        # Setup
        key = "1"
        input_data = test_read_expected()
        write_db(self.default_filename, input_data)
        expected = input_data
        del expected[key]
        # Test
        remove_by_key_db(self.default_filename, key)
        actual = read_db(self.default_filename)
        self.assertEqual(actual, expected)
        wipe_json_file(self.default_filename)

    def test_remove_by_key_db_non_existant_key(self):
        self.assertRaises(KeyError, remove_by_key_db, self.default_filename, "invalid_key")
        wipe_json_file(self.default_filename)
