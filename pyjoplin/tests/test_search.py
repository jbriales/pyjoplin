# coding=utf-8
import unittest

from pyjoplin import commands
from pyjoplin.models import Note, NoteIndex, Folder


def generate_random_word(N):
    # TODO: Cleanup (keep here as a hack until I move this to its own file)
    import string
    import random

    return "".join(random.choices(string.ascii_lowercase, k=N))


class TestSearchAliases(unittest.TestCase):
    def test_alias_only_found_after_space(self):
        reference_str = "at: foo"
        modified_str = commands.substitute_search_column_aliases(reference_str)
        self.assertEqual(
            reference_str,
            modified_str,
            msg="'t:' should be substituted ONLY after '^' (BOL) or ' ' (space)",
        )


class TestNoteSearch(unittest.TestCase):
    def setUp(self):
        # List of testnote ids that need to be cleaned up at the end of test
        self.testnote_ids = list()

    def test_note_search_single_word(self):
        test_title = "pyjoplin-test test_note_search_single_word"
        test_query = generate_random_word(30)
        test_body = (
            u"""
            This is a %s word
            """
            % test_query
        )

        note_id = commands.new(test_title, "test", body=test_body)
        self.testnote_ids.append(note_id)

        # Check fulltext search works
        found_index_notes = commands.search(test_query)
        self.assertEqual(len(found_index_notes), 1)

    def test_note_search_with_title_alias(self):
        test_query = generate_random_word(30)
        # Create note that should be found
        note_id = commands.new(
            "test_pyjoplin test_note_search_with_title_alias %s" % test_query,
            "test",
            body="foo body",
        )
        self.testnote_ids.append(note_id)

        # Create note that should NOT be found
        note_id = commands.new(
            "test_pyjoplin test_note_search_with_title_alias bar",
            "test",
            body="foo body %s" % test_query,
        )
        self.testnote_ids.append(note_id)

        # Check alias filter 't:' works (finding only 1st note)
        search_str = "t: %s" % test_query
        found_index_notes = commands.search(search_str)
        self.assertEqual(len(found_index_notes), 1)

        # Check alias filter 's:' works (finding only 2nd note)
        search_str = "b: %s" % test_query
        found_index_notes = commands.search(search_str)
        self.assertEqual(len(found_index_notes), 1)

    def tearDown(self):
        for note_id in self.testnote_ids:
            commands.delete(note_id)


if __name__ == "__main__":
    unittest.main()
