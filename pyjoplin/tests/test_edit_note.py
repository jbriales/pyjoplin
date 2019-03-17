# coding=utf-8
import unittest

from pyjoplin import commands


class TestNewNote(unittest.TestCase):

    @unittest.skip("for manual debug")
    def test_edit_note_with_body(self):
        test_body = 'foo body'
        testnote_id = commands.new('foo test', 'test', body=test_body)

        # Edit to manually debug
        commands.edit(testnote_id)

        commands.delete(testnote_id)


if __name__ == '__main__':
    unittest.main()
