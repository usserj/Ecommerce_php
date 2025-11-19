"""User model."""
import hashlib
import secrets
from datetime import datetime, timedelta
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


class User(UserMixin, db.Model):
    """User model for customers."""

    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=True)  # Nullable for OAuth users
    foto = db.Column(db.String(255), default='')
    modo = db.Column(db.String(20), default='directo')  # directo, facebook, google
    verificacion = db.Column(db.Integer, default=1)  # 0=verified, 1=pending
    emailEncriptado = db.Column('emailEncriptado', db.String(255))
    reset_token = db.Column(db.String(255), nullable=True)  # Password reset token
    reset_token_expiry = db.Column(db.DateTime, nullable=True)  # Token expiration
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    compras = db.relationship(
        'Compra', backref='usuario', lazy='dynamic',
        cascade='all, delete-orphan'
    )
    comentarios = db.relationship(
        'Comentario', backref='usuario', lazy='dynamic',
        cascade='all, delete-orphan'
    )
    deseos = db.relationship(
        'Deseo', backref='usuario', lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<User {self.email}>'

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

    def migrate_password(self, password):
        """Migrate from legacy crypt() to bcrypt.

        Call this after successful login with legacy password.
        """
        if not self.password.startswith(('$2a$', '$2b$', '$2y$')):
            self.set_password(password)
            db.session.commit()

    def generate_verification_token(self):
        """Generate email verification token."""
        if not self.emailEncriptado:
            self.emailEncriptado = hashlib.md5(self.email.encode()).hexdigest()
            db.session.commit()
        return self.emailEncriptado

    @staticmethod
    def verify_email_token(token):
        """Verify email token and activate user."""
        user = User.query.filter_by(emailEncriptado=token).first()
        if user:
            user.verificacion = 0
            db.session.commit()
            return user
        return None

    def generate_reset_token(self, expiry_minutes=30):
        """Generate password reset token.

        Args:
            expiry_minutes: Token validity in minutes (default: 30)

        Returns:
            str: Reset token
        """
        # Generate secure random token
        token = secrets.token_urlsafe(32)

        # Set token and expiry
        self.reset_token = token
        self.reset_token_expiry = datetime.utcnow() + timedelta(minutes=expiry_minutes)

        db.session.commit()
        return token

    def verify_reset_token(self):
        """Verify if reset token is valid and not expired.

        Returns:
            bool: True if token is valid, False otherwise
        """
        if not self.reset_token or not self.reset_token_expiry:
            return False

        # Check if token has expired
        if datetime.utcnow() > self.reset_token_expiry:
            return False

        return True

    def clear_reset_token(self):
        """Clear password reset token after use."""
        self.reset_token = None
        self.reset_token_expiry = None
        db.session.commit()

    @staticmethod
    def find_by_reset_token(token):
        """Find user by reset token.

        Args:
            token: Reset token

        Returns:
            User: User object if found and token is valid, None otherwise
        """
        user = User.query.filter_by(reset_token=token).first()
        if user and user.verify_reset_token():
            return user
        return None

    def is_verified(self):
        """Check if user email is verified."""
        return self.verificacion == 0

    def get_orders(self):
        """Get user's orders."""
        from app.models.order import Compra
        return self.compras.order_by(Compra.fecha.desc()).all()

    def get_wishlist(self):
        """Get user's wishlist."""
        return self.deseos.all()

    def add_to_wishlist(self, producto_id):
        """Add product to wishlist."""
        from app.models.wishlist import Deseo

        if not self.deseos.filter_by(id_producto=producto_id).first():
            deseo = Deseo(id_usuario=self.id, id_producto=producto_id)
            db.session.add(deseo)
            db.session.commit()
            return True
        return False

    def remove_from_wishlist(self, producto_id):
        """Remove product from wishlist."""
        deseo = self.deseos.filter_by(id_producto=producto_id).first()
        if deseo:
            db.session.delete(deseo)
            db.session.commit()
            return True
        return False

    def has_purchased(self, producto_id):
        """Check if user has purchased a product."""
        return self.compras.filter_by(id_producto=producto_id).first() is not None
