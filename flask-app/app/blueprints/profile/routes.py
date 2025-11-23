"""User profile routes."""
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.blueprints.profile import profile_bp
from app.models.user import User
from app.models.product import Producto
from app.models.order import Compra
from app.models.wishlist import Deseo
from app.extensions import db, csrf
from werkzeug.utils import secure_filename
import os


@profile_bp.route('/')
@login_required
def dashboard():
    """User dashboard."""
    from app.models.message import Mensaje

    # Get recent orders
    orders = current_user.get_orders()[:5]

    # Get wishlist count
    wishlist_count = current_user.deseos.count()

    # Get unread messages count
    user_mensajes_no_leidos = Mensaje.contar_no_leidos('user', current_user.id)

    return render_template('profile/dashboard.html',
                         orders=orders,
                         wishlist_count=wishlist_count,
                         user_mensajes_no_leidos=user_mensajes_no_leidos)


@profile_bp.route('/orders')
@login_required
def orders():
    """User orders history."""
    page = request.args.get('page', 1, type=int)
    orders = Compra.query.filter_by(id_usuario=current_user.id).order_by(
        Compra.fecha.desc()
    ).paginate(page=page, per_page=10, error_out=False)

    return render_template('profile/orders.html', orders=orders)


@profile_bp.route('/orders/<int:id>')
@login_required
def order_detail(id):
    """View order details with tracking information."""
    order = Compra.query.get_or_404(id)

    # Verify user owns this order
    if order.id_usuario != current_user.id:
        flash('No tienes permiso para ver este pedido.', 'error')
        return redirect(url_for('profile.orders'))

    # Calculate precio_total if not available
    precio_total = order.get_total()

    return render_template('profile/order_detail.html',
                         order=order,
                         precio_total=precio_total)


@profile_bp.route('/orders/<int:id>/cancel', methods=['POST'])
@login_required
def cancel_order(id):
    """Cancel an order."""
    order = Compra.query.get_or_404(id)

    # Verify user owns this order
    if order.id_usuario != current_user.id:
        flash('No tienes permiso para cancelar este pedido.', 'error')
        return redirect(url_for('profile.orders'))

    # Check if order can be cancelled
    if not order.puede_cancelar():
        flash('Este pedido no puede ser cancelado en su estado actual.', 'error')
        return redirect(url_for('profile.order_detail', id=id))

    try:
        order.cambiar_estado('cancelado')
        flash(f'Pedido #{order.id} cancelado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al cancelar pedido: {e}', 'error')

    return redirect(url_for('profile.order_detail', id=id))


@profile_bp.route('/wishlist')
@login_required
def wishlist():
    """User wishlist."""
    deseos = current_user.get_wishlist()

    products = []
    for deseo in deseos:
        products.append(deseo.producto)

    return render_template('profile/wishlist.html', products=products)


@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    """Edit user profile."""
    if request.method == 'POST':
        current_user.nombre = request.form.get('nombre', current_user.nombre)

        # Handle password change
        new_password = request.form.get('new_password')
        if new_password:
            current_password = request.form.get('current_password')
            if current_user.check_password(current_password):
                current_user.set_password(new_password)
            else:
                flash('Contraseña actual incorrecta.', 'error')
                return redirect(url_for('profile.edit'))

        # Handle photo upload
        if 'foto' in request.files:
            file = request.files['foto']
            if file and file.filename:
                from PIL import Image

                filename = secure_filename(file.filename)
                upload_folder = os.path.join('app/static/uploads/usuarios', str(current_user.id))

                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)

                filepath = os.path.join(upload_folder, filename)

                # Resize image to 500x500 using PIL
                try:
                    img = Image.open(file)
                    img = img.resize((500, 500), Image.Resampling.LANCZOS)
                    img.save(filepath)
                except Exception as e:
                    # If resize fails, save original
                    file.seek(0)  # Reset file pointer
                    file.save(filepath)

                current_user.foto = filepath.replace('app/static/', '')

        db.session.commit()
        flash('Perfil actualizado correctamente.', 'success')
        return redirect(url_for('profile.dashboard'))

    return render_template('profile/edit.html')


@profile_bp.route('/wishlist/toggle', methods=['POST'])
@login_required
@csrf.exempt
def toggle_wishlist():
    """Toggle product in wishlist."""
    try:
        data = request.get_json()
        producto_id = data.get('producto_id')

        if not producto_id:
            return jsonify({
                'success': False,
                'message': 'Producto inválido'
            }), 400

        producto = Producto.query.get(producto_id)
        if not producto:
            return jsonify({
                'success': False,
                'message': 'Producto no encontrado'
            }), 404

        # Check if already in wishlist
        deseo = Deseo.query.filter_by(
            id_usuario=current_user.id,
            id_producto=producto_id
        ).first()

        if deseo:
            # Remove from wishlist
            db.session.delete(deseo)
            db.session.commit()
            return jsonify({
                'success': True,
                'added': False,
                'message': 'Producto eliminado de favoritos'
            })
        else:
            # Add to wishlist
            nuevo_deseo = Deseo(
                id_usuario=current_user.id,
                id_producto=producto_id
            )
            db.session.add(nuevo_deseo)
            db.session.commit()
            return jsonify({
                'success': True,
                'added': True,
                'message': 'Producto agregado a favoritos'
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


@profile_bp.route('/delete', methods=['POST'])
@login_required
def delete():
    """Delete user account."""
    user_id = current_user.id

    # Delete user (cascade will delete related records)
    db.session.delete(current_user)
    db.session.commit()

    flash('Su cuenta ha sido eliminada.', 'info')
    return redirect(url_for('main.index'))


# ==================== MESSAGING SYSTEM ====================

@profile_bp.route('/mensajes')
@login_required
def mensajes():
    """User inbox - received messages."""
    from app.models.message import Mensaje

    # Get all received messages
    mensajes_recibidos = Mensaje.query.filter_by(
        destinatario_tipo='user',
        destinatario_id=current_user.id
    ).order_by(Mensaje.fecha.desc()).all()

    # Count unread messages
    no_leidos = Mensaje.contar_no_leidos('user', current_user.id)

    return render_template('profile/mensajes.html',
                         mensajes=mensajes_recibidos,
                         no_leidos=no_leidos,
                         tab='recibidos')


@profile_bp.route('/mensajes/enviados')
@login_required
def mensajes_enviados():
    """User sent messages."""
    from app.models.message import Mensaje

    # Get all sent messages
    mensajes_enviados = Mensaje.query.filter_by(
        remitente_tipo='user',
        remitente_id=current_user.id
    ).order_by(Mensaje.fecha.desc()).all()

    return render_template('profile/mensajes.html',
                         mensajes=mensajes_enviados,
                         tab='enviados')


@profile_bp.route('/mensajes/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_mensaje():
    """Compose new message to admin."""
    from app.models.message import Mensaje
    from app.models.admin import Administrador

    if request.method == 'POST':
        try:
            asunto = request.form.get('asunto', '').strip()
            contenido = request.form.get('contenido', '').strip()

            if not all([asunto, contenido]):
                flash('El asunto y contenido son obligatorios.', 'error')
                return redirect(url_for('profile.nuevo_mensaje'))

            # Get first active admin (or you could let user choose)
            admin = Administrador.query.filter_by(estado=1).first()

            if not admin:
                flash('No hay administradores disponibles para recibir mensajes.', 'error')
                return redirect(url_for('profile.mensajes'))

            # Send message (user to admin)
            mensaje = Mensaje.enviar_mensaje(
                remitente_tipo='user',
                remitente_id=current_user.id,
                destinatario_tipo='admin',
                destinatario_id=admin.id,
                asunto=asunto,
                contenido=contenido
            )

            flash(f'Mensaje enviado exitosamente. Recibirás respuesta pronto.', 'success')
            return redirect(url_for('profile.mensajes_enviados'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al enviar mensaje: {e}', 'error')

    # GET - show form
    return render_template('profile/mensaje_form.html',
                         mensaje=None)


@profile_bp.route('/mensajes/<int:id>')
@login_required
def ver_mensaje(id):
    """View message details."""
    from app.models.message import Mensaje

    mensaje = Mensaje.query.get_or_404(id)

    # Verify user has access to this message (either sender or recipient)
    if not ((mensaje.destinatario_tipo == 'user' and mensaje.destinatario_id == current_user.id) or
            (mensaje.remitente_tipo == 'user' and mensaje.remitente_id == current_user.id)):
        flash('No tiene permiso para ver este mensaje.', 'error')
        return redirect(url_for('profile.mensajes'))

    # Mark as read if user is recipient
    if mensaje.destinatario_tipo == 'user' and mensaje.destinatario_id == current_user.id:
        mensaje.marcar_como_leido()

    # Get conversation thread
    if mensaje.mensaje_padre_id:
        # This is a reply, get parent and all siblings
        padre = Mensaje.query.get(mensaje.mensaje_padre_id)
        conversacion = [padre] + list(padre.respuestas.all())
    else:
        # This is a parent message, get all replies
        conversacion = [mensaje] + list(mensaje.respuestas.all())

    return render_template('profile/mensaje_detalle.html',
                         mensaje=mensaje,
                         conversacion=conversacion)


@profile_bp.route('/mensajes/<int:id>/responder', methods=['GET', 'POST'])
@login_required
def responder_mensaje(id):
    """Reply to a message."""
    from app.models.message import Mensaje

    mensaje_original = Mensaje.query.get_or_404(id)

    # Verify user has access
    if not ((mensaje_original.destinatario_tipo == 'user' and mensaje_original.destinatario_id == current_user.id) or
            (mensaje_original.remitente_tipo == 'user' and mensaje_original.remitente_id == current_user.id)):
        flash('No tiene permiso para responder este mensaje.', 'error')
        return redirect(url_for('profile.mensajes'))

    if request.method == 'POST':
        try:
            contenido = request.form.get('contenido', '').strip()

            if not contenido:
                flash('El contenido del mensaje es obligatorio.', 'error')
                return redirect(url_for('profile.responder_mensaje', id=id))

            # Determine recipient (whoever is NOT the current user)
            if mensaje_original.remitente_tipo == 'user' and mensaje_original.remitente_id == current_user.id:
                # User sent original, reply to recipient (should be admin)
                dest_tipo = mensaje_original.destinatario_tipo
                dest_id = mensaje_original.destinatario_id
            else:
                # User received original, reply to sender (should be admin)
                dest_tipo = mensaje_original.remitente_tipo
                dest_id = mensaje_original.remitente_id

            # Find the root message for threading
            mensaje_padre_id = mensaje_original.mensaje_padre_id if mensaje_original.mensaje_padre_id else mensaje_original.id

            # Send reply
            respuesta = Mensaje.enviar_mensaje(
                remitente_tipo='user',
                remitente_id=current_user.id,
                destinatario_tipo=dest_tipo,
                destinatario_id=dest_id,
                asunto=f"Re: {mensaje_original.asunto}",
                contenido=contenido,
                mensaje_padre_id=mensaje_padre_id
            )

            flash('Respuesta enviada exitosamente.', 'success')
            return redirect(url_for('profile.ver_mensaje', id=mensaje_padre_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al enviar respuesta: {e}', 'error')

    # GET - show reply form
    return render_template('profile/mensaje_form.html',
                         mensaje=mensaje_original,
                         es_respuesta=True)


@profile_bp.route('/mensajes/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_mensaje(id):
    """Delete a message."""
    from app.models.message import Mensaje

    mensaje = Mensaje.query.get_or_404(id)

    # Verify user has access
    if not ((mensaje.destinatario_tipo == 'user' and mensaje.destinatario_id == current_user.id) or
            (mensaje.remitente_tipo == 'user' and mensaje.remitente_id == current_user.id)):
        flash('No tiene permiso para eliminar este mensaje.', 'error')
        return redirect(url_for('profile.mensajes'))

    try:
        asunto = mensaje.asunto
        db.session.delete(mensaje)
        db.session.commit()
        flash(f'Mensaje "{asunto}" eliminado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar mensaje: {e}', 'error')

    return redirect(url_for('profile.mensajes'))
