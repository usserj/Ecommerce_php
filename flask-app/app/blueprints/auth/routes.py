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
    """Forgot password."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = ForgotPasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user:
            # Generate new password
            import secrets
            import string
            new_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))

            # Update password
            user.set_password(new_password)
            db.session.commit()

            # Send email with new password
            send_password_reset_email(user.email, new_password)

            flash('Se ha enviado una nueva contraseña a su email.', 'success')
        else:
            # Don't reveal if email exists
            flash('Si el email existe, recibirá instrucciones para recuperar su contraseña.', 'info')

        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html', form=form)
