"""User model."""
import crypt
import hashlib
from datetime import datetime
from flask_login import UserMixin
from app.extensions import db, bcrypt


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
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    compras = db.relationship('Compra', backref='usuario', lazy='dynamic', cascade='all, delete-orphan')
    comentarios = db.relationship('Comentario', backref='usuario', lazy='dynamic', cascade='all, delete-orphan')
    deseos = db.relationship('Deseo', backref='usuario', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.email}>'

    def set_password(self, password):
        """Set password hash using bcrypt."""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Check password against hash.

        Supports both legacy PHP crypt() hashes and new bcrypt hashes.
        """
        if not self.password:
            return False

        # Check if it's a bcrypt hash (starts with $2a$, $2b$, or $2y$)
        if self.password.startswith(('$2a$', '$2b$', '$2y$')):
            return bcrypt.check_password_hash(self.password, password)

        # Legacy PHP crypt() support
        try:
            return self.password == crypt.crypt(password, self.password)
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

    def is_verified(self):
        """Check if user email is verified."""
        return self.verificacion == 0

    def get_orders(self):
        """Get user's orders."""
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
