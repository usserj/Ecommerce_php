"""Shop/Product catalog routes."""
from flask import render_template, request, abort, redirect, url_for
from app.blueprints.shop import shop_bp
from app.models.product import Producto
from app.models.categoria import Categoria, Subcategoria
from app.models.comment import Comentario
from app.models.setting import Banner
from sqlalchemy import or_


@shop_bp.route('/')
@shop_bp.route('/categoria/<ruta>')
def index(ruta=None):
    """Product listing page."""
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort', 'reciente')  # reciente, vendidos, precio_asc, precio_desc
    per_page = 12

    query = Producto.query.filter_by(estado=1)

    # Filter by category and get banners
    categoria = None
    banners = []

    if ruta:
        categoria = Categoria.query.filter_by(ruta=ruta, estado=1).first_or_404()
        query = query.filter_by(id_categoria=categoria.id)
        # Get category-specific banners
        banners = Banner.get_banners_for_category(ruta)
    else:
        # Get general banners for home/all products page
        banners = Banner.get_general_banners()

    # Sorting
    if sort_by == 'vendidos':
        query = query.order_by(Producto.ventas.desc())
    elif sort_by == 'precio_asc':
        query = query.order_by(Producto.precio.asc())
    elif sort_by == 'precio_desc':
        query = query.order_by(Producto.precio.desc())
    else:  # reciente (default)
        query = query.order_by(Producto.fecha.desc())

    # Pagination
    productos = query.paginate(
        page=page, per_page=per_page, error_out=False
    )

    categorias = Categoria.query.filter_by(estado=1).all()

    return render_template('shop/products.html',
                         productos=productos,
                         categorias=categorias,
                         categoria_actual=categoria,
                         banners=banners,
                         sort_by=sort_by)


@shop_bp.route('/producto/<ruta>')
def product_detail(ruta):
    """Product detail page."""
    producto = Producto.query.filter_by(ruta=ruta, estado=1).first_or_404()

    # Increment views
    producto.increment_views()

    # Get related products
    relacionados = Producto.query.filter(
        Producto.id_categoria == producto.id_categoria,
        Producto.id != producto.id,
        Producto.estado == 1
    ).limit(4).all()

    # Get comments
    comentarios = producto.comentarios.order_by(Comentario.fecha.desc()).all()

    return render_template('shop/product_detail.html',
                         producto=producto,
                         relacionados=relacionados,
                         comentarios=comentarios)


@shop_bp.route('/buscar')
def search():
    """Search products."""
    q = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = 12

    if not q:
        return redirect(url_for('shop.index'))

    # Search in title and description
    productos = Producto.query.filter(
        or_(
            Producto.titulo.like(f'%{q}%'),
            Producto.descripcion.like(f'%{q}%')
        ),
        Producto.estado == 1
    ).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('shop/search.html',
                         productos=productos,
                         query=q)


@shop_bp.route('/ofertas')
def ofertas():
    """Products on offer."""
    page = request.args.get('page', 1, type=int)
    per_page = 12

    productos = Producto.query.filter_by(estado=1, oferta=1).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('shop/ofertas.html', productos=productos)


@shop_bp.route('/producto/<ruta>/comentar', methods=['POST'])
def add_comment(ruta):
    """Add a comment/review to a product."""
    from flask_login import login_required, current_user
    from flask import flash, redirect, url_for
    from app.extensions import db
    from app.models.order import Compra
    
    # Require login
    if not current_user.is_authenticated:
        flash('Debes iniciar sesión para dejar un comentario.', 'error')
        return redirect(url_for('auth.login'))
    
    producto = Producto.query.filter_by(ruta=ruta, estado=1).first_or_404()
    
    # Validate that user has purchased this product
    has_purchased = Compra.query.filter_by(
        id_usuario=current_user.id,
        id_producto=producto.id
    ).first()
    
    if not has_purchased:
        flash('Solo puedes comentar productos que hayas comprado.', 'error')
        return redirect(url_for('shop.product_detail', ruta=ruta))
    
    # Check if user already commented this product
    existing_comment = Comentario.query.filter_by(
        id_usuario=current_user.id,
        id_producto=producto.id
    ).first()
    
    if existing_comment:
        flash('Ya has comentado este producto. Puedes editar tu comentario existente.', 'warning')
        return redirect(url_for('shop.product_detail', ruta=ruta))
    
    comentario_texto = request.form.get('comentario')
    calificacion = request.form.get('calificacion', 5, type=int)
    
    if not comentario_texto:
        flash('El comentario no puede estar vacío.', 'error')
        return redirect(url_for('shop.product_detail', ruta=ruta))
    
    # Validate rating (1-5)
    if calificacion < 1 or calificacion > 5:
        calificacion = 5
    
    comentario = Comentario(
        id_usuario=current_user.id,
        id_producto=producto.id,
        comentario=comentario_texto,
        calificacion=calificacion
    )
    
    db.session.add(comentario)
    db.session.commit()
    
    flash('¡Gracias por tu comentario!', 'success')
    return redirect(url_for('shop.product_detail', ruta=ruta))


@shop_bp.route('/comentario/editar/<int:id>', methods=['POST'])
def edit_comment(id):
    """Edit user's own comment."""
    from flask_login import login_required, current_user
    from flask import flash, redirect, url_for, request
    from app.extensions import db
    
    # Require login
    if not current_user.is_authenticated:
        flash('Debes iniciar sesión.', 'error')
        return redirect(url_for('auth.login'))
    
    comentario = Comentario.query.get_or_404(id)
    
    # Verify ownership
    if comentario.id_usuario != current_user.id:
        flash('No tienes permiso para editar este comentario.', 'error')
        return redirect(url_for('shop.product_detail', ruta=comentario.producto.ruta))
    
    comentario_texto = request.form.get('comentario')
    calificacion = request.form.get('calificacion', type=int)
    
    if comentario_texto:
        comentario.comentario = comentario_texto
    
    if calificacion and 1 <= calificacion <= 5:
        comentario.calificacion = calificacion
    
    db.session.commit()
    
    flash('Comentario actualizado exitosamente.', 'success')
    return redirect(url_for('shop.product_detail', ruta=comentario.producto.ruta))


@shop_bp.route('/comentario/eliminar/<int:id>', methods=['POST'])
def delete_comment(id):
    """Delete user's own comment."""
    from flask_login import login_required, current_user
    from flask import flash, redirect, url_for
    from app.extensions import db
    
    # Require login
    if not current_user.is_authenticated:
        flash('Debes iniciar sesión.', 'error')
        return redirect(url_for('auth.login'))
    
    comentario = Comentario.query.get_or_404(id)
    
    # Verify ownership
    if comentario.id_usuario != current_user.id:
        flash('No tienes permiso para eliminar este comentario.', 'error')
        return redirect(url_for('shop.product_detail', ruta=comentario.producto.ruta))
    
    producto_ruta = comentario.producto.ruta
    
    db.session.delete(comentario)
    db.session.commit()
    
    flash('Comentario eliminado exitosamente.', 'success')
    return redirect(url_for('shop.product_detail', ruta=producto_ruta))
