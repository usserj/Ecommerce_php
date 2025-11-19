#!/usr/bin/env python
"""Apply database migrations."""
import pymysql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def apply_migration():
    """Apply SQL migration to database."""
    try:
        # Database connection
        connection = pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'Ecommerce_Ec'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        with connection.cursor() as cursor:
            # Read migration file
            migration_file = os.path.join(os.path.dirname(__file__), 'migrations', 'add_new_fields.sql')

            if not os.path.exists(migration_file):
                print(f"✓ Migration file not found: {migration_file}")
                return

            with open(migration_file, 'r', encoding='utf-8') as f:
                sql_script = f.read()

            # Split by semicolons and execute each statement
            statements = [s.strip() for s in sql_script.split(';') if s.strip() and not s.strip().startswith('--')]

            for statement in statements:
                if statement and not statement.startswith('USE'):
                    try:
                        cursor.execute(statement)
                        print(f"✓ Executed: {statement[:50]}...")
                    except pymysql.err.OperationalError as e:
                        # Ignore "duplicate column" errors (migration already applied)
                        if 'Duplicate column name' in str(e):
                            print(f"⊘ Column already exists (skipped)")
                        else:
                            print(f"✗ Error: {e}")

        connection.commit()
        print("\n✓ Migration applied successfully!")

        # Rename migration file so it doesn't run again
        if os.path.exists(migration_file):
            applied_file = migration_file.replace('.sql', '.applied.sql')
            os.rename(migration_file, applied_file)
            print(f"✓ Migration file marked as applied: {applied_file}")

    except Exception as e:
        print(f"✗ Migration failed: {e}")
        raise
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == '__main__':
    apply_migration()
