"""Administrator model."""
from datetime import datetime
from flask_login import UserMixin
from app.extensions import db, bcrypt

# Windows-compatible crypt implementation
try:
    import crypt
    HAS_CRYPT = True
except ImportError:
    # Windows doesn't have crypt module, use passlib as fallback
    try:
        from passlib.hash import des_crypt, md5_crypt, sha256_crypt, sha512_crypt
        HAS_CRYPT = False
    except ImportError:
        # If passlib is not installed, disable legacy password support
        HAS_CRYPT = None


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
        Windows-compatible implementation.
        """
        if not self.password:
            return False

        # Check if it's a bcrypt hash (starts with $2a$, $2b$, or $2y$)
        if self.password.startswith(('$2a$', '$2b$', '$2y$')):
            return bcrypt.check_password_hash(self.password, password)

        # Legacy PHP crypt() support - cross-platform
        if HAS_CRYPT is None:
            # No crypt support available, legacy passwords won't work
            # User will need to reset password
            return False

        try:
            if HAS_CRYPT:
                # Unix/Linux: use native crypt
                return self.password == crypt.crypt(password, self.password)
            else:
                # Windows: use passlib
                hash_type = self.password.split('$')[1] if '$' in self.password else None

                if hash_type == '1':
                    # MD5-based crypt
                    return md5_crypt.verify(password, self.password)
                elif hash_type == '5':
                    # SHA-256 crypt
                    return sha256_crypt.verify(password, self.password)
                elif hash_type == '6':
                    # SHA-512 crypt
                    return sha512_crypt.verify(password, self.password)
                else:
                    # DES crypt (old format)
                    return des_crypt.verify(password, self.password)
        except Exception:
            return False

    def is_admin(self):
        """Check if user is administrator."""
        return self.perfil == 'administrador'

    def is_active_user(self):
        """Check if user is active."""
        return self.estado == 1
