"""Email service."""
from flask import current_app, render_template, url_for, flash
from flask_mail import Message
from app.extensions import mail
from threading import Thread
import logging

logger = logging.getLogger(__name__)


def send_async_email(app, msg):
    """Send email asynchronously."""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            logger.error(f"Error sending email: {e}", exc_info=True)


def send_email(subject, recipient, template, **kwargs):
    """Send email using template."""
    # Check if email is configured
    if not current_app.config.get('MAIL_USERNAME') or not current_app.config.get('MAIL_PASSWORD'):
        logger.warning("Email no configurado. No se enviará el correo.")
        return False

    try:
        msg = Message(
            subject,
            recipients=[recipient],
            sender=current_app.config.get('MAIL_DEFAULT_SENDER') or current_app.config.get('MAIL_USERNAME')
        )
        msg.html = render_template(f'emails/{template}.html', **kwargs)

        # Send async
        Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
        return True
    except Exception as e:
        logger.error(f"Error preparando email: {e}", exc_info=True)
        return False


def send_verification_email(email, token):
    """Send email verification."""
    verification_url = url_for('auth.verify_email', token=token, _external=True)

    send_email(
        subject='Verificación de Email - Tienda Virtual',
        recipient=email,
        template='verification',
        verification_url=verification_url
    )


def send_password_reset_email(email, new_password):
    """Send password reset email."""
    send_email(
        subject='Nueva Contraseña - Tienda Virtual',
        recipient=email,
        template='reset_password',
        new_password=new_password
    )


def send_contact_email(nombre, email, mensaje):
    """Send contact form email."""
    # Check if email is configured
    if not current_app.config.get('MAIL_USERNAME') or not current_app.config.get('MAIL_PASSWORD'):
        logger.warning("Email no configurado. El mensaje de contacto no se enviará por email.")
        # In a real application, you might want to save this to a database instead
        return False

    try:
        default_sender = current_app.config.get('MAIL_DEFAULT_SENDER') or current_app.config.get('MAIL_USERNAME')
        msg = Message(
            subject=f'Consulta de {nombre}',
            recipients=[default_sender],
            sender=default_sender,
            reply_to=email
        )
        msg.body = f"""
        Nombre: {nombre}
        Email: {email}

        Mensaje:
        {mensaje}
        """
        mail.send(msg)
        return True
    except Exception as e:
        logger.error(f"Error enviando email de contacto: {e}", exc_info=True)
        return False


def send_order_confirmation_email(user, order):
    """Send order confirmation email."""
    send_email(
        subject='Confirmación de Compra - Tienda Virtual',
        recipient=user.email,
        template='order_confirmation',
        user=user,
        order=order
    )
