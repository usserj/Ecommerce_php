"""User profile routes."""
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.blueprints.profile import profile_bp
from app.models.user import User
from app.extensions import db
from werkzeug.utils import secure_filename
import os


@profile_bp.route('/')
@login_required
def dashboard():
    """User dashboard."""
    # Get recent orders
    orders = current_user.get_orders()[:5]

    # Get wishlist count
    wishlist_count = current_user.deseos.count()

    return render_template('profile/dashboard.html',
                         orders=orders,
                         wishlist_count=wishlist_count)


@profile_bp.route('/orders')
@login_required
def orders():
    """User orders history."""
    page = request.args.get('page', 1, type=int)
    orders = current_user.compras.order_by(current_user.compras.c.fecha.desc()).paginate(
        page=page, per_page=10, error_out=False
    )

    return render_template('profile/orders.html', orders=orders)


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
                filename = secure_filename(file.filename)
                upload_folder = os.path.join('app/static/uploads/usuarios', str(current_user.id))

                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)

                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)

                current_user.foto = filepath.replace('app/static/', '')

        db.session.commit()
        flash('Perfil actualizado correctamente.', 'success')
        return redirect(url_for('profile.dashboard'))

    return render_template('profile/edit.html')


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
