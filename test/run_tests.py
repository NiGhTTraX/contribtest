#!/usr/bin/env python
import argparse
import sys
import unittest
import os


script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.realpath(os.path.join(script_dir, "..")))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run contribtest tests")
    parser.add_argument("suite", nargs="?", type=str,
                        help="System or module path for test suite to run, defaults to all tests",
                        default=script_dir)
    args = parser.parse_args()

    # Get all the tests from the suite.
    tests = unittest.TestLoader().discover(args.suite, "test_*.py")

    # Run them.
    unittest.TextTestRunner().run(tests)

