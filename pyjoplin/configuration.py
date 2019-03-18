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

    # Define template for inputs PATH and TITLE (optional)
    # EDITOR_CALL_TEMPLATE = 'xfce4-terminal --disable-server --title="note - {title}" -e \'vim "{path}"\''
    # EDITOR_CALL_TEMPLATE = 'xfce4-terminal --disable-server -e \'vim "%s"\''
    # EDITOR_CALL_TEMPLATE = 'gvim "{path}"'  # substitute file path as EDITOR_TEMPLATE % filepath
    EDITOR_CALL_TEMPLATE = 'gedit -s "{path}" +'
    # EDITOR_CALL_TEMPLATE = 'remarkable {path}'
    # EDITOR_CALL_TEMPLATE = '/home/jesus/.local/bin/retext {path}'

    # Use desktop notifications for pyjoplin actions
    DO_NOTIFY = True

    DEFAULT_NOTEBOOK_NAME = 'personal'

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
