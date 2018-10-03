# coding=utf-8
"""
Define global configuration variables
- Paths
"""
import os


class Config:
    PATH_CONFIG = os.path.expanduser("~/.config/pyjoplin/")
    PATH_TEMP = "/tmp/pyjoplin/"

    # TODO: Use path to load/save config in file
    # Example: https://github.com/adamchainz/lifelogger/blob/master/lifelogger/config.py
    def __init__(self):
        # self._path = path
        # self._loaded = False
        # self._data = {}

        # Ensure config path folders exist
        for folder in [self.CONFIG_PATH, self.TEMP_PATH]:
            if not os.path.exists(folder):
                try:
                    os.makedirs(folder)
                except OSError as exc:  # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise


# Create global config variable
config = Config()
