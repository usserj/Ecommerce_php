"""
Punto de entrada de la aplicación Flask Ecommerce
Migrado desde PHP a Python/Flask
"""
import os
from app import create_app, db
from app.models import (
    Usuario, Administrador, Producto, Categoria, Subcategoria,
    Compra, Deseo, Banner, Slide, Cabecera, Comercio,
    Notificacion, Visita, Comentario
)

# Determinar el entorno
config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)


@app.shell_context_processor
def make_shell_context():
    """
    Hace que db y los modelos estén disponibles en el shell de Flask
    Uso: flask shell
    """
    return {
        'db': db,
        'Usuario': Usuario,
        'Administrador': Administrador,
        'Producto': Producto,
        'Categoria': Categoria,
        'Subcategoria': Subcategoria,
        'Compra': Compra,
        'Deseo': Deseo,
        'Banner': Banner,
        'Slide': Slide,
        'Cabecera': Cabecera,
        'Comercio': Comercio,
        'Notificacion': Notificacion,
        'Visita': Visita,
        'Comentario': Comentario
    }


@app.cli.command()
def test():
    """Ejecuta los tests unitarios"""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@app.cli.command()
def init_db():
    """Inicializa la base de datos"""
    db.create_all()
    print('✅ Base de datos inicializada')


@app.cli.command()
def seed_db():
    """Llena la base de datos con datos de ejemplo"""
    from scripts.seed import seed_database
    seed_database()
    print('✅ Base de datos poblada con datos de ejemplo')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
