#!/usr/bin/env python2
# coding=utf-8
"""
Run unittest discover to execute all tests in the package hierarchy
"""
import subprocess

if __name__ == '__main__':
    # Just call main test from here
    subprocess.call("pyjoplin test", shell=True)
