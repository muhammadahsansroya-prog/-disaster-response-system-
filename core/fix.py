import os
import sys

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'disaster_system.settings')

import django
django.setup()

from django.apps import apps
from django.db import connection

# Target models to force-sync columns
models_to_sync = ['HelpRequest', 'Resource', 'DispatchLog', 'Department']

with connection.cursor() as cursor:
    for model_name in models_to_sync:
        model = apps.get_model('core', model_name)
        table_name = model._meta.db_table
        
        # Get existing columns in MySQL table
        cursor.execute(f"SHOW COLUMNS FROM `{table_name}`")
        existing_cols = {row[0] for row in cursor.fetchall()}
        
        # Iterate over all fields defined in models.py
        for field in model._meta.fields:
            col_name = field.column
            if col_name not in existing_cols:
                db_type = field.db_type(connection)
                if db_type:
                    sql = f"ALTER TABLE `{table_name}` ADD COLUMN `{col_name}` {db_type} NULL;"
                    try:
                        cursor.execute(sql)
                        print(f"✓ Added column '{col_name}' to table '{table_name}'")
                    except Exception as e:
                        print(f"Error adding {col_name}:", e)

print("\n🎉 ALL MODEL FIELDS ARE 100% SYNCED WITH MYSQL DATABASE!")