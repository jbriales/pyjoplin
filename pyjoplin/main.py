#!/usr/bin/env python2
# coding=utf-8
"""
Interface Joplin via python
"""

import argparse
import six
import sys

from pyjoplin.commands import *


def test():
    """
    Test main pyjoplin functionalities: new, search
    :return:
    """
    # Create new test note
    print("Creating new test note...")
    test_title = 'temp-test-for-pyjoplin'
    test_query = 'asdfghjkl'
    new(test_title, 'search')
    print("... succeeded!")

    # Create content for test note
    print("Saving content for test note...")
    new_note = Note.get(Note.title == test_title)
    new_note.body = 'This is a %s word' % test_query
    num_saved = new_note.save()
    assert num_saved == 1
    print("... succeeded!")

    # Check fulltext search works
    # NOTE: Index should be updated upon .save()
    print("Check test note was indexed in the FTS table...")
    found_index_notes = search(test_query)
    assert len(found_index_notes) == 1
    print("... succeeded!")

    # Delete note
    # NOTE: Index should be updated upon .delete()
    delete(new_note.id)

    # Check entry was removed from fulltext search works
    # NOTE: Index should be updated upon .delete_instance()
    print("Check test note removed from FTS index after deletion...")
    found_index_notes = search(test_query)
    assert len(found_index_notes) == 0
    print("... succeeded!")

    print("Complete test succeeded!")

    
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
    # sys.exit(0 if successful else 1)


if __name__ == '__main__':
    main()
