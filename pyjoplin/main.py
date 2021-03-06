#!/usr/bin/env python3
# coding=utf-8
"""
Interface Joplin via python
"""

from __future__ import print_function

import argcomplete, argparse
import six
import sys

from pyjoplin.commands import *


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


edit_by_title.parser = subparsers.add_parser(
    'edit-by-title', description=edit_by_title.__doc__)
edit_by_title.parser.set_defaults(func=edit_by_title)
edit_by_title.parser.add_argument(
    'title',
    type=six.text_type,
    nargs='+',
    help="Note's title to search (by exact match)"
)

print_for_uid.parser = subparsers.add_parser(
    'print', description=print_for_uid.__doc__)
print_for_uid.parser.set_defaults(func=print_for_uid)
print_for_uid.parser.add_argument(
    'uid',
    type=six.text_type,
    nargs=1,
    help="Note's UUID"
)

print_for_title.parser = subparsers.add_parser(
    'find-title', description=print_for_title.__doc__)
print_for_title.parser.set_defaults(func=print_for_title)
print_for_title.parser.add_argument(
    'title',
    type=six.text_type,
    nargs='+',
    help="Note's title to search (by exact match)"
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

list_conflicts.parser = subparsers.add_parser(
    'list-conflicts', description=list_conflicts.__doc__)
list_conflicts.parser.set_defaults(func=list_conflicts)

rename_conflicting_notes.parser = subparsers.add_parser(
    'mark-conflicts', description=rename_conflicting_notes.__doc__)
rename_conflicting_notes.parser.set_defaults(func=rename_conflicting_notes)


def cli_search(search_str):
    """
    Search input query into FTS tables in Joplin database
    Prints titles for matching notes

    :param string or list-of-strings:
    """
    if isinstance(search_str, list):
        # For case coming from CLI
        search_str = ' '.join(search_str)

    if not search_str:
        # Special handling of empty query: Return all titles
        # TODO: Move this to a different cli function instead, and handle switch logic from bash
        with db.atomic():
            for note in Note.select():
                print(note.title.encode('utf-8'))

    found_notes = search(search_str)
    if not found_notes:
        raise Exception('No notes found')
    else:
        for idx, note in enumerate(found_notes):
            print(note['title'])


cli_search.parser = subparsers.add_parser(
    'search', description=cli_search.__doc__)
cli_search.parser.add_argument(
    'search_str',
    type=six.text_type,
    nargs='*',
    help="The query for the FTS search."
)
cli_search.parser.set_defaults(func=cli_search)


def cli_get(ids):
    """
    Prints titles for notes' ids
    """
    for note in get_notes_by_id(ids, ordered=True):
        print(note['title'])


cli_get.parser = subparsers.add_parser(
    'get', description=cli_get.__doc__)
cli_get.parser.add_argument(
    'ids',
    type=six.text_type,
    nargs='*',
    help="List of uids"
)
cli_get.parser.set_defaults(func=cli_get)


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

    try:
        func(**kwargs)
        sys.exit(0)
    except Exception as e:
        if(hasattr(e, 'message')):
            print("Finished with exception message: %s\n" % e.message, file=sys.stderr)
        print("Raising exception again for details:", file=sys.stderr)
        raise e
        sys.exit(1)


if __name__ == '__main__':
    main()
