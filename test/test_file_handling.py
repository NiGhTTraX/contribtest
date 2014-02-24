import unittest
import logging
import tempfile
import shutil

import generate


class TestFileHandling(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        log = logging.getLogger(generate.__name__)
        log.addHandler(logging.NullHandler())

    def setUp(self):
        self.__tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.__tempdir)

    def test_list_files_empty_dir(self):
        self.assertListEqual(list(generate.list_files(self.__tempdir)), [])

    def test_list_files_one_file(self):
        with tempfile.NamedTemporaryFile(dir=self.__tempdir, suffix=".rst") as f:
            self.assertListEqual(list(generate.list_files(self.__tempdir)), [f.name])

    def test_list_files_lots_of_files(self):
        TEST_RANGE = 10
        files = [tempfile.NamedTemporaryFile(dir=self.__tempdir, suffix=".rst") for i in range(TEST_RANGE)]

        self.assertListEqual(sorted(generate.list_files(self.__tempdir)),
                sorted([f.name for f in files]))

        for f in files:
            f.close()

    def test_read_file(self):
        f = tempfile.NamedTemporaryFile(delete=False)
        f.write("{}\n---\nana are mere".encode())
        f.close()

        metadata, content = generate.read_file(f.name)
        self.assertDictEqual(metadata, {})
        self.assertEqual(content, "ana are mere")

    def test_read_file_multiple_separators(self):
        f = tempfile.NamedTemporaryFile(delete=False)
        f.write("{}\n---\nana are mere\n---\nsi pere".encode())
        f.close()

        metadata, content = generate.read_file(f.name)
        self.assertDictEqual(metadata, {})
        self.assertEqual(content, "ana are mere\n---\nsi pere")

    def test_read_file_valid_metadata(self):
        f = tempfile.NamedTemporaryFile(delete=False)
        f.write('{"test": "cucu"}\n---\n'.encode())
        f.close()

        metadata, _ = generate.read_file(f.name)
        self.assertDictEqual(metadata, {"test": "cucu"})

    def test_read_file_invalid_metadata(self):
        f = tempfile.NamedTemporaryFile(delete=False)
        f.write('{"cucu"}\n---\n'.encode())
        f.close()

        with self.assertRaises(ValueError):
            metadata, _ = generate.read_file(f.name)

    def test_write_output_ends_with_one_newline(self):
        f = tempfile.NamedTemporaryFile(delete=False)
        f.close()

        generate.write_output(f.name, "blah")
        with open(f.name, "r") as ff:
            self.assertEqual(ff.read(), "blah\n")

    def test_write_output_max_2_consecutive_newlines(self):
        f = tempfile.NamedTemporaryFile(delete=False)
        f.close()

        generate.write_output(f.name, "blah\n\n\n\n\n\n\nblah")
        with open(f.name, "r") as ff:
            self.assertEqual(ff.read(), "blah\n\nblah\n")

    def test_write_output_no_trailing_white_space(self):
        f = tempfile.NamedTemporaryFile(delete=False)
        f.close()

        generate.write_output(f.name, "blah\n\n\n\n\n\n\n")
        with open(f.name, "r") as ff:
            self.assertEqual(ff.read(), "blah\n")


if __name__ == "__main__":
    unittest.main()

