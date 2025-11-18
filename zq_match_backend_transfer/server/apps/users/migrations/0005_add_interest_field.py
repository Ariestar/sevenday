from django.db import migrations


class Migration(migrations.Migration):
    """
    No-op migration to preserve history.
    The 'interest' field already exists from 0001_initial; this migration
    previously attempted to add it again, causing duplicate column errors
    on fresh databases (e.g., SQLite in tests).

    Keeping this as an empty migration ensures forward-compatibility while
    avoiding redundant schema operations. Subsequent migration 0006 will
    handle any field alterations if needed.
    """

    dependencies = [
        ("users", "0004_remove_user_application_alter_user_email_and_more"),
    ]

    operations = []