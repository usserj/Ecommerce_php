#!/usr/bin/env python3
"""Run SMTP configuration migration."""
from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    # Add SMTP columns to comercio table
    migrations = [
        "ALTER TABLE comercio ADD COLUMN IF NOT EXISTS mailServer VARCHAR(100) DEFAULT 'smtp.gmail.com'",
        "ALTER TABLE comercio ADD COLUMN IF NOT EXISTS mailPort INT DEFAULT 587",
        "ALTER TABLE comercio ADD COLUMN IF NOT EXISTS mailUseTLS BOOLEAN DEFAULT TRUE",
        "ALTER TABLE comercio ADD COLUMN IF NOT EXISTS mailUsername VARCHAR(255)",
        "ALTER TABLE comercio ADD COLUMN IF NOT EXISTS mailPassword TEXT",
        "ALTER TABLE comercio ADD COLUMN IF NOT EXISTS mailDefaultSender VARCHAR(255)"
    ]

    try:
        for migration in migrations:
            try:
                db.session.execute(db.text(migration))
                print(f"✓ Ejecutado: {migration[:60]}...")
            except Exception as e:
                # Column might already exist, that's okay
                if "Duplicate column name" in str(e):
                    print(f"⚠ Columna ya existe: {migration[:60]}...")
                else:
                    raise

        db.session.commit()
        print("\n✅ Migración SMTP completada exitosamente!")

    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error en migración: {e}")
        raise
