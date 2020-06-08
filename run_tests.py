#!/usr/bin/env python3
# coding=utf-8
"""
Run unittest discover to execute all tests in the package hierarchy
"""
import unittest
import subprocess

if __name__ == "__main__":
    test_loader = unittest.defaultTestLoader.discover(".")
    test_runner = unittest.TextTestRunner()
    test_runner.run(test_loader)
