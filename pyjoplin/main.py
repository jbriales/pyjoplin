#!/usr/bin/env python2
# coding=utf-8
"""
Interface Joplin via python
"""

import argcomplete, argparse
import six
import sys
from termcolor import colored
import traceback

from pyjoplin.commands import *


def print_green(text):
    print(colored(text, 'green'))
    

def print_red(text):
    print(colored(text, 'red'))


def test():
    """
    Test main pyjoplin functionalities: new, search
    :return:
    """

    try:
        subprocess.check_output('type -t joplin', shell=True)
    except subprocess.CalledProcessError as err:
        print("ERROR: joplin CLI does not exist")
        print("Sol: Install")
        return False

    # Create new test note
    print("Creating new test note...")
    test_title = 'temp-test-for-pyjoplin'
    test_query = 'asdfghjkl'
    test_body = u"""
    This is a %s word
    
    This is a unicode string: \u2192
    
    # Solution: (working or not)
    blablabla
    ```python
    code
    stub
    ```
    """ % test_query
    new(test_title, 'search')
    print_green("... succeeded!")

    # Create content for test note
    print("Saving content for test note...")
    new_note = Note.get(Note.title == test_title)
    new_note.body = test_body
    num_saved = new_note.save()
    assert num_saved == 1
    print_green("... succeeded!")

    # Try writing note to tempfile (with unicode content!)
    print("Saving note content to temp text file...")
    from utils import generate_tempfile_name
    path_tempfile = generate_tempfile_name('edit_', '.md')
    try:
        new_note.to_file(path_tempfile)
        print_green("... succeeded!")
    except:
        print_red("Failed! See traceback for details:")
        print(traceback.format_exc())

    # Try reading back from file to note
    print("Writing temp text file to note content...")
    try:
        new_note.from_file(path_tempfile)
        print_green("... succeeded!")
    except:
        print_red("Failed! See traceback for details:")
        print(traceback.format_exc())

    # Check imfeelinglucky works
    print("Check imfeelinglucky functionality...")
    stub = imfeelinglucky(new_note.id)
    assert stub == u'    code\n    stub\n    '
    print_green("... succeeded!")

    # TODO: Check also with inline stub

    # Check clipboard was correctly populated
    import pyperclip
    print("Check clipboard content...")
    clipboard_content = pyperclip.paste()
    assert clipboard_content == stub
    print_green("... succeeded!")

    # Delete note
    # NOTE: Index should be updated upon .delete()
    delete(new_note.id)

    # Check entry was removed from fulltext search works
    # NOTE: Index should be updated upon .delete_instance()
    print("Check test note removed from FTS index after deletion...")
    found_index_notes = search(test_query)
    assert len(found_index_notes) == 0
    print_green("... succeeded!")

    print("Complete test succeeded!")



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

find_title.parser = subparsers.add_parser(
    'find-title', description=find_title.__doc__)
find_title.parser.set_defaults(func=find_title)
find_title.parser.add_argument(
    'title',
    help="Note title to search"
)

imfeelinglucky.parser = subparsers.add_parser(
    'imfeelinglucky', description=imfeelinglucky.__doc__)
imfeelinglucky.parser.set_defaults(func=imfeelinglucky)
imfeelinglucky.parser.add_argument(
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

find_empty_notes.parser = subparsers.add_parser(
    'find_empty', description=find_empty_notes.__doc__
)
find_empty_notes.parser.set_defaults(func=find_empty_notes)
find_empty_notes.parser.add_argument(
    "--delete",
    help="Delete found empty notes",
    action='store_true'
)


argcomplete.autocomplete(parser)

    
def main():
    if len(sys.argv) <= 1:
        parser.print_help()
        return True

    # NOTE: Can this be simplified? Check doc
    args = parser.parse_args()
    kwargs = vars(args)
    func = kwargs.pop('func')

    successful = func(**kwargs)
    sys.exit(0 if successful else 1)


if __name__ == '__main__':
    main()
