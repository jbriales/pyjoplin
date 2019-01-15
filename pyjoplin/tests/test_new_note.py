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
        commands.delete(testnote_id)


if __name__ == '__main__':
    unittest.main()
