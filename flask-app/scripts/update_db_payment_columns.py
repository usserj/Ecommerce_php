#!/usr/bin/env python3
"""Add payment gateway columns to comercio table."""
import pymysql
import sys

def add_payment_columns():
    """Add new payment gateway columns to comercio table."""
    print("🔧 Conectando a la base de datos...")

    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='Ecommerce_Ec',
            charset='utf8mb4'
        )
        cursor = connection.cursor()

        print("✅ Conexión exitosa!")
        print("\n🔧 Agregando columnas de pasarelas de pago...")

        # List of columns to add: (name, definition)
        columns = [
            ("modoPaymentez", "VARCHAR(20) DEFAULT 'test'"),
            ("appCodePaymentez", "TEXT"),
            ("appKeyPaymentez", "TEXT"),
            ("modoDatafast", "VARCHAR(20) DEFAULT 'test'"),
            ("midDatafast", "VARCHAR(100)"),
            ("tidDatafast", "VARCHAR(100)"),
            ("modoDeUna", "VARCHAR(20) DEFAULT 'test'"),
            ("apiKeyDeUna", "TEXT"),
            ("cuentasBancarias", "TEXT"),
        ]

        for column_name, column_def in columns:
            try:
                # Check if column exists
                cursor.execute(f"SHOW COLUMNS FROM comercio LIKE '{column_name}'")
                result = cursor.fetchone()

                if not result:
                    # Add column
                    sql = f"ALTER TABLE comercio ADD COLUMN {column_name} {column_def}"
                    cursor.execute(sql)
                    connection.commit()
                    print(f"  ✅ Agregada: {column_name}")
                else:
                    print(f"  ⏭️  Ya existe: {column_name}")

            except pymysql.err.OperationalError as e:
                print(f"  ⚠️  Error con {column_name}: {e}")
                connection.rollback()

        print("\n✅ Migración completada exitosamente!")

        cursor.close()
        connection.close()

        return 0

    except pymysql.err.OperationalError as e:
        print(f"❌ Error de conexión: {e}")
        print("\n💡 Verifica que MySQL esté corriendo y las credenciales sean correctas.")
        return 1
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(add_payment_columns())
