# coding=utf-8
"""
Define global configuration variables
- Paths
"""
import os

CONFIG_PATH = os.path.expanduser("~/.config/pyjoplin/")
TEMP_PATH = "/tmp/pyjoplin/"

# Ensure folders above exist
for folder in [CONFIG_PATH, TEMP_PATH]:
    if not os.path.exists(folder):
        try:
            os.makedirs(folder)
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
