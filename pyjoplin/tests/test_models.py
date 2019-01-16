# coding=utf-8
import unittest

from pyjoplin.models import Note, NoteIndex, Folder


class TestModelNote(unittest.TestCase):

    def test_note_from_file(self):
        path_to_test_note = 'data/note.md'
        note = Note()
        note.from_file(path_to_test_note)

    def test_note_from_file_with_bad_notebook_format(self):
        path_to_test_note = 'data/note-with_bad_nb_format.md'
        note = Note()
        with self.assertRaises(RuntimeError) as cm:
            note.from_file(path_to_test_note)
        the_exception = cm.exception
        self.assertEqual(the_exception.message, 'Bad notebook line format')

    def test_note_from_file_with_bad_notebook_name(self):
        path_to_test_note = 'data/note-with_bad_nb_name.md'
        note = Note()
        with self.assertRaises(Folder.DoesNotExist) as cm:
            note.from_file(path_to_test_note)


if __name__ == '__main__':
    unittest.main()
