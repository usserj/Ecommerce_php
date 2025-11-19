"""Authentication forms."""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp


class LoginForm(FlaskForm):
    """Login form."""

    email = StringField('Email', validators=[
        DataRequired(message='El email es requerido'),
        Email(message='Email inválido')
    ])

    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es requerida')
    ])

    remember_me = BooleanField('Recuérdame')
    submit = SubmitField('Iniciar Sesión')


class RegisterForm(FlaskForm):
    """Registration form."""

    nombre = StringField('Nombre', validators=[
        DataRequired(message='El nombre es requerido'),
        Length(min=2, max=100, message='El nombre debe tener entre 2 y 100 caracteres'),
        Regexp('^[a-zA-ZñÑáéíóúÁÉÍÓÚ ]+$', message='El nombre solo puede contener letras')
    ])

    email = StringField('Email', validators=[
        DataRequired(message='El email es requerido'),
        Email(message='Email inválido')
    ])

    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es requerida'),
        Length(min=6, message='La contraseña debe tener al menos 6 caracteres'),
        Regexp('^[a-zA-Z0-9]+$', message='La contraseña solo puede contener letras y números')
    ])

    password2 = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(message='Debe confirmar la contraseña'),
        EqualTo('password', message='Las contraseñas no coinciden')
    ])

    submit = SubmitField('Registrarse')


class ForgotPasswordForm(FlaskForm):
    """Forgot password form."""

    email = StringField('Email', validators=[
        DataRequired(message='El email es requerido'),
        Email(message='Email inválido')
    ])

    submit = SubmitField('Recuperar Contraseña')
