# coding=utf-8

import inspect
import os
import subprocess

from peewee import Entity, fn
from pkg_resources import resource_filename
from pyjoplin import notification
from pyjoplin.configuration import config
from pyjoplin.models import Folder, Note, NoteIndex, database as db
from pyjoplin.utils import time_joplin


PATH_SYNONYMS = resource_filename("pyjoplin", "synonyms.txt")


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
            NoteIndex.insert(
                {
                    NoteIndex.uid: note.id,
                    NoteIndex.title: note.title,
                    NoteIndex.body: note.body,
                }
            ).execute()

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
                print("%s %s" % (note.id, note.title))
                if delete:
                    note.delete_instance()
                    print("Deleted")


def rename_conflicting_notes():
    notes = Note.select().where(Note.is_conflict == 1)
    with db.atomic():
        for note in notes:
            if not note.title.endswith("(CONFLICT)"):
                note.title = note.title + " (CONFLICT)"
                num_saved_notes = note.save()
                if num_saved_notes != 1:
                    notification.show_error("Renaming conflicting note", note.title)


def list_conflicts():
    """
    List conflicting notes

    :return:
    """

    notes = Note.select().where(Note.is_conflict == 1)
    print("List of conflicting notes:")
    with db.atomic():
        for note in notes:
            print("-----------------------------")
            print("%s %s" % (note.id, note.title))


def substitute_search_column_aliases(search_str):
    import re

    # Substitute 't:' (after beginning of string or space) by 'title:'
    search_str = re.sub(r"(^| )t:", r"\1title:", search_str)
    # Substitute 'b:' (after beginning of string or space) by 'body:'
    search_str = re.sub(r"(^| )b:", r"\1body:", search_str)
    return search_str


def replace_synonyms(search_str):
    # Define list of sets of synonyms
    # These synonyms help ensuring I get all relevant results
    # even if I may often switch between several close alternatives
    # This avoids having to write down certain kw just for search once and again
    with open(PATH_SYNONYMS, "r") as f:
        sets_of_synonyms = [the_line.strip()[1:-1].split(r"' '") for the_line in f]
    # NOTE: These are not sets but lists, but anyway keeping some name

    # Preprocess into dictionary for faster query
    dict_of_synonyms = {
        the_word: the_set for the_set in sets_of_synonyms for the_word in the_set
    }

    pattern: str = r"(?P<pre>^|\s)(?P<word>%s)(?=\s|$)" % "|".join(
        dict_of_synonyms.keys()
    )

    import re

    # Replace any registered synonym into OR-set for SQLite query
    # e.g. py turns into ( py OR python )
    return re.sub(
        pattern,
        lambda m: m.group("pre")
        + r"(%s)" % (r" OR ".join(dict_of_synonyms[m.group("word")])),
        search_str,
    )
    # return search_str


def search(search_str):
    search_str = substitute_search_column_aliases(search_str)

    # Replace synonyms with all their equivalents in OR search
    search_str = replace_synonyms(search_str)

    # Search query in the FTS table
    with db.atomic():
        found_index_notes = (
            NoteIndex.select(
                NoteIndex,
                fn.snippet(Entity(NoteIndex._meta.table_name)).alias("snippet"),
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
        dict_query = {note["id"]: note for note in query}
        # Grab note only if in the query
        ordered_notes = [dict_query[id] for id in ids if id in dict_query]
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
    subprocess.call(
        "rm database.sqlite", shell=True, cwd=os.path.expanduser("~/.config/joplin/")
    )
    subprocess.call(
        "ln -s ../joplin-desktop/database.sqlite",
        shell=True,
        cwd=os.path.expanduser("~/.config/joplin/"),
    )

    if config.DO_NOTIFY:
        notification.show("Setup succeeded")


def new(title, notebook_name="personal", body=""):
    """
    Create new note in notebook
    :param title:
    :param notebook_name: optional
    :param body: optional
    :return: new_note.id
    """

    # Ensure that note with the same title does not exist already in the database
    try:
        note = Note.get(Note.title == title)
        notification.show_error("Note with same name already exists", note.title)
        raise Exception(f"Note with same name already exists")
    except Note.DoesNotExist:
        # All good, it should not exist
        pass

    # Retrieve notebook id
    try:
        notebook = Folder.get(Folder.title == notebook_name)
    except Folder.DoesNotExist:
        notification.show_error("Notebook not found", notebook_name)
        raise Folder.DoesNotExist

    # Create new note instance
    # Get unique identifier following Joplin format
    # Source: https://github.com/laurent22/joplin/issues/305#issuecomment-374123414
    import uuid

    uid = str(uuid.uuid4()).replace("-", "")
    # Get current time in Joplin format (int epoch in milliseconds)
    uint_current_timestamp_msec = time_joplin()
    new_note = Note(
        body=body,
        created_time=uint_current_timestamp_msec,
        id=uid,
        parent=notebook.id,
        source="pyjoplin",
        source_application="pyjoplin",
        title=title,
        updated_time=uint_current_timestamp_msec,
        user_created_time=uint_current_timestamp_msec,
        user_updated_time=uint_current_timestamp_msec,
    )
    num_saved_notes = new_note.save(force_insert=True)
    if num_saved_notes != 1:
        notification.show_error_and_raise("Creating note", new_note.title)
    if config.DO_NOTIFY:
        notification.show("New note created in nb %s" % notebook.title, title)

    return new_note.id


def edit(uid):
    subprocess.Popen(
        "increase_hit_history_for pyjoplin %s" % inspect.currentframe().f_code.co_name,
        shell=True,
    )

    # Find note entry by uid
    note = Note.get(Note.id == uid)
    # Save previous title and body for reference
    init_title = note.title
    init_body = note.body

    # Populate temporary file from note content
    path_sentinel = os.path.join(config.PATH_TEMP, f"{uid}")
    if os.path.exists(path_sentinel):
        notification.show_error("Note is already under edit", note.title, note.id)
        raise Exception("Note is already under edit")
    else:
        # Create sentinel to block this note
        open(path_sentinel, "a").close()

    path_tempfile = os.path.join(config.PATH_TEMP, f"{note.title.replace('/', '_')}.md")

    # Create named symlink to sentinel note
    # for better readability
    # NOTE:
    #   Because of this link, the sentinel is no longer *just* a sentinel.
    #   Instead, it is a plain text file containing the actual note content.
    try:
        os.symlink(path_sentinel, path_tempfile)
    except FileExistsError:
        notification.show_error(
            "Note file with same name is already under edit", note.title, note.id
        )
        raise Exception(f"Temp file named {note.title} already exists")

    note.to_file(path_tempfile)

    # Open file with editor
    # NOTE: Stop using template, this command gets too complicated for a single string
    #       It's better to have a list of inputs to build the last complicated command
    #       Nesting bash becomes necessary to execute source for non-interactive customization
    # NOTE: Using vimx since aliases do not seem to apply in non-interactive (even if I define it inside bashrc!?)
    proc = subprocess.Popen(
        # [
        #     'xfce4-terminal',
        #     '--disable-server',
        #     '--title',
        #     'pyjoplin - {title}'.format(title=note.title),
        #     '-e',
        #     'bash -c "source ~/.bashrc && unset PYTHONPATH && vimx \'{path}\' || vi \'{path}\'"'.format(path=path_tempfile)
        # ],
        [
            "urxvt256c",
            "-title",
            "pyjoplin - {title}".format(title=note.title),
            "-e",
            "bash",
            "-c",
            # NOTE: `source ~/.bashrc` is necessary to customize interactive shell for vim
            # e.g. to disable "flow control characters"
            # NOTE: `unset PYTHONPATH` seems necessary for this to work when called through ulauncher extension
            "source ~/.bashrc && unset PYTHONPATH && vimx -u ~/Code/python/pyjoplin/vim/vimrc '{path}'".format(
                path=path_tempfile
            )
            # NOTE: Version below works when called from terminal,
            # e.g. `pyjoplin edit 170b3c8de5034f7c8023a6a39f02219c`
            # but it immediately exits when called via ulauncher
            # 'vimx',
            # '{path}'.format(path=path_tempfile)
        ],
        stdout=subprocess.PIPE,
    )
    # cmd_str = config.EDITOR_CALL_TEMPLATE.format(title=note.title, path=path_tempfile)
    # proc = subprocess.Popen(
    #     cmd_str, shell=True,
    #     # NOTE: This is needed for non-gedit editors, but DISPLAY seems to be giving issues
    #     # env=dict(
    #     #     os.environ,
    #     #     PYTHONPATH='',  # avoid issues when calling Python3 scripts from Python2
    #     #     DISPLAY=":0.0"  # ensure some GUI apps catch the right display
    #     # ),
    #     stdout=subprocess.PIPE
    # )

    # Loop during edition to save incremental changes
    import time

    last_modification_time_sec = os.path.getmtime(path_tempfile)
    try:
        # Sync note under edition with database note in a loop
        while proc.poll() is None:
            time.sleep(0.5)
            if os.path.getmtime(path_tempfile) > last_modification_time_sec:
                last_modification_time_sec = os.path.getmtime(path_tempfile)

                note.from_file(path_tempfile)
                num_saved_notes = note.save()
                if num_saved_notes != 1:
                    notification.show_error(
                        "Saving note changes during edition", note.title
                    )
                # else:
                #     notification.show("Note saved", note.title)
    except:
        notification.show_error("During note edition sync loop", note.title)
        raise Exception("ERROR during editor-database sync loop")

    returncode = proc.wait()
    if returncode != 0:
        print("ERROR during edition")
        print("Output:")
        output = proc.stdout.read().decode("utf-8")
        print(output)
        notification.show_error(
            "returncode from editor was not 0. Inspect note to sanity-check.",
            note.title,
            output,
        )
        raise Exception("ERROR during edition")

    # Save edited file content to Notes table
    note.from_file(path_tempfile)

    # Cleanup temp files
    # NOTE:
    # If the editor finished with some error code
    # and things didn't go well,
    # we do NOT remove the sentinel.
    # So we will get an error when trying to open the note again, showcasing the issue
    # (even though you should have got an error notification, but just in case!)
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


def print_for_uid(uid):
    """
    Print note content
    :param uid:
    :return: returncode
    """
    try:
        note = Note.get(Note.id == uid)
        print(note.to_string(), end="")
        return 0
    except Note.DoesNotExist:
        print(f"No note found with id {uid}")
        return 2


# Basic function to abstract peewee
# Gets UID from given title by exact match, if any
def find_title(title):
    try:
        note = Note.get(Note.title == title)
        return note.id
    except Note.DoesNotExist:
        return None


# Util for CLI
def print_for_title(title):
    if isinstance(title, list):
        # For case coming from CLI
        title = " ".join(title)

    uid = find_title(title)
    if uid:
        print_for_uid(uid)
        return 0
    else:
        print("No exact match found for title query " + title)
        return 2


def edit_by_title(title):
    if isinstance(title, list):
        # For case coming from CLI
        title = " ".join(title)
    try:
        note = Note.get(Note.title == title.rstrip())
        edit(note.id)
    except Note.DoesNotExist:
        print("No exact match found for title query " + title)


def find_notebook(name):
    try:
        notebook = Folder.get(Folder.title == name)
        print(notebook.id)
        print(notebook.title)
    except Note.DoesNotExist:
        print("No exact match found for query")


def imfeelinglucky(uid):
    """
    Try to make most straightforward action on note,
    similar in spirit to "I'm feeling lucky" feature in Google search.
    :param uid:
    :return:
    """
    subprocess.Popen(
        "increase_hit_history_for pyjoplin %s" % inspect.currentframe().f_code.co_name,
        shell=True,
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
    stub = stub.strip("\n")

    # Copy stub into the clipboard
    # NOTE: Using xclip because pyperclip does not work
    # Create temporary file with text
    path_tempfile = os.path.join(config.PATH_TEMP, "stub")
    with open(path_tempfile, "w") as f:
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


def new_and_edit(title, notebook="search"):
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
    search_str = " ".join(search_terms)
    found_index_notes = search(search_str)
    # NOTE: This should be enough to show found entries in jlauncher
    print("FTS: %d notes found" % found_index_notes.count())
    for idx_note in found_index_notes:
        # print("Note: {title}\n{body}\n".format(**idx_note))
        print("Note: {title}\n{snippet}\n".format(**idx_note))

    # NoteIndex.lucene()
    print("Testing via peewee")
