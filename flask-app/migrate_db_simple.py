#!/usr/bin/env python3
"""
Simple database migration script that doesn't require Flask app initialization
"""

import pymysql
import sys
import os

# Database connection details (update these if needed)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Update if you have a password
    'database': 'ecommerce_db',
    'charset': 'utf8mb4'
}

def run_migration():
    """Execute SQL migration for compras table."""
    try:
        print("🔄 Connecting to database...")

        # Connect to database
        connection = pymysql.connect(**DB_CONFIG)
        print(f"✅ Connected to database: {DB_CONFIG['database']}")

        # SQL statements to execute
        migrations = [
            ("Add precio_total column",
             "ALTER TABLE compras ADD COLUMN precio_total DECIMAL(10,2) DEFAULT NULL COMMENT 'Total price including shipping'"),

            ("Add estado column",
             "ALTER TABLE compras ADD COLUMN estado VARCHAR(20) DEFAULT 'pendiente' COMMENT 'Order status'"),

            ("Add tracking column",
             "ALTER TABLE compras ADD COLUMN tracking VARCHAR(100) DEFAULT NULL COMMENT 'Tracking number'"),

            ("Add fecha_estado column",
             "ALTER TABLE compras ADD COLUMN fecha_estado DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Last status update'"),

            ("Add index on estado",
             "ALTER TABLE compras ADD INDEX idx_estado (estado)"),

            ("Populate precio_total for existing records",
             "UPDATE compras SET precio_total = CAST(pago AS DECIMAL(10,2)) + COALESCE(envio, 0) WHERE precio_total IS NULL AND pago IS NOT NULL"),

            ("Set default estado for old records",
             "UPDATE compras SET estado = 'entregado' WHERE estado IS NULL OR estado = ''"),
        ]

        with connection.cursor() as cursor:
            for i, (description, sql) in enumerate(migrations, 1):
                try:
                    print(f"\n📝 {i}. {description}...")
                    cursor.execute(sql)
                    connection.commit()
                    print(f"✅ Success")
                except pymysql.err.OperationalError as e:
                    if 'Duplicate column' in str(e) or 'Duplicate key' in str(e):
                        print(f"⚠️  Already exists, skipping...")
                    else:
                        print(f"❌ Error: {e}")
                        raise

        # Verify changes
        print("\n🔍 Verifying changes...")
        with connection.cursor() as cursor:
            cursor.execute("DESCRIBE compras")
            columns = cursor.fetchall()

            column_names = [col[0] for col in columns]
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

            # Count orders
            cursor.execute("""
                SELECT COUNT(*) AS total_orders,
                       COUNT(precio_total) AS with_precio_total,
                       COUNT(tracking) AS with_tracking
                FROM compras
            """)
            stats = cursor.fetchone()
            print(f"\n📊 Statistics:")
            print(f"   Total orders: {stats[0]}")
            print(f"   With precio_total: {stats[1]}")
            print(f"   With tracking: {stats[2]}")

        connection.close()
        print("\n✅ Migration completed successfully!")
        return True

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("DATABASE MIGRATION FOR COMPRAS TABLE")
    print("=" * 60)
    print(f"\nTarget database: {DB_CONFIG['database']}")
    print(f"Host: {DB_CONFIG['host']}")

    response = input("\nProceed with migration? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Migration cancelled.")
        sys.exit(0)

    success = run_migration()
    sys.exit(0 if success else 1)
