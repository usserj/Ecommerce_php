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


@shop_bp.route('/categoria/<cat_ruta>/subcategoria/<subcat_ruta>')
def subcategory(cat_ruta, subcat_ruta):
    """Products filtered by subcategory."""
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort', 'reciente')
    per_page = 12

    # Find category first
    categoria = Categoria.query.filter_by(ruta=cat_ruta, estado=1).first_or_404()

    # Find subcategory
    subcategoria = Subcategoria.query.filter_by(
        ruta=subcat_ruta,
        id_categoria=categoria.id,
        estado=1
    ).first_or_404()

    # Filter products by subcategory
    query = Producto.query.filter_by(
        id_subcategoria=subcategoria.id,
        estado=1
    )

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

    # Get subcategory banners
    banners = Banner.get_banners_for_subcategory(subcat_ruta)

    categorias = Categoria.query.filter_by(estado=1).all()

    return render_template('shop/products.html',
                         productos=productos,
                         categorias=categorias,
                         categoria_actual=categoria,
                         subcategoria_actual=subcategoria,
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
    """Search products with AI-powered intelligent search and advanced filters."""
    q = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = 12

    # Advanced filters
    precio_min = request.args.get('precio_min', type=float)
    precio_max = request.args.get('precio_max', type=float)
    categoria_id = request.args.get('categoria', type=int)
    rating_min = request.args.get('rating', type=int)
    solo_oferta = request.args.get('oferta', type=int, default=0)
    solo_stock = request.args.get('stock', type=int, default=0)
    ordenar = request.args.get('sort', default='relevancia')

    if not q:
        return redirect(url_for('shop.index'))

    # Variables para resultados de IA
    intencion_usuario = None
    sugerencias_busqueda = []
    use_ai = False

    # Base query
    query = Producto.query.filter(Producto.estado == 1)

    # Intentar búsqueda inteligente con IA (solo para queries más específicas)
    if len(q.strip()) > 3:
        try:
            from app.services.ai_service import ai_service
            resultado_ia = ai_service.busqueda_inteligente(q)

            if resultado_ia.get('success') and resultado_ia.get('productos_ids'):
                # IA encontró productos relevantes
                productos_ids = resultado_ia.get('productos_ids', [])
                intencion_usuario = resultado_ia.get('intencion_usuario', '')
                sugerencias_busqueda = resultado_ia.get('sugerencias_busqueda', [])

                # Buscar productos por IDs recomendados por IA
                if productos_ids:
                    query = query.filter(Producto.id.in_(productos_ids))
                    use_ai = True
        except Exception as e:
            # Si falla IA, continuar con búsqueda SQL tradicional
            print(f"Error en búsqueda con IA: {e}")
            pass

    # Fallback: Búsqueda SQL tradicional si IA no se usó
    if not use_ai:
        query = query.filter(
            or_(
                Producto.titulo.like(f'%{q}%'),
                Producto.descripcion.like(f'%{q}%')
            )
        )

    # Apply advanced filters
    if precio_min is not None:
        query = query.filter(Producto.precio >= precio_min)

    if precio_max is not None:
        query = query.filter(Producto.precio <= precio_max)

    if categoria_id:
        query = query.filter(Producto.id_categoria == categoria_id)

    if rating_min:
        # Filter products with average rating >= rating_min
        from sqlalchemy import func
        from app.models.comment import Comentario

        subquery = db.session.query(
            Comentario.id_producto,
            func.avg(Comentario.calificacion).label('avg_rating')
        ).group_by(Comentario.id_producto)\
         .having(func.avg(Comentario.calificacion) >= rating_min)\
         .subquery()

        query = query.join(subquery, Producto.id == subquery.c.id_producto)

    if solo_oferta:
        query = query.filter(Producto.oferta > 0)

    if solo_stock:
        query = query.filter(Producto.stock > 0)

    # Apply sorting
    if ordenar == 'precio_asc':
        query = query.order_by(Producto.precio.asc())
    elif ordenar == 'precio_desc':
        query = query.order_by(Producto.precio.desc())
    elif ordenar == 'mas_vendidos':
        query = query.order_by(Producto.ventas.desc())
    elif ordenar == 'reciente':
        query = query.order_by(Producto.id.desc())
    # else: relevancia (order from AI or default)

    productos = query.paginate(page=page, per_page=per_page, error_out=False)

    # Get categories for filter
    from app.models.categoria import Categoria
    categorias = Categoria.query.filter_by(estado=1).order_by(Categoria.categoria).all()

    return render_template('shop/search.html',
                         productos=productos,
                         query=q,
                         intencion_usuario=intencion_usuario,
                         sugerencias_busqueda=sugerencias_busqueda,
                         use_ai=use_ai,
                         categorias=categorias,
                         # Pass filter values back to template
                         precio_min=precio_min,
                         precio_max=precio_max,
                         categoria_id=categoria_id,
                         rating_min=rating_min,
                         solo_oferta=solo_oferta,
                         solo_stock=solo_stock,
                         ordenar=ordenar)


@shop_bp.route('/ofertas')
def ofertas():
    """Products on offer."""
    page = request.args.get('page', 1, type=int)
    per_page = 12

    productos = Producto.query.filter_by(estado=1, oferta=1).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('shop/ofertas.html', productos=productos)


@shop_bp.route('/product/<int:id>/comment', methods=['POST'])
def add_comment_api(id):
    """Add a comment/review to a product (API endpoint)."""
    from flask_login import current_user
    from flask import jsonify
    from app.extensions import db
    from app.models.order import Compra

    # Require login
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'message': 'Debes iniciar sesión para dejar un comentario.'}), 401

    producto = Producto.query.get_or_404(id)

    # Validate that user has purchased this product
    has_purchased = Compra.query.filter_by(
        id_usuario=current_user.id,
        id_producto=producto.id
    ).first()

    if not has_purchased:
        return jsonify({'success': False, 'message': 'Solo puedes comentar productos que hayas comprado.'}), 403

    # Check if user already commented this product
    existing_comment = Comentario.query.filter_by(
        id_usuario=current_user.id,
        id_producto=producto.id
    ).first()

    if existing_comment:
        return jsonify({'success': False, 'message': 'Ya has comentado este producto. Puedes editar tu comentario existente.'}), 400

    # Get form data
    comentario_texto = request.form.get('comentario')
    calificacion = request.form.get('calificacion', 5, type=int)

    if not comentario_texto:
        return jsonify({'success': False, 'message': 'El comentario no puede estar vacío.'}), 400

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

    return jsonify({
        'success': True,
        'message': '¡Gracias por tu comentario!',
        'comment': {
            'id': comentario.id,
            'usuario': current_user.nombre,
            'comentario': comentario.comentario,
            'calificacion': comentario.calificacion,
            'fecha': comentario.fecha.strftime('%d/%m/%Y')
        }
    })


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


@shop_bp.route('/comment/<int:id>/vote-helpful', methods=['POST'])
def vote_helpful(id):
    """Vote a review as helpful."""
    comentario = Comentario.query.get_or_404(id)

    # Increment helpful votes
    comentario.increment_helpful_votes()

    return jsonify({
        'success': True,
        'helpful_votes': comentario.helpful_votes,
        'message': '¡Gracias por tu feedback!'
    })
