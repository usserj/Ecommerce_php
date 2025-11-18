"""Email service."""
from flask import current_app, render_template, url_for
from flask_mail import Message
from app.extensions import mail
from threading import Thread


def send_async_email(app, msg):
    """Send email asynchronously."""
    with app.app_context():
        mail.send(msg)


def send_email(subject, recipient, template, **kwargs):
    """Send email using template."""
    msg = Message(
        subject,
        recipients=[recipient],
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )
    msg.html = render_template(f'emails/{template}.html', **kwargs)

    # Send async
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()


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
    msg = Message(
        subject=f'Consulta de {nombre}',
        recipients=[current_app.config['MAIL_DEFAULT_SENDER']],
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        reply_to=email
    )
    msg.body = f"""
    Nombre: {nombre}
    Email: {email}

    Mensaje:
    {mensaje}
    """
    mail.send(msg)


def send_order_confirmation_email(user, order):
    """Send order confirmation email."""
    send_email(
        subject='Confirmación de Compra - Tienda Virtual',
        recipient=user.email,
        template='order_confirmation',
        user=user,
        order=order
    )
