"""
Script para crear tablas necesarias para funcionalidades de IA

Ejecutar con:
    python -m app.migrations.add_ai_tables

O desde el directorio flask-app:
    python app/migrations/add_ai_tables.py
"""

import sys
import os

# Agregar el directorio raíz al path
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(current_dir)
flask_app_dir = os.path.dirname(app_dir)
sys.path.insert(0, flask_app_dir)

from app import create_app
from app.extensions import db


def create_ai_tables():
    """Crea las tablas para funcionalidades de IA"""

    print("╔════════════════════════════════════════════════════════════╗")
    print("║        CREANDO TABLAS PARA FUNCIONALIDADES DE IA          ║")
    print("╚════════════════════════════════════════════════════════════╝\n")

    app = create_app()

    with app.app_context():
        print("✓ Conectado a la base de datos\n")

        # Tabla conversaciones_chatbot
        print("📝 Creando tabla: conversaciones_chatbot")
        try:
            db.session.execute(db.text("""
                CREATE TABLE IF NOT EXISTS conversaciones_chatbot (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    session_id VARCHAR(100) NOT NULL,
                    usuario_id INT NULL,
                    rol VARCHAR(10) NOT NULL,
                    mensaje TEXT NOT NULL,
                    contexto TEXT NULL,
                    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_session (session_id),
                    INDEX idx_usuario (usuario_id),
                    INDEX idx_fecha (fecha),
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """))
            db.session.commit()
            print("✅ Tabla 'conversaciones_chatbot' creada exitosamente\n")
        except Exception as e:
            print(f"⚠️  Error al crear tabla 'conversaciones_chatbot': {e}")
            print(f"   (Puede que ya exista)\n")
            db.session.rollback()

        # Tabla analisis_reviews
        print("📝 Creando tabla: analisis_reviews")
        try:
            db.session.execute(db.text("""
                CREATE TABLE IF NOT EXISTS analisis_reviews (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    producto_id INT NULL,
                    sentimiento_positivo INT DEFAULT 0,
                    sentimiento_neutral INT DEFAULT 0,
                    sentimiento_negativo INT DEFAULT 0,
                    aspectos_positivos TEXT NULL,
                    aspectos_negativos TEXT NULL,
                    calidad_score DECIMAL(3,1),
                    recomendacion TEXT,
                    fecha_analisis DATETIME DEFAULT CURRENT_TIMESTAMP,
                    total_reviews INT,
                    INDEX idx_producto (producto_id),
                    INDEX idx_fecha (fecha_analisis),
                    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """))
            db.session.commit()
            print("✅ Tabla 'analisis_reviews' creada exitosamente\n")
        except Exception as e:
            print(f"⚠️  Error al crear tabla 'analisis_reviews': {e}")
            print(f"   (Puede que ya exista)\n")
            db.session.rollback()

        print("══════════════════════════════════════════════════════════")
        print("✓ Proceso completado")
        print("✓ Tablas de IA creadas/verificadas")
        print("✓ Sistema listo para usar funcionalidades de IA")
        print("══════════════════════════════════════════════════════════\n")

        print("📌 Próximos pasos:")
        print("1. Reinicia tu aplicación Flask: python run.py")
        print("2. Prueba el chatbot en cualquier página de la tienda")
        print("3. Verifica el panel admin para análisis de reviews")
        print("\n¡Todo listo! 🎉\n")


if __name__ == '__main__':
    create_ai_tables()
