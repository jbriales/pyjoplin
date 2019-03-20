# coding=utf-8
import dropbox
import unittest
import subprocess

from pyjoplin import commands
from pyjoplin.sync_dropbox_personal import dbx, list_all_files


class TestExternalDropboxSync(unittest.TestCase):

    def test_new_and_deleted_note_in_remote_dropbox(self):
        test_body = 'foo body'
        testnote_id = commands.new('test dropbox API delete', 'test', body=test_body)

        # Sync Joplin with remote Dropbox to upload new test note
        subprocess.check_call('joplin sync', shell=True)

        # Check new note is in remote Dropbox
        entries = list_all_files(dbx)
        testnote_name = u"%s.md" % testnote_id
        self.assertTrue(
            any(entry.name == testnote_name for entry in entries),
            msg='Test note creation was not synced in remote Dropbox'
        )

        # Delete local note
        commands.delete(testnote_id)

        # Sync Joplin with remote Dropbox to delete test note
        subprocess.check_call('joplin sync', shell=True)

        # Check note was deleted in remote Dropbox
        entries = list_all_files(dbx)
        filter_entries = [entry for entry in entries if entry.name == testnote_name]
        testnote_entry = next(entry for entry in entries if entry.name == testnote_name)
        self.assertIsInstance(
            testnote_entry, dropbox.files.DeletedMetadata,
            msg='Test note deletion was not synced in remote Dropbox'
        )


if __name__ == '__main__':
    unittest.main()
