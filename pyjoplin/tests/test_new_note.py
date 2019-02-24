# coding=utf-8
import unittest

from pyjoplin import commands
from pyjoplin.models import Note, NoteIndex, Folder


class TestNewNote(unittest.TestCase):

    def test_new_note_in_non_existing_notebook(self):
        with self.assertRaises(Folder.DoesNotExist) as exc:
            commands.new('foo note', 'bar not existing notebook')

    def test_new_note(self):
        testnote_id = commands.new('foo test', 'test')
        retrieved_note = Note.get(Note.id == testnote_id)
        commands.delete(testnote_id)

    def test_new_note_with_body(self):
        test_body = 'foo body'
        testnote_id = commands.new('foo test', 'test', body=test_body)

        retrieved_note = Note.get(Note.id == testnote_id)
        self.assertEqual(retrieved_note.body, test_body)

        commands.delete(testnote_id)

    def test_delete_note_from_fts(self):
        test_query = 'asdfghjkl'
        testnote_id = commands.new('foo test', 'test', body=test_query)
        commands.delete(testnote_id)
        # Check entry was removed from fulltext search works
        # NOTE: Index should be updated upon .delete_instance()
        found_index_notes = commands.search(test_query)
        self.assertEqual(len(found_index_notes), 0)


if __name__ == '__main__':
    unittest.main()
