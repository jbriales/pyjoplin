# coding=utf-8
import unittest

from pyjoplin import commands
from pyjoplin.models import Folder, Note, NoteIndex


class TestSynonyms(unittest.TestCase):
    def test_minimal_kw(self):
        the_input = "py"
        the_output = commands.replace_synonyms(the_input)
        expected_output = "(py OR python)"
        self.assertEqual(the_output, expected_output)

    def test_kw_contained_in_str(self):
        # py is in the set of keywords and contained as subword of python
        the_input = "python"
        the_output = commands.replace_synonyms(the_input)
        expected_output = "(py OR python)"
        self.assertEqual(the_output, expected_output)


if __name__ == "__main__":
    unittest.main()
