from peewee import *

database = SqliteDatabase('/home/jesus/.config/joplin/database.sqlite', **{})

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

    class Meta:
        table_name = 'notes'

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

