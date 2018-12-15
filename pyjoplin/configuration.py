# coding=utf-8
"""
Define global configuration variables
- Paths
"""
import os
from pkg_resources import resource_filename


class Config:
    # Folders
    PATH_CONFIG = os.path.expanduser("~/.config/pyjoplin/")
    PATH_TEMP = "/tmp/pyjoplin/"
    # Files
    PATH_ICON = resource_filename('pyjoplin', 'images/pyjoplin-64.png')

    EDITOR_CALL_TEMPLATE = r'gedit -s "%s" +'  # substitute file path as EDITOR_TEMPLATE % filepath
    # EDITOR_CALL_TEMPLATE = 'remarkable %s'  # substitute file path as EDITOR_TEMPLATE % filepath
    # EDITOR_CALL_TEMPLATE = '/home/jesus/.local/bin/retext %s'  # substitute file path as EDITOR_TEMPLATE % filepath

    # Use desktop notifications for pyjoplin actions
    DO_NOTIFY = True

    # TODO: Use path to load/save config in file
    # Example: https://github.com/adamchainz/lifelogger/blob/master/lifelogger/config.py
    def __init__(self):
        # self._path = path
        # self._loaded = False
        # self._data = {}

        # Ensure config path folders exist
        for folder in [self.PATH_CONFIG, self.PATH_TEMP]:
            if not os.path.exists(folder):
                try:
                    os.makedirs(folder)
                except OSError as exc:  # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise


# Create global config variable
config = Config()
