# coding=utf-8
import unittest

from pyjoplin import commands
from pyjoplin.models import Folder, Note, NoteIndex


class TestSynonyms(unittest.TestCase):
    def test_py(self):
        the_input = "py"
        the_output = commands.replace_synonyms(the_input)
        expected_output = "(py OR python)"
        self.assertEqual(the_output, expected_output)

    def test_python(self):
        the_input = "python"
        the_output = commands.replace_synonyms(the_input)
        expected_output = "(py OR python)"
        self.assertEqual(the_output, expected_output)


if __name__ == "__main__":
    unittest.main()
