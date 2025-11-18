"""Shop/Product catalog routes."""
from flask import render_template, request, abort
from app.blueprints.shop import shop_bp
from app.models.product import Producto
from app.models.categoria import Categoria, Subcategoria
from app.models.comment import Comentario
from sqlalchemy import or_


@shop_bp.route('/')
@shop_bp.route('/categoria/<ruta>')
def index(ruta=None):
    """Product listing page."""
    page = request.args.get('page', 1, type=int)
    per_page = 12

    query = Producto.query.filter_by(estado=1)

    # Filter by category
    categoria = None
    if ruta:
        categoria = Categoria.query.filter_by(ruta=ruta, estado=1).first_or_404()
        query = query.filter_by(id_categoria=categoria.id)

    # Pagination
    productos = query.order_by(Producto.fecha.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    categorias = Categoria.query.filter_by(estado=1).all()

    return render_template('shop/products.html',
                         productos=productos,
                         categorias=categorias,
                         categoria_actual=categoria)


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
