#!/usr/bin/env python2
# coding=utf-8
"""
Interface Joplin via python
"""

import argparse
import os
import six
import subprocess
import sys

from pyjoplin.models import Note, NoteIndex, database as db
from peewee import fn, Entity


def rebuild_fts_index():
    """
    Rebuild virtual table for FTS (fulltext search)
    populating with all existing notes

    :return:
    """
    # Create empty FTS table from scratch
    try:
        # Remove table in case it existed
        NoteIndex.drop_table()
    except Exception:
        pass
    NoteIndex.create_table()

    # Add all entries into virtual FTS table
    notes = Note.select()
    with db.atomic():
        for note in notes:
            NoteIndex.insert({
                NoteIndex.uid: note.id,
                NoteIndex.title: note.title,
                NoteIndex.body: note.body
            }).execute()


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


def setup():
    """
    Do setup required by pyjoplin for interfacing with desktop and terminal app
    NOTE: db is shared by terminal and desktop apps
    :return:
    """
    # Substitute CLI database by symbolic link to desktop database.sqlite
    subprocess.call("rm database.sqlite", shell=True,
                    cwd=os.path.expanduser('~/.config/joplin/'))
    subprocess.call("ln -s ../joplin-desktop/database.sqlite", shell=True,
                    cwd=os.path.expanduser('~/.config/joplin/'))


def new(title, notebook='search'):
    """
    Create new note in notebook
    :param title:
    :param notebook:
    :return:
    """
    # Set destination notebook as active in Joplin CLI
    # joplin use <notebook>
    subprocess.call("joplin use %s" % notebook, shell=True)

    # Create new note in Joplin CLI
    subprocess.call("joplin mknote \'%s\'" % title, shell=True)

    # Retrieve new note id
    try:
        new_note = Note.get(Note.title == title)
    except Note.DoesNotExist:
        print("ERROR: Note creation via joplin CLI failed")
        raise Note.DoesNotExist

    return new_note.id


def edit(uid):
    from pyjoplin.utils import generate_tempfile_name

    # Find note entry by uid
    note = Note.get(Note.id == uid)

    # Populate temporary file from note content
    path_tempfile = generate_tempfile_name('edit_', '.md')
    note.to_file(path_tempfile)

    # Open file with editor
    cmd_str = 'gedit -s %s +' % path_tempfile
    call_return = subprocess.call(cmd_str, shell=True)
    assert call_return is 0

    # Save previous title and body for reference
    previous_title = note.title
    previous_body = note.body

    # Save edited file content to Notes table
    note.from_file(path_tempfile)

    # Check for note changes
    if note.title == previous_title and note.body == previous_body:
        # Changed nothing, no need to save
        return

    # Delete entry if empty
    if (not note.title) and (not note.body):
        note.delete_instance()
        return

    # Save note changes into database
    # NOTE: FTS entry is automatically updated within .save()
    num_saved_notes = note.save()
    assert num_saved_notes == 1, "Error saving note changes"


def delete(uid):
    # Find note entry by uid
    note = Note.get(Note.id == uid)
    note.delete_instance()


def new_and_edit(title, notebook='search'):
    # Create new entry via Joplin CLI
    new_uid = new(title, notebook)
    # Edit note
    edit(new_uid)


def toy(search_terms):
    rebuild_fts_index()
    print("Created and populated virtual NoteIndex FTS table")

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


def test():
    """
    Test main pyjoplin functionalities: new, search
    :return:
    """
    # Create new test note
    test_title = 'temp-test-for-pyjoplin'
    test_query = 'asdfghjkl'
    new(test_title, 'search')

    # Create content for test note
    new_note = Note.get(Note.title == test_title)
    new_note.body = 'This is a %s word' % test_query
    num_saved = new_note.save()
    assert num_saved == 1

    # Check fulltext search works
    # NOTE: Index should be updated upon .save()
    found_index_notes = search(test_query)
    assert len(found_index_notes) == 1

    # Delete note
    # NOTE: Index should be updated upon .delete()
    delete(new_note.id)

    # Check entry was removed from fulltext search works
    # NOTE: Index should be updated upon .delete_instance()
    found_index_notes = search(test_query)
    assert len(found_index_notes) == 0

    print("Test succeeded!")

    
def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog="By Jesus Briales"
    )
    subparsers = parser.add_subparsers()

    setup.parser = subparsers.add_parser(
        'setup', description=setup.__doc__)
    setup.parser.set_defaults(func=setup)

    rebuild_fts_index.parser = subparsers.add_parser(
        'rebuild_fts_index', description=rebuild_fts_index.__doc__)
    rebuild_fts_index.parser.set_defaults(func=rebuild_fts_index)

    new.parser = subparsers.add_parser(
        'new', description=new.__doc__)
    new.parser.set_defaults(func=new)
    new.parser.add_argument(
        'title',
        help="Title string"
    )
    new.parser.add_argument(
        '--notebook',
        default='search',
        help="Destination notebook"
    )

    edit.parser = subparsers.add_parser(
        'edit', description=edit.__doc__)
    edit.parser.set_defaults(func=edit)
    edit.parser.add_argument(
        'uid',
        help="Note uid (docid)"
    )

    new_and_edit.parser = subparsers.add_parser(
        'new_and_edit', description=new_and_edit.__doc__)
    new_and_edit.parser.set_defaults(func=new_and_edit)
    new_and_edit.parser.add_argument(
        'title',
        help="Title string"
    )
    new_and_edit.parser.add_argument(
        '--notebook',
        default='search',
        help="Destination notebook"
    )

    delete.parser = subparsers.add_parser(
        'delete', description=delete.__doc__)
    delete.parser.set_defaults(func=delete)
    delete.parser.add_argument(
        'uid',
        help="Note uid (docid)"
    )

    test.parser = subparsers.add_parser(
        'test', description=test.__doc__)
    test.parser.set_defaults(func=test)

    toy.parser = subparsers.add_parser(
        'toy', description=toy.__doc__)
    toy.parser.add_argument(
        'search_terms',
        type=six.text_type,
        nargs='*',
        help="The query for the search."
    )
    toy.parser.set_defaults(func=toy)

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

    # sys.exit(0 if successful else 1)


if __name__ == '__main__':
    main()
