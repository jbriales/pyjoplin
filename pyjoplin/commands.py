# coding=utf-8

import inspect
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


def find_empty_notes(delete=False):
    """
    Find and report empty notes
    Useful e.g. to find if some note was left empty due to synchronization issues

    :return:
    """

    notes = Note.select().order_by(Note.title)
    print("Listing empty notes:")
    with db.atomic():
        for note in notes:
            if not note.body:
                print('%s %s' % (note.id, note.title))
                if delete:
                    note.delete_instance()
                    print('Deleted')


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


def get_notes_by_id(ids, ordered=False):
    # Find notes with id in uids
    # Peewee: `x << y` stands for `x in y`
    # NOTE: Order in query is unrelated to order in uids
    query = Note.select().where(Note.id << ids).dicts()
    # Debug: [note['id'] for note in query]

    if ordered:
        # Order query list in same order as uids
        dict_query = {note['id']: note for note in query}
        # Grab note only if in the query
        ordered_notes = [dict_query[id]
                         for id in ids
                         if id in dict_query]
        query = ordered_notes
        # Debug: [note['id'] for note in query]

    return query


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
        notification.show_error("Creating new note via Joplin CLI", title)
        raise Note.DoesNotExist

    if config.DO_NOTIFY:
        notification.show("New note created in %s" % notebook, title)

    return new_note.id


def edit(uid):
    subprocess.Popen(
        'increase_hit_history_for pyjoplin %s' % inspect.currentframe().f_code.co_name,
        shell=True
    )

    # Find note entry by uid
    note = Note.get(Note.id == uid)
    # Save previous title and body for reference
    init_title = note.title
    init_body = note.body

    # Populate temporary file from note content
    path_sentinel = os.path.join(config.PATH_TEMP, '%s' % uid)
    if os.path.exists(path_sentinel):
        notification.show_error("Note is already under edit", note.title)
        return False
    else:
        # Create sentinel to block this note
        open(path_sentinel, 'a').close()

    path_tempfile = os.path.join(config.PATH_TEMP, '%s.md' % note.title.replace('/', '_'))

    note.to_file(path_tempfile)

    # Open file with editor
    cmd_str = config.EDITOR_CALL_TEMPLATE % path_tempfile
    proc = subprocess.Popen(
        cmd_str, shell=True,
        # NOTE: This is needed for non-gedit editors, but DISPLAY seems to be giving issues
        # env=dict(
        #     os.environ,
        #     PYTHONPATH='',  # avoid issues when calling Python3 scripts from Python2
        #     DISPLAY=":0.0"  # ensure some GUI apps catch the right display
        # ),
        stdout=subprocess.PIPE
    )

    # Loop during edition to save incremental changes
    import time
    last_modification_time = os.path.getmtime(path_tempfile)
    while proc.poll() is None:
        time.sleep(0.5)
        if os.path.getmtime(path_tempfile) > last_modification_time:
            last_modification_time = os.path.getmtime(path_tempfile)

            note.from_file(path_tempfile)
            num_saved_notes = note.save()
            if num_saved_notes != 1:
                notification.show_error("Saving note changes during edition", note.title)
            # else:
            #     notification.show("Note saved", note.title)

    returncode = proc.wait()
    if returncode != 0:
        print("ERROR during edition")
        print("Output:")
        output = proc.stdout.read().decode('utf-8')
        print(output)
        raise Exception

    # Save edited file content to Notes table
    note.from_file(path_tempfile)
    os.remove(path_tempfile)
    os.remove(path_sentinel)

    # Check for note changes
    if note.title == init_title and note.body == init_body:
        # Changed nothing, no need to save
        if config.DO_NOTIFY:
            notification.show("Finished edition with no changes", note.title)
        return

    # Delete entry if empty
    if (not note.title) and (not note.body):
        note.delete_instance()
        if config.DO_NOTIFY:
            notification.show("Deleted note", init_title)
        return

    # Save note changes into database
    # NOTE: FTS entry is automatically updated within .save()
    num_saved_notes = note.save()
    if num_saved_notes != 1:
        notification.show_error_and_raise("Saving note changes", note.title)

    if config.DO_NOTIFY:
        notification.show("Note saved", note.title)


def find_title(title):
    try:
        note = Note.get(Note.title == title)
        print(note.id)
        print(note.title)
        print(note.body)
    except:
        print("No exact match found for query")


def imfeelinglucky(uid):
    """
    Try to make most straightforward action on note,
    similar in spirit to "I'm feeling lucky" feature in Google search.
    :param uid:
    :return:
    """
    subprocess.Popen(
        'increase_hit_history_for pyjoplin %s' % inspect.currentframe().f_code.co_name,
        shell=True
    )

    # NOTE: For now only implements searching first code stub in Solution:
    # In other cases it could open url for "link-type" notes

    # Find note entry by uid
    note = Note.get(Note.id == uid)

    # Parse first code stub (if any)
    import re
    stub = ""
    if not stub:
        # Typical example:
        # # Solution...
        # ... (one or several lines)
        # ```<lang>
        # <code_stub>
        # ```
        pattern_str = r"#?\s*Solution.*?```.*?\n(.*?)```"
        m = re.search(pattern_str, note.body, re.DOTALL)
        if m:
            stub = m.group(1)
    if not stub:
        # Inline solution:
        # # Solution...
        # ... (one or several lines)
        # `<code_stub>`
        pattern_str = r"#?\s*Solution.*?`(.*?)`"
        m = re.search(pattern_str, note.body, re.DOTALL)
        if m:
            stub = m.group(1)
    if not stub:
        notification.show("No code stub found, opening file", note.title)
        edit(uid)
        return None
    # Strip newlines to avoid unexpected execution e.g. in shell
    stub = stub.strip('\n')

    # Copy stub into the clipboard
    # NOTE: Using xclip because pyperclip does not work
    # Create temporary file with text
    path_tempfile = os.path.join(config.PATH_TEMP, 'stub')
    with open(path_tempfile, 'w') as f:
        f.write(stub)
    cmd = "xclip -selection clipboard %s" % path_tempfile
    subprocess.call(cmd, shell=True)

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