"""Migration script to add payment gateway columns to comercio table."""
from app import create_app
from app.extensions import db
import pymysql

app = create_app()

def migrate_payment_gateways():
    """Add new payment gateway columns to comercio table."""
    with app.app_context():
        connection = db.engine.raw_connection()
        cursor = connection.cursor()

        try:
            print("🔧 Agregando columnas de pasarelas de pago...")

            # Paymentez columns
            columns_to_add = [
                ("modoPaymentez", "VARCHAR(20) DEFAULT 'test'"),
                ("appCodePaymentez", "TEXT"),
                ("appKeyPaymentez", "TEXT"),

                # Datafast columns
                ("modoDatafast", "VARCHAR(20) DEFAULT 'test'"),
                ("midDatafast", "VARCHAR(100)"),
                ("tidDatafast", "VARCHAR(100)"),

                # De Una columns
                ("modoDeUna", "VARCHAR(20) DEFAULT 'test'"),
                ("apiKeyDeUna", "TEXT"),

                # Bank accounts
                ("cuentasBancarias", "TEXT"),
            ]

            for column_name, column_def in columns_to_add:
                try:
                    # Check if column exists
                    cursor.execute(f"SHOW COLUMNS FROM comercio LIKE '{column_name}'")
                    result = cursor.fetchone()

                    if not result:
                        # Add column if it doesn't exist
                        sql = f"ALTER TABLE comercio ADD COLUMN {column_name} {column_def}"
                        cursor.execute(sql)
                        connection.commit()
                        print(f"✅ Agregada columna: {column_name}")
                    else:
                        print(f"⏭️  Columna ya existe: {column_name}")

                except pymysql.err.OperationalError as e:
                    print(f"⚠️  Error agregando {column_name}: {e}")
                    connection.rollback()

            print("\n✅ Migración completada exitosamente!")

        except Exception as e:
            print(f"❌ Error durante la migración: {e}")
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()


if __name__ == '__main__':
    migrate_payment_gateways()
