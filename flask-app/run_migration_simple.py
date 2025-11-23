#!/usr/bin/env python3
"""
Simple migration script to add missing columns to compras table
"""

import pymysql
import sys

def run_migration():
    """Execute SQL migration for compras table."""

    # Database connection details (from config.py)
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'Ecommerce_Ec',
        'charset': 'utf8mb4'
    }

    try:
        print("🔄 Connecting to database...")
        connection = pymysql.connect(**db_config)
        print(f"✅ Connected to database: {db_config['database']}")

        # Read SQL file
        print("\n📖 Reading migration file...")
        with open('migrations/002_orden_estados_stock_audit.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # Split SQL by semicolons
        statements = [s.strip() for s in sql_content.split(';') if s.strip()]

        print(f"📝 Found {len(statements)} SQL statements\n")
        print("=" * 80)

        executed = 0
        skipped = 0
        errors = 0

        with connection.cursor() as cursor:
            for i, statement in enumerate(statements, 1):
                # Skip comments
                if statement.startswith('--'):
                    continue

                # Skip USE statements
                if statement.upper().strip().startswith('USE '):
                    print(f"[{i}] ⏭️  Skipping USE statement")
                    skipped += 1
                    continue

                # Execute SELECT statements but don't fail on them
                if statement.upper().strip().startswith('SELECT'):
                    print(f"[{i}] ⏭️  Skipping verification query")
                    skipped += 1
                    continue

                try:
                    # Print first 80 chars of statement
                    preview = statement.replace('\n', ' ')[:80]
                    print(f"\n[{i}] 🔧 {preview}...")

                    cursor.execute(statement)
                    connection.commit()
                    executed += 1
                    print(f"     ✅ Success")

                except pymysql.err.OperationalError as e:
                    error_str = str(e)
                    if 'Duplicate column' in error_str:
                        print(f"     ⚠️  Column already exists (skipping)")
                        skipped += 1
                    elif 'Duplicate key' in error_str or "already exists" in error_str:
                        print(f"     ⚠️  Index/table already exists (skipping)")
                        skipped += 1
                    else:
                        print(f"     ❌ Error: {e}")
                        errors += 1
                except Exception as e:
                    print(f"     ❌ Error: {e}")
                    errors += 1

        print("\n" + "=" * 80)
        print(f"\n📊 Migration Summary:")
        print(f"   ✅ Executed successfully: {executed}")
        print(f"   ⏭️  Skipped: {skipped}")
        print(f"   ❌ Errors: {errors}")

        # Verify the migration
        print("\n" + "=" * 80)
        print("🔍 Verifying migration...\n")

        with connection.cursor() as cursor:
            cursor.execute("DESCRIBE compras")
            columns = cursor.fetchall()

            column_names = [col[0] for col in columns]

            # Check if our columns exist
            required_cols = ['precio_total', 'estado', 'tracking', 'fecha_estado']
            found = [col for col in required_cols if col in column_names]
            missing = [col for col in required_cols if col not in column_names]

            print("📋 Required columns status:")
            for col in required_cols:
                if col in column_names:
                    print(f"   ✅ {col}")
                else:
                    print(f"   ❌ {col} (MISSING)")

            # Check tables
            cursor.execute("SHOW TABLES LIKE 'stock_movements'")
            if cursor.fetchone():
                print(f"\n   ✅ stock_movements table")
            else:
                print(f"\n   ⚠️  stock_movements table (not created)")

            cursor.execute("SHOW TABLES LIKE 'stock_reservations'")
            if cursor.fetchone():
                print(f"   ✅ stock_reservations table")
            else:
                print(f"   ⚠️  stock_reservations table (not created)")

            if missing:
                print(f"\n❌ Migration incomplete: Missing columns: {', '.join(missing)}")
                return False
            else:
                print(f"\n✅ ✅ ✅ Migration completed successfully!")
                print(f"   All {len(found)} required columns exist in 'compras' table")
                return True

    except FileNotFoundError:
        print("❌ Migration file not found: migrations/002_orden_estados_stock_audit.sql")
        return False
    except pymysql.err.OperationalError as e:
        print(f"❌ Database connection error: {e}")
        print("\n💡 Tips:")
        print("   - Check if MySQL is running")
        print("   - Verify database name: Ecommerce_Ec")
        print("   - Verify credentials: root user with no password")
        return False
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'connection' in locals():
            connection.close()
            print("\n🔌 Database connection closed")

if __name__ == '__main__':
    print("=" * 80)
    print("🚀 DATABASE MIGRATION - Order States & Stock Audit")
    print("=" * 80 + "\n")

    success = run_migration()

    print("\n" + "=" * 80)
    if success:
        print("✅ MIGRATION COMPLETED SUCCESSFULLY")
    else:
        print("❌ MIGRATION FAILED")
    print("=" * 80)

    sys.exit(0 if success else 1)
