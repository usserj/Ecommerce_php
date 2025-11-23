#!/usr/bin/env python3
"""
Script to run database migration for adding precio_total and tracking columns
"""

import pymysql
import sys
from app import create_app
from app.extensions import db

def run_migration():
    """Execute SQL migration for compras table."""
    app = create_app()

    with app.app_context():
        try:
            print("🔄 Running database migration...")

            # Get database connection info from config
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']

            # Extract connection details
            # Format: mysql+pymysql://user:pass@host/dbname
            import re
            match = re.match(r'mysql\+pymysql://([^:]+):([^@]+)@([^/]+)/(.+)', db_uri)
            if not match:
                print("❌ Could not parse database URI")
                return False

            user, password, host, database = match.groups()

            # Read SQL file
            with open('migrations/002_orden_estados_stock_audit.sql', 'r') as f:
                sql_content = f.read()

            # Connect to database
            connection = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                cursorclass=pymysql.cursors.DictCursor
            )

            print(f"✅ Connected to database: {database}")

            # Split SQL by semicolons and execute each statement
            statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]

            with connection.cursor() as cursor:
                for i, statement in enumerate(statements, 1):
                    # Skip USE statements as we already selected the database
                    if statement.upper().startswith('USE'):
                        continue

                    # Skip SELECT verification queries
                    if statement.upper().startswith('SELECT'):
                        print(f"⏭️  Skipping verification query {i}")
                        continue

                    try:
                        print(f"📝 Executing statement {i}...")
                        cursor.execute(statement)
                        connection.commit()
                        print(f"✅ Statement {i} executed successfully")
                    except pymysql.err.OperationalError as e:
                        if 'Duplicate column' in str(e) or 'Duplicate key' in str(e):
                            print(f"⚠️  Column/index already exists, skipping...")
                        else:
                            print(f"❌ Error in statement {i}: {e}")
                            raise

            # Verify changes
            with connection.cursor() as cursor:
                cursor.execute("DESCRIBE compras")
                columns = cursor.fetchall()

                column_names = [col['Field'] for col in columns]
                print("\n✅ Current columns in compras table:")
                for col_name in column_names:
                    print(f"   - {col_name}")

                # Check if our columns exist
                required_cols = ['precio_total', 'estado', 'tracking', 'fecha_estado']
                missing = [col for col in required_cols if col not in column_names]

                if missing:
                    print(f"\n❌ Missing columns: {missing}")
                    return False
                else:
                    print(f"\n✅ All required columns exist!")

            connection.close()
            print("\n✅ Migration completed successfully!")
            return True

        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)
