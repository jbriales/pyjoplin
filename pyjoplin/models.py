from io import open  # Unicode compatibility via default utf-8 encoding
import os
import traceback

from peewee import *
from playhouse.sqlite_ext import *


path_database = os.path.expanduser('~/.config/joplin-desktop/database.sqlite')
database = SqliteExtDatabase(path_database, **{})


class UnknownField(object):
    def __init__(self, *_, **__): pass


class BaseModel(Model):
    class Meta:
        database = database


class Alarms(BaseModel):
    note = TextField(column_name='note_id', index=True)
    trigger_time = IntegerField()

    class Meta:
        table_name = 'alarms'


class DeletedItems(BaseModel):
    deleted_time = IntegerField()
    item = TextField(column_name='item_id')
    item_type = IntegerField()
    sync_target = IntegerField(index=True)

    class Meta:
        table_name = 'deleted_items'


class Folders(BaseModel):
    created_time = IntegerField()
    encryption_applied = IntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    encryption_cipher_text = TextField(constraints=[SQL("DEFAULT '""'")])
    id = TextField(null=True, primary_key=True)
    parent = TextField(column_name='parent_id', constraints=[SQL("DEFAULT '""'")])
    title = TextField(constraints=[SQL("DEFAULT '""'")], index=True)
    updated_time = IntegerField(index=True)
    user_created_time = IntegerField(constraints=[SQL("DEFAULT 0")])
    user_updated_time = IntegerField(constraints=[SQL("DEFAULT 0")], index=True)

    class Meta:
        table_name = 'folders'


class ItemChanges(BaseModel):
    created_time = IntegerField(index=True)
    item = TextField(column_name='item_id', index=True)
    item_type = IntegerField(index=True)
    type = IntegerField()

    class Meta:
        table_name = 'item_changes'


class MasterKeys(BaseModel):
    checksum = TextField()
    content = TextField()
    created_time = IntegerField()
    encryption_method = IntegerField()
    id = TextField(null=True, primary_key=True)
    source_application = TextField()
    updated_time = IntegerField()

    class Meta:
        table_name = 'master_keys'


class NoteResources(BaseModel):
    is_associated = IntegerField()
    last_seen_time = IntegerField()
    note = TextField(column_name='note_id', index=True)
    resource = TextField(column_name='resource_id', index=True)

    class Meta:
        table_name = 'note_resources'


class NoteTags(BaseModel):
    created_time = IntegerField()
    encryption_applied = IntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    encryption_cipher_text = TextField(constraints=[SQL("DEFAULT '""'")])
    id = TextField(null=True, primary_key=True)
    note = TextField(column_name='note_id', index=True)
    tag = TextField(column_name='tag_id', index=True)
    updated_time = IntegerField(index=True)
    user_created_time = IntegerField(constraints=[SQL("DEFAULT 0")])
    user_updated_time = IntegerField(constraints=[SQL("DEFAULT 0")], index=True)

    class Meta:
        table_name = 'note_tags'


class Note(BaseModel):
    # altitude = UnknownField(constraints=[SQL("DEFAULT 0")])  # NUMERIC
    application_data = TextField(constraints=[SQL("DEFAULT '""'")])
    author = TextField(constraints=[SQL("DEFAULT '""'")])
    body = TextField(constraints=[SQL("DEFAULT '""'")])
    created_time = IntegerField()
    encryption_applied = IntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    encryption_cipher_text = TextField(constraints=[SQL("DEFAULT '""'")])
    id = TextField(null=True, primary_key=True)
    is_conflict = IntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    is_todo = IntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    # latitude = UnknownField(constraints=[SQL("DEFAULT 0")])  # NUMERIC
    # longitude = UnknownField(constraints=[SQL("DEFAULT 0")])  # NUMERIC
    order = IntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    parent = TextField(column_name='parent_id', constraints=[SQL("DEFAULT '""'")])
    source = TextField(constraints=[SQL("DEFAULT '""'")])
    source_application = TextField(constraints=[SQL("DEFAULT '""'")])
    source_url = TextField(constraints=[SQL("DEFAULT '""'")])
    title = TextField(constraints=[SQL("DEFAULT '""'")], index=True)
    todo_completed = IntegerField(constraints=[SQL("DEFAULT 0")])
    todo_due = IntegerField(constraints=[SQL("DEFAULT 0")])
    updated_time = IntegerField(index=True)
    user_created_time = IntegerField(constraints=[SQL("DEFAULT 0")])
    user_updated_time = IntegerField(constraints=[SQL("DEFAULT 0")], index=True)

    def to_file(self, file_path):
        """
        Store this note title and body into a text file
        :param file_path:
        :return:
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("%s\n\n%s" % (self.title, self.body))

    def from_file(self, file_path):
        """
        Populate this note title and body from a text file
        NOTE: This does not save the note in the database, just changes its content
        :param file_path:
        :return:
        """
        # Save new content to Notes table
        # NOTE: FTS entry is automatically updated within .save()
        with open(file_path, 'r', encoding='utf-8') as f:
            # Get summary from first line
            self.title = f.readline().strip()
            # Read rest of file as body
            self.body = f.read().strip()

    def save(self, *args, **kwargs):
        # Call default save method
        rows = super(Note, self).save(*args, **kwargs)
        # Store this note for full-text search
        try:
            NoteIndex.store_note(self)
        except OperationalError as err:
            print(traceback.format_exc())
            print("Sol: Run pyjoplin rebuild_fts_index?")
        return rows

    def delete_instance(self, *args, **kwargs):
        NoteIndex.remove_note(self)
        return super(Note, self).delete_instance(*args, **kwargs)

    class Meta:
        table_name = 'notes'


class NoteIndex(FTSModel):
    # Full-text search index.
    rowid = RowIDField()
    uid = TextField()
    title = SearchField()
    body = SearchField()

    @classmethod
    def store_note(cls, note):
        try:
            NoteIndex.get(NoteIndex.uid == note.id)
        except NoteIndex.DoesNotExist:
            NoteIndex.create(uid=note.id, title=note.title, body=note.body)
        else:
            (NoteIndex
                .update(title=note.title, body=note.body)
                .where(NoteIndex.uid == note.id)
                .execute())

    @classmethod
    def remove_note(cls, note):
        try:
            index_entry = NoteIndex.get(NoteIndex.uid == note.id)
            index_entry.delete_instance()
        except NoteIndex.DoesNotExist:
            pass

    class Meta:
        table_name = 'notes_index'
        database = database
        # Use the porter stemming algorithm to tokenize content.
        options = {'tokenize': 'porter'}


class Resources(BaseModel):
    created_time = IntegerField()
    encryption_applied = IntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    encryption_blob_encrypted = IntegerField(constraints=[SQL("DEFAULT 0")])
    encryption_cipher_text = TextField(constraints=[SQL("DEFAULT '""'")])
    file_extension = TextField(constraints=[SQL("DEFAULT '""'")])
    filename = TextField(constraints=[SQL("DEFAULT '""'")])
    id = TextField(null=True, primary_key=True)
    mime = TextField()
    title = TextField(constraints=[SQL("DEFAULT '""'")], index=True)
    updated_time = IntegerField(index=True)
    user_created_time = IntegerField(constraints=[SQL("DEFAULT 0")])
    user_updated_time = IntegerField(constraints=[SQL("DEFAULT 0")], index=True)

    class Meta:
        table_name = 'resources'


class Settings(BaseModel):
    key = TextField(null=True, primary_key=True)
    value = TextField(null=True)

    class Meta:
        table_name = 'settings'

# class SqliteSequence(BaseModel):
#     name = UnknownField(null=True)  #
#     seq = UnknownField(null=True)  #
#
#     class Meta:
#         table_name = 'sqlite_sequence'
#         primary_key = False


class SyncItems(BaseModel):
    force_sync = IntegerField(constraints=[SQL("DEFAULT 0")])
    item = TextField(column_name='item_id', index=True)
    item_type = IntegerField(index=True)
    # sync_disabled = IntegerField(constraints=[SQL("DEFAULT "0"")])
    sync_disabled_reason = TextField(constraints=[SQL("DEFAULT '""'")])
    sync_target = IntegerField(index=True)
    sync_time = IntegerField(constraints=[SQL("DEFAULT 0")], index=True)

    class Meta:
        table_name = 'sync_items'


class TableFields(BaseModel):
    field_default = TextField(null=True)
    field_name = TextField()
    field_type = IntegerField()
    table_name = TextField()

    class Meta:
        table_name = 'table_fields'


class Tags(BaseModel):
    created_time = IntegerField()
    encryption_applied = IntegerField(constraints=[SQL("DEFAULT 0")], index=True)
    encryption_cipher_text = TextField(constraints=[SQL("DEFAULT '""'")])
    id = TextField(null=True, primary_key=True)
    title = TextField(constraints=[SQL("DEFAULT '""'")], index=True)
    updated_time = IntegerField(index=True)
    user_created_time = IntegerField(constraints=[SQL("DEFAULT 0")])
    user_updated_time = IntegerField(constraints=[SQL("DEFAULT 0")], index=True)

    class Meta:
        table_name = 'tags'


class Version(BaseModel):
    version = IntegerField()

    class Meta:
        table_name = 'version'
        primary_key = False

