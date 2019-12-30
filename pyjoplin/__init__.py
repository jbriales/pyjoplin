# coding=utf-8
"""
Python utilities to interface and enrich Joplin note app with extra functionalities
"""
__version__ = '0.1dev'
__author__ = 'jbriales'
__license__ = 'MIT'

# Import main commands to make them available at package level
from .commands import rebuild_fts_index, search, setup, new, edit, delete, new_and_edit, imfeelinglucky, get_notes_by_id
