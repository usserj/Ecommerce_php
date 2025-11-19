"""Main blueprint routes."""
from flask import render_template, request
from app.blueprints.main import main_bp
from app.models.product import Producto
from app.models.categoria import Categoria
from app.models.setting import Slide
from app.services.analytics_service import track_visit


@main_bp.route('/')
def index():
    """Home page."""
    # Track visit
    track_visit(request.remote_addr)

    # Get featured/latest products
    productos_destacados = Producto.query.filter_by(estado=1)\
        .order_by(Producto.ventas.desc())\
        .limit(8).all()

    # Get products on offer
    productos_oferta = Producto.query.filter_by(estado=1, oferta=1)\
        .limit(4).all()

    # Get slides
    slides = Slide.query.order_by(Slide.orden).all()

    return render_template('main/index.html',
                         productos_destacados=productos_destacados,
                         productos_oferta=productos_oferta,
                         slides=slides)


@main_bp.route('/contacto', methods=['GET', 'POST'])
def contacto():
    """Contact page."""
    if request.method == 'POST':
        from app.services.email_service import send_contact_email
        from flask import flash

        nombre = request.form.get('nombre')
        email = request.form.get('email')
        mensaje = request.form.get('mensaje')

        if nombre and email and mensaje:
            success = send_contact_email(nombre, email, mensaje)
            if success:
                flash('Mensaje enviado correctamente. Le responderemos pronto.', 'success')
            else:
                flash('Gracias por su mensaje. Hemos guardado su consulta y le responderemos pronto.', 'info')
            return render_template('main/contacto.html')

    return render_template('main/contacto.html')


@main_bp.route('/sobre-nosotros')
def sobre_nosotros():
    """About us page."""
    return render_template('main/sobre_nosotros.html')
