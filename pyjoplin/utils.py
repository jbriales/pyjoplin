# coding=utf-8
"""
Various miscellanea utils kept here for clarity
"""
from datetime import datetime
import os

from pyjoplin.config import config


def generate_tempfile_name(prefix, suffix):
    now = datetime.now().isoformat()
    # message_filename = os.path.join(MSG_PATH, 'ENTRY_MSG_'+start_str)
    # TODO: Turn this into an option instead
    return os.path.join(config.PATH_TEMP, prefix + now + suffix)
