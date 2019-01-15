#!/usr/bin/env python2
# coding=utf-8
"""
Run unittest discover to execute all tests in the package hierarchy
"""
import unittest
import subprocess

if __name__ == '__main__':
    test_loader = unittest.defaultTestLoader.discover('.')
    test_runner = unittest.TextTestRunner()
    test_runner.run(test_loader)

    # NOTE: Legacy, to be refactored into unit tests
    # Just call main test from here
    # subprocess.call("pyjoplin test", shell=True)



