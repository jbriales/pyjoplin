#!/usr/bin/env python2
# coding=utf-8
"""
Interface Joplin via python
"""

import argparse
import six
import sys

from pyjoplin.models import Note, NoteIndex, database as db
from peewee import fn, Entity


parser = argparse.ArgumentParser(
    description=__doc__,
    epilog="By Jesus Briales"
)
subparsers = parser.add_subparsers()


def search(search_str):
    # Search query in the FTS table
    with db.atomic():
        found_index_notes = (
            NoteIndex
            .select(
                NoteIndex,
                fn.snippet(Entity(NoteIndex._meta.table_name)).alias('snippet')
            )
            .where(NoteIndex.match(search_str))
            .order_by(NoteIndex.bm25())
            .dicts()
        )
    return found_index_notes


def toy(search_terms):

    # Create virtual FTS table from scratch
    try:
        # Remove table in case it existed
        NoteIndex.drop_table()
    except Exception:
        pass
    NoteIndex.create_table()
    print("Created virtual NoteIndex FTS table")

    # Add all entries into virtual FTS table
    notes = Note.select()
    with db.atomic():
        for note in notes:
            print("Note:\n{title}\n{body}\n".format(**note.__data__))
            NoteIndex.insert({
                NoteIndex.uid: note.id,
                NoteIndex.title: note.title,
                NoteIndex.body: note.body
            }).execute()

    NoteIndex.rebuild()

    # Search query in the FTS table
    # search_str = 'editor note'
    # search_str = 'sqlite python'
    search_str = ' '.join(search_terms)
    found_index_notes = search(search_str)
    # NOTE: This should be enough to show found entries in jlauncher
    print("FTS: %d notes found" % found_index_notes.count())
    for idx_note in found_index_notes:
        # print("Note: {title}\n{body}\n".format(**idx_note))
        print("Note: {title}\n{snippet}\n".format(**idx_note))

    # NoteIndex.lucene()
    print("Testing via peewee")
    
    
toy.parser = subparsers.add_parser(
    'toy', description='Toy test')
toy.parser.add_argument(
    'search_terms',
    type=six.text_type,
    nargs='*',
    help="The query for the search."
)
toy.parser.set_defaults(func=toy)


def main():
    if len(sys.argv) <= 1:
        parser.print_help()
        return True

    # NOTE: Can this be simplified? Check doc
    args = parser.parse_args()
    kwargs = vars(args)
    func = kwargs.pop('func')

    successful = func(**kwargs)

    # # Parse arguments
    # args = parser.parse_args()
    # # Call function on user arguments
    # # NOTE: This works with functions with both positional and keyword arguments
    # # thanks to syntactic sugar of Python function calls (positional arguments can become keyword arguments by name
    # a_fun(**vars(args))

    sys.exit(0 if successful else 1)


if __name__ == '__main__':
    main()
