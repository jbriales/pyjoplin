# coding=utf-8
import os
import unittest

from pyjoplin import commands
from pyjoplin.models import Note, NoteIndex, Folder

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


class TestModelNote(unittest.TestCase):

    def test_note_from_file(self):
        path_to_test_note = os.path.join(THIS_DIR, 'data/note.md')
        note = Note()
        note.from_file(path_to_test_note)

    def test_note_from_file_with_bad_notebook_format(self):
        path_to_test_note = os.path.join(THIS_DIR, 'data/note-with_bad_nb_format.md')
        note = Note()
        with self.assertRaises(RuntimeError) as cm:
            note.from_file(path_to_test_note)
        the_exception = cm.exception
        self.assertEqual(the_exception.message, 'Bad notebook line format')

    def test_note_from_file_with_bad_notebook_name(self):
        path_to_test_note = os.path.join(THIS_DIR, 'data/note-with_bad_nb_name.md')
        note = Note()
        with self.assertRaises(Folder.DoesNotExist) as cm:
            note.from_file(path_to_test_note)

    def test_note_to_file_with_unicode(self):
        test_title = 'pyjoplin_test test_note_to_file_with_unicode'
        test_body = u"This is a unicode string: \u2192"

        note_id = commands.new(test_title, 'test', body=test_body)
        new_note = Note.get(Note.id == note_id)

        path_tempfile = '/tmp/pyjoplin/test_note_to_file_with_unicode'
        new_note.to_file(path_tempfile)

        backup_body = new_note.body
        new_note.from_file(path_tempfile)

        self.assertEqual(new_note.body, backup_body)


if __name__ == '__main__':
    unittest.main()
