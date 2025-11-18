"""OAuth authentication (Google, Facebook)."""
from flask import url_for, redirect, flash, session, current_app
from flask_login import login_user
from app.blueprints.auth import auth_bp
from app.extensions import oauth, db
from app.models.user import User
from app.models.notification import Notificacion
import logging

logger = logging.getLogger(__name__)


@auth_bp.route('/login/google')
def google_login():
    """Initiate Google OAuth login."""
    # Check if Google OAuth is configured
    if not current_app.config.get('GOOGLE_CLIENT_ID') or not current_app.config.get('GOOGLE_CLIENT_SECRET'):
        flash('El inicio de sesión con Google no está configurado. Use el registro directo.', 'warning')
        return redirect(url_for('auth.login'))

    try:
        redirect_uri = url_for('auth.google_callback', _external=True, _scheme='https' if current_app.config.get('PREFERRED_URL_SCHEME') == 'https' else 'http')
        return oauth.google.authorize_redirect(redirect_uri)
    except Exception as e:
        logger.error(f"Error iniciando OAuth con Google: {e}", exc_info=True)
        flash('Error al iniciar sesión con Google. Intente con el registro directo.', 'error')
        return redirect(url_for('auth.login'))


@auth_bp.route('/login/google/callback')
def google_callback():
    """Handle Google OAuth callback."""
    try:
        token = oauth.google.authorize_access_token()
        user_info = token.get('userinfo')

        if not user_info or 'email' not in user_info:
            flash('Error al obtener información de Google.', 'error')
            return redirect(url_for('auth.login'))

        # Check if user exists
        user = User.query.filter_by(email=user_info['email']).first()

        if user:
            # User exists, check if modo is compatible
            if user.modo != 'google' and user.modo != 'directo':
                flash(f'Este email está registrado con {user.modo}. Use ese método para iniciar sesión.', 'error')
                return redirect(url_for('auth.login'))

            # Update user info
            if user.modo == 'directo':
                user.modo = 'google'

            if 'name' in user_info:
                user.nombre = user_info['name']

            if 'picture' in user_info:
                user.foto = user_info['picture']

            user.verificacion = 0  # Google users are verified
            db.session.commit()

        else:
            # Create new user
            user = User(
                nombre=user_info.get('name', user_info['email'].split('@')[0]),
                email=user_info['email'],
                foto=user_info.get('picture', ''),
                modo='google',
                verificacion=0  # Google users are pre-verified
            )
            db.session.add(user)
            db.session.commit()

            # Increment new users counter
            Notificacion.increment_new_users()

        # Login user
        login_user(user)
        flash(f'Bienvenido {user.nombre}!', 'success')
        return redirect(url_for('main.index'))

    except Exception as e:
        logger.error(f"Error en callback de Google: {e}", exc_info=True)
        flash('Error al iniciar sesión con Google. Por favor, intente nuevamente.', 'error')
        return redirect(url_for('auth.login'))


@auth_bp.route('/login/facebook')
def facebook_login():
    """Initiate Facebook OAuth login."""
    # Check if Facebook OAuth is configured
    if not current_app.config.get('FACEBOOK_CLIENT_ID') or not current_app.config.get('FACEBOOK_CLIENT_SECRET'):
        flash('El inicio de sesión con Facebook no está configurado. Use el registro directo.', 'warning')
        return redirect(url_for('auth.login'))

    try:
        redirect_uri = url_for('auth.facebook_callback', _external=True, _scheme='https' if current_app.config.get('PREFERRED_URL_SCHEME') == 'https' else 'http')
        return oauth.facebook.authorize_redirect(redirect_uri)
    except Exception as e:
        logger.error(f"Error iniciando OAuth con Facebook: {e}", exc_info=True)
        flash('Error al iniciar sesión con Facebook. Intente con el registro directo.', 'error')
        return redirect(url_for('auth.login'))


@auth_bp.route('/login/facebook/callback')
def facebook_callback():
    """Handle Facebook OAuth callback."""
    try:
        token = oauth.facebook.authorize_access_token()

        # Get user info
        resp = oauth.facebook.get('me?fields=id,name,email,picture')
        user_info = resp.json()

        if not user_info or 'email' not in user_info:
            flash('Error al obtener información de Facebook.', 'error')
            return redirect(url_for('auth.login'))

        # Check if user exists
        user = User.query.filter_by(email=user_info['email']).first()

        if user:
            # User exists
            if user.modo != 'facebook' and user.modo != 'directo':
                flash(f'Este email está registrado con {user.modo}. Use ese método para iniciar sesión.', 'error')
                return redirect(url_for('auth.login'))

            # Update user info
            if user.modo == 'directo':
                user.modo = 'facebook'

            user.nombre = user_info.get('name', user.nombre)

            if 'picture' in user_info and 'data' in user_info['picture']:
                user.foto = user_info['picture']['data'].get('url', '')

            user.verificacion = 0  # Facebook users are verified
            db.session.commit()

        else:
            # Create new user
            foto = ''
            if 'picture' in user_info and 'data' in user_info['picture']:
                foto = user_info['picture']['data'].get('url', '')

            user = User(
                nombre=user_info.get('name', user_info['email'].split('@')[0]),
                email=user_info['email'],
                foto=foto,
                modo='facebook',
                verificacion=0  # Facebook users are pre-verified
            )
            db.session.add(user)
            db.session.commit()

            # Increment new users counter
            Notificacion.increment_new_users()

        # Login user
        login_user(user)
        flash(f'Bienvenido {user.nombre}!', 'success')
        return redirect(url_for('main.index'))

    except Exception as e:
        logger.error(f"Error en callback de Facebook: {e}", exc_info=True)
        flash('Error al iniciar sesión con Facebook. Por favor, intente nuevamente.', 'error')
        return redirect(url_for('auth.login'))
