import unittest
import logging
import tempfile
import shutil
import os

import generate


class MockLoggingHandler(logging.Handler):
    """Mock logging handler to check for expected logs."""

    def __init__(self, *args, **kwargs):
        self.reset()
        logging.Handler.__init__(self, *args, **kwargs)

    def emit(self, record):
        self.messages[record.levelname.lower()].append(record.getMessage())

    def reset(self):
        self.messages = {
            'debug': [],
            'info': [],
            'warning': [],
            'error': [],
            'critical': [],
        }


class TestLogging(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        log = logging.getLogger(generate.__name__)
        cls.__log_handler = MockLoggingHandler(level="DEBUG")
        log.setLevel("DEBUG")
        log.addHandler(cls.__log_handler)

    def setUp(self):
        self.__tempdir = tempfile.mkdtemp()

        # Reset logging messages.
        self.__log_handler.reset()

    def tearDown(self):
        shutil.rmtree(self.__tempdir)

    def test_generate_no_layout(self):
        f = tempfile.NamedTemporaryFile(dir=self.__tempdir, suffix=".rst",
                delete=False)
        f.write("{}\n---\n".encode())
        f.close()

        generate.generate_site(self.__tempdir, self.__tempdir)

        self.assertListEqual(self.__log_handler.messages["error"],
                ["Template doesn't contain layout",
                 "Parsing %s" % f.name])

    def test_generate_missing_template(self):
        f = tempfile.NamedTemporaryFile(dir=self.__tempdir, suffix=".rst",
                delete=False)
        f.write('{"layout": "missing"}\n---\n'.encode())
        f.close()

        generate.generate_site(self.__tempdir, self.__tempdir)

        self.assertListEqual(self.__log_handler.messages["error"],
                ["Template not found",
                 "Parsing missing"])


    def test_generate_invalid_template(self):
        f = tempfile.NamedTemporaryFile(dir=self.__tempdir, suffix=".rst",
                delete=False)

        p = os.path.join(self.__tempdir, "layout")
        os.mkdir(p)

        t = tempfile.NamedTemporaryFile(dir=p, suffix=".html", delete=False)

        f.write(('{"layout": "%s"}\n---\n' % os.path.basename(t.name)).encode())
        f.close()

        t.write("{% broken }}}}}".encode())
        t.close()

        generate.generate_site(self.__tempdir, self.__tempdir)

        self.assertListEqual(self.__log_handler.messages["error"],
                ["There was an error in parsing template %s" %
                    os.path.basename(t.name)])

    def test_generate(self):
        f = tempfile.NamedTemporaryFile(dir=self.__tempdir, suffix=".rst",
                delete=False)

        p = os.path.join(self.__tempdir, "layout")
        os.mkdir(p)

        t = tempfile.NamedTemporaryFile(dir=p, suffix=".html", delete=False)

        f.write(('{"layout": "%s"}\n---\n' % os.path.basename(t.name)).encode())
        f.close()

        t.write("stuff".encode())
        t.close()

        generate.generate_site(self.__tempdir, self.__tempdir)

        self.assertListEqual(self.__log_handler.messages["error"], [])
        expected_name = os.path.splitext(os.path.basename(f.name))[0] + ".html"
        self.assertListEqual(self.__log_handler.messages["info"],
                ["Generating site from %s" % self.__tempdir,
                 "Writing %s with template %s" % (expected_name,
                         os.path.basename(t.name))])

if __name__ == "__main__":
    unittest.main()

