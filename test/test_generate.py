import unittest
import os
import logging
import tempfile
import shutil

import generate


class TestGenerate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        log = logging.getLogger(generate.__name__)
        log.addHandler(logging.NullHandler())

    def setUp(self):
        self.__tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.__tempdir)

    def test_generate(self):
        generate.generate_site("source/", self.__tempdir)

        with open("expected_output/index.html", "r") as f1, \
             open(os.path.join(self.__tempdir, "index.html"), "r") as f2:
            self.assertEqual(f1.read(), f2.read())

    def test_generate_no_layout(self):
        f = tempfile.NamedTemporaryFile(dir=self.__tempdir, suffix=".rst",
                delete=False)
        f.write("{}\n---\n".encode())
        f.close()

        generate.generate_site(self.__tempdir, self.__tempdir)

        self.assertFalse(os.path.isfile(f.name + ".html"))

    def test_generate_missing_template(self):
        f = tempfile.NamedTemporaryFile(dir=self.__tempdir, suffix=".rst",
                delete=False)
        f.write('{"layout": "missing"}\n---\n'.encode())
        f.close()

        generate.generate_site(self.__tempdir, self.__tempdir)

        self.assertFalse(os.path.isfile(f.name + ".html"))

    def test_generate_invalid_template(self):
        f = tempfile.NamedTemporaryFile(dir=self.__tempdir, suffix=".rst",
                delete=False)
        p = os.path.join(self.__tempdir, "layout")
        os.mkdir(p)
        t = tempfile.NamedTemporaryFile(dir=p, suffix=".html", delete=False)
        f.write(('{"layout": "%s"}\n---\n' % os.path.basename(t.name)).encode())
        f.close()
        t.write("{ broken }}}}}".encode())
        t.close()

        generate.generate_site(self.__tempdir, self.__tempdir)

        self.assertFalse(os.path.isfile(f.name + ".html"))


if __name__ == "__main__":
    unittest.main()

