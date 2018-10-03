# coding=utf-8

import os
import subprocess

from peewee import fn, Entity

from pyjoplin.models import Note, NoteIndex, database as db
from pyjoplin.configuration import config
from pyjoplin import notification


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

    if config.DO_NOTIFY:
        notification.show("Rebuilt index", message="FTS index populated from scratch")


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

    if config.DO_NOTIFY:
        notification.show("Setup succeeded")


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

    if config.DO_NOTIFY:
        notification.show("New note created", title)

    return new_note.id


def edit(uid):
    from pyjoplin.utils import generate_tempfile_name

    # Find note entry by uid
    note = Note.get(Note.id == uid)
    backup_title = note.title

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
        if config.DO_NOTIFY:
            notification.show("Finished edition with no changes", note.title)
        return

    # Delete entry if empty
    if (not note.title) and (not note.body):
        note.delete_instance()
        if config.DO_NOTIFY:
            notification.show("Deleted note", backup_title)
        return

    # Save note changes into database
    # NOTE: FTS entry is automatically updated within .save()
    num_saved_notes = note.save()
    if num_saved_notes != 1:
        notification.show_error_and_raise("Saving note changes", note.title)

    if config.DO_NOTIFY:
        notification.show("Note saved", note.title)


def imfeelinglucky(uid):
    """
    Try to make most straightforward action on note,
    similar in spirit to "I'm feeling lucky" feature in Google search.
    :param uid:
    :return:
    """
    # NOTE: For now only implements searching first code stub in Solution:
    # In other cases it could open url for "link-type" notes

    # Find note entry by uid
    note = Note.get(Note.id == uid)

    # Parse first code stub (if any)
    import re
    # Typical example:
    # # Solution:
    # ... (one or several lines)
    # ```<lang>
    # <code_stub>
    # ```
    pattern_str = r"#?\s*Solution.*?```.*?\n(.*)```"
    try:
        stub = re.search(pattern_str, note.body, re.DOTALL).group(1)
    except AttributeError:
        notification.show("No code stub found", note.title)
        return None

    # Copy stub into the clipboard
    import pyperclip
    pyperclip.copy(stub)

    notification.show("Extracted code stub:", note.title, stub)
    return stub


def delete(uid):
    # Find note entry by uid
    note = Note.get(Note.id == uid)
    note.delete_instance()
    if config.DO_NOTIFY:
        notification.show("Deleted note", note.title)


def new_and_edit(title, notebook='search'):
    # Create new entry via Joplin CLI
    new_uid = new(title, notebook)
    # Edit note
    edit(new_uid)
    return new_uid


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