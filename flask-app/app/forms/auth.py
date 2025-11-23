"""Authentication forms."""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, ValidationError
from app.utils.validators import validate_password_strength


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
        Regexp('^[a-zA-ZñÑáéíóúÁÉÍÓÚ ]+$', message='El nombre solo puede contener letras y espacios')
    ])

    email = StringField('Email', validators=[
        DataRequired(message='El email es requerido'),
        Email(message='Email inválido')
    ])

    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es requerida'),
        Length(min=8, max=128, message='La contraseña debe tener entre 8 y 128 caracteres')
    ])

    password2 = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(message='Debe confirmar la contraseña'),
        EqualTo('password', message='Las contraseñas no coinciden')
    ])

    submit = SubmitField('Registrarse')

    def validate_password(self, field):
        """Custom password strength validation."""
        is_valid, message = validate_password_strength(field.data)
        if not is_valid:
            raise ValidationError(message)


class ForgotPasswordForm(FlaskForm):
    """Forgot password form."""

    email = StringField('Email', validators=[
        DataRequired(message='El email es requerido'),
        Email(message='Email inválido')
    ])

    submit = SubmitField('Recuperar Contraseña')
