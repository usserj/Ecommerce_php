"""Authentication routes."""
from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app.blueprints.auth import auth_bp
from app.models.user import User
from app.extensions import db, limiter
from app.forms.auth import LoginForm, RegisterForm, ForgotPasswordForm
from app.services.email_service import send_verification_email, send_password_reset_email
from app.models.notification import Notificacion


@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per hour")
def register():
    """User registration."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegisterForm()

    if form.validate_on_submit():
        # Check if user already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('El email ya está registrado.', 'error')
            return redirect(url_for('auth.register'))

        # Create new user
        user = User(
            nombre=form.nombre.data,
            email=form.email.data,
            modo='directo',
            verificacion=1  # Pending verification
        )
        user.set_password(form.password.data)
        user.generate_verification_token()

        db.session.add(user)
        db.session.commit()

        # Update notifications
        Notificacion.increment_new_users()

        # Send verification email
        send_verification_email(user.email, user.emailEncriptado)

        flash('Registro exitoso. Por favor revise su email para verificar su cuenta.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    """User login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Email o contraseña incorrectos.', 'error')
            return redirect(url_for('auth.login'))

        if not user.is_verified():
            flash('Debe verificar su email antes de iniciar sesión.', 'warning')
            return redirect(url_for('auth.login'))

        # Migrate legacy password if needed
        user.migrate_password(form.password.data)

        # Login user
        login_user(user, remember=form.remember_me.data)

        # Redirect to next page or home
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('main.index')

        flash(f'Bienvenido {user.nombre}!', 'success')
        return redirect(next_page)

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    session.clear()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/verificar/<token>')
def verify_email(token):
    """Verify email address."""
    user = User.verify_email_token(token)

    if user:
        flash('Email verificado correctamente. Ahora puede iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))
    else:
        flash('Token de verificación inválido o expirado.', 'error')
        return redirect(url_for('main.index'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
@limiter.limit("3 per hour")
def forgot_password():
    """Request password reset."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = ForgotPasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user:
            # Generate reset token
            token = user.generate_reset_token(expiry_minutes=30)

            # Send email with reset link
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            send_password_reset_email(user.email, reset_url)

            flash('Se han enviado instrucciones para recuperar su contraseña a su email. El enlace expira en 30 minutos.', 'success')
        else:
            # Don't reveal if email exists (security best practice)
            flash('Si el email existe, recibirá instrucciones para recuperar su contraseña.', 'info')

        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html', form=form)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
@limiter.limit("5 per hour")
def reset_password(token):
    """Reset password with token."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    # Find user by token
    user = User.find_by_reset_token(token)

    if not user:
        flash('El enlace de recuperación es inválido o ha expirado. Por favor solicite uno nuevo.', 'error')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')

        # Validation
        if not password or not password_confirm:
            flash('Por favor complete todos los campos.', 'error')
            return render_template('auth/reset_password.html', token=token)

        # Validate password strength (same as registration)
        from app.utils.validators import validate_password_strength
        is_valid, message = validate_password_strength(password)
        if not is_valid:
            flash(message, 'error')
            return render_template('auth/reset_password.html', token=token)

        if password != password_confirm:
            flash('Las contraseñas no coinciden.', 'error')
            return render_template('auth/reset_password.html', token=token)

        # Update password
        user.set_password(password)
        user.clear_reset_token()

        flash('Contraseña actualizada exitosamente. Ahora puede iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', token=token)
