#!/usr/bin/env python2
# coding=utf-8
"""
Interface Joplin via python
"""

from pyjoplin.models import Note, database as db

if __name__ == "__main__":
    query = Note.select()

    with db.atomic():
        for note in query:
            print("Note:\n{title}\n{body}\n".format(**note.__data__))

    print("Testing via peewee")

