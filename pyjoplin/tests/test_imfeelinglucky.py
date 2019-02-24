# coding=utf-8
import unittest

from pyjoplin import commands


class TestImfeelinglucky(unittest.TestCase):

    def setUp(self):
        # List of testnote ids that need to be cleaned up at the end of test
        self.testnote_ids = list()

    def test_imfeelinglucky_stub_multiline(self):
        test_title = 'pyjoplin-test test_note_search_single_word'
        test_body = """
foo foo foo

# Solution: (working or not)
blablabla
```python
code
stub
```

bar bar bar
"""

        note_id = commands.new(test_title, 'test', body=test_body)
        self.testnote_ids.append(note_id)

        stub = commands.imfeelinglucky(note_id)
        self.assertEqual(stub, 'code\nstub')

        # Check clipboard was correctly populated
        import pyperclip
        clipboard_content = pyperclip.paste()
        self.assertEqual(stub, clipboard_content)

    def test_imfeelinglucky_stub_inline(self):
        test_title = 'pyjoplin-test test_note_search_single_word'
        test_stub = 'asdfghjkl'
        test_body = """
            foo foo foo

            # Solution: (working or not)
            blablabla `%s`

            bar bar bar
            """ % test_stub

        note_id = commands.new(test_title, 'test', body=test_body)
        self.testnote_ids.append(note_id)

        stub = commands.imfeelinglucky(note_id)
        self.assertEqual(stub, test_stub)

        # Check clipboard was correctly populated
        import pyperclip
        clipboard_content = pyperclip.paste()
        self.assertEqual(stub, clipboard_content)

    def tearDown(self):
        for note_id in self.testnote_ids:
            commands.delete(note_id)


if __name__ == '__main__':
    unittest.main()
