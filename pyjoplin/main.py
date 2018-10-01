#!/usr/bin/env python2
# coding=utf-8
"""
Interface Joplin via python
"""

from pyjoplin.models import Note, NoteIndex, database as db


def main():
    query = Note.select()

    # Create virtual FTS table from scratch
    try:
        # Remove table in case it existed
        NoteIndex.drop_table()
    except Exception:
        pass
    NoteIndex.create_table()
    print("Created virtual NoteIndex FTS table")

    # Add all entries into virtual FTS table
    with db.atomic():
        for note in query:
            print("Note:\n{title}\n{body}\n".format(**note.__data__))
            NoteIndex.insert({
                NoteIndex.uid: note.id,
                NoteIndex.title: note.title,
                NoteIndex.body: note.body
            }).execute()

    NoteIndex.rebuild()

    # Search query in the FTS table
    # search_string = 'editor note'
    search_string = 'sqlite python'
    query = (
        NoteIndex
        .select()
        .where(NoteIndex.match(search_string))
        .order_by(NoteIndex.bm25())
    )
    # NOTE: This should be enough to show found entries in jlauncher
    print("FTS: %d notes found" % query.count())
    for idx_note in query:
        print("Note: {title}\n{body}\n".format(**idx_note.__data__))

    # NoteIndex.lucene()
    print("Testing via peewee")


if __name__ == "__main__":
    main()
