"""Administrator model."""
import crypt
from datetime import datetime
from flask_login import UserMixin
from app.extensions import db, bcrypt


class Administrador(UserMixin, db.Model):
    """Administrator model for backend users."""

    __tablename__ = 'administradores'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    foto = db.Column(db.String(255), default='')
    password = db.Column(db.String(255), nullable=False)
    perfil = db.Column(db.String(50), default='editor')  # administrador, editor
    estado = db.Column(db.Integer, default=1)  # 1=active, 0=inactive
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Administrador {self.email}>'

    def set_password(self, password):
        """Set password hash using bcrypt."""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Check password against hash.

        Supports both legacy PHP crypt() hashes and new bcrypt hashes.
        """
        if not self.password:
            return False

        # Check if it's a bcrypt hash
        if self.password.startswith(('$2a$', '$2b$', '$2y$')):
            return bcrypt.check_password_hash(self.password, password)

        # Legacy PHP crypt() support
        try:
            return self.password == crypt.crypt(password, self.password)
        except Exception:
            return False

    def is_admin(self):
        """Check if user is administrator."""
        return self.perfil == 'administrador'

    def is_active_user(self):
        """Check if user is active."""
        return self.estado == 1
