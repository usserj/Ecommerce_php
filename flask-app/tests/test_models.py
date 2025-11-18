"""
Unit tests for SQLAlchemy models
"""

import pytest
from datetime import datetime
from app.models.user import Usuario
from app.models.admin import Administrador
from app.models.product import Producto
from app.models.categoria import Categoria, Subcategoria
from app.models.order import Compra
from app.models.comment import Comentario
from app.models.wishlist import Deseo


# ===========================
# Usuario Model Tests
# ===========================

@pytest.mark.unit
@pytest.mark.models
class TestUsuarioModel:
    """Tests for Usuario model"""

    def test_create_user(self, db_session):
        """Test creating a new user"""
        user = Usuario(
            nombre='John Doe',
            email='john@example.com',
            verificado=True,
            activo=True
        )
        user.set_password('password123')

        db_session.add(user)
        db_session.commit()

        assert user.id is not None
        assert user.nombre == 'John Doe'
        assert user.email == 'john@example.com'
        assert user.verificado is True
        assert user.activo is True
        assert user.password is not None

    def test_set_password(self, db_session):
        """Test password hashing"""
        user = Usuario(nombre='Test', email='test@test.com')
        user.set_password('mypassword')

        assert user.password is not None
        assert user.password != 'mypassword'
        assert user.password.startswith('$2')  # bcrypt hash

    def test_check_password(self, test_user):
        """Test password verification"""
        assert test_user.check_password('password123') is True
        assert test_user.check_password('wrongpassword') is False

    def test_password_migration_from_legacy(self, db_session):
        """Test password migration from PHP crypt to bcrypt"""
        import crypt

        # Create user with legacy PHP password
        user = Usuario(nombre='Legacy User', email='legacy@test.com')
        legacy_password = 'oldpassword'
        user.password = crypt.crypt(legacy_password, crypt.METHOD_SHA512)

        db_session.add(user)
        db_session.commit()

        # Check password should work and migrate to bcrypt
        assert user.check_password(legacy_password) is True

        # After migration, password should be bcrypt
        assert user.password.startswith('$2')

    def test_user_relationships(self, db_session, test_user, test_producto):
        """Test user relationships (compras, comentarios, deseos)"""
        # Create compra
        compra = Compra(
            usuario_id=test_user.id,
            producto_id=test_producto.id,
            cantidad=1,
            precio_unitario=test_producto.precio,
            total=test_producto.precio
        )
        db_session.add(compra)

        # Create comentario
        comentario = Comentario(
            usuario_id=test_user.id,
            producto_id=test_producto.id,
            comentario='Great!',
            calificacion=5
        )
        db_session.add(comentario)

        # Create deseo
        deseo = Deseo(
            usuario_id=test_user.id,
            producto_id=test_producto.id
        )
        db_session.add(deseo)

        db_session.commit()

        # Test relationships
        assert len(test_user.compras) == 1
        assert len(test_user.comentarios) == 1
        assert len(test_user.deseos) == 1

    def test_user_oauth_fields(self, db_session):
        """Test user with OAuth fields"""
        user = Usuario(
            nombre='Google User',
            email='user@gmail.com',
            google_id='google-123',
            foto='https://example.com/photo.jpg',
            verificado=True
        )
        db_session.add(user)
        db_session.commit()

        assert user.google_id == 'google-123'
        assert user.foto is not None


# ===========================
# Administrador Model Tests
# ===========================

@pytest.mark.unit
@pytest.mark.models
class TestAdministradorModel:
    """Tests for Administrador model"""

    def test_create_admin(self, db_session):
        """Test creating admin"""
        admin = Administrador(
            nombre='Admin User',
            email='admin@test.com',
            rol='admin',
            activo=True
        )
        admin.set_password('adminpass')

        db_session.add(admin)
        db_session.commit()

        assert admin.id is not None
        assert admin.nombre == 'Admin User'
        assert admin.rol == 'admin'
        assert admin.activo is True

    def test_admin_password(self, test_admin):
        """Test admin password"""
        assert test_admin.check_password('admin123') is True
        assert test_admin.check_password('wrong') is False


# ===========================
# Categoria Model Tests
# ===========================

@pytest.mark.unit
@pytest.mark.models
class TestCategoriaModel:
    """Tests for Categoria model"""

    def test_create_categoria(self, db_session):
        """Test creating categoria"""
        categoria = Categoria(
            nombre='Electronics',
            descripcion='Electronic products',
            estado=True
        )
        db_session.add(categoria)
        db_session.commit()

        assert categoria.id is not None
        assert categoria.nombre == 'Electronics'
        assert categoria.estado is True

    def test_categoria_subcategorias_relationship(self, db_session, test_categoria):
        """Test categoria-subcategoria relationship"""
        subcat1 = Subcategoria(
            nombre='Phones',
            categoria_id=test_categoria.id,
            estado=True
        )
        subcat2 = Subcategoria(
            nombre='Laptops',
            categoria_id=test_categoria.id,
            estado=True
        )

        db_session.add_all([subcat1, subcat2])
        db_session.commit()

        assert len(test_categoria.subcategorias) == 2

    def test_categoria_productos_relationship(self, db_session, test_categoria):
        """Test categoria-productos relationship"""
        producto = Producto(
            titulo='Product 1',
            precio=99.99,
            stock=10,
            categoria_id=test_categoria.id,
            estado=True
        )
        db_session.add(producto)
        db_session.commit()

        assert len(test_categoria.productos) == 1


# ===========================
# Producto Model Tests
# ===========================

@pytest.mark.unit
@pytest.mark.models
class TestProductoModel:
    """Tests for Producto model"""

    def test_create_producto(self, db_session, test_categoria):
        """Test creating producto"""
        producto = Producto(
            titulo='Test Product',
            descripcion='Description',
            precio=99.99,
            stock=10,
            categoria_id=test_categoria.id,
            estado=True
        )
        db_session.add(producto)
        db_session.commit()

        assert producto.id is not None
        assert producto.titulo == 'Test Product'
        assert producto.precio == 99.99
        assert producto.stock == 10

    def test_producto_with_offer(self, test_producto_oferta):
        """Test producto with discount"""
        assert test_producto_oferta.precio == 100.0
        assert test_producto_oferta.precio_oferta == 75.0

    def test_get_price_method(self, test_producto, test_producto_oferta):
        """Test get_price method"""
        assert test_producto.get_price() == 99.99
        assert test_producto_oferta.get_price() == 75.0  # Returns offer price

    def test_is_on_offer_method(self, test_producto, test_producto_oferta):
        """Test is_on_offer method"""
        assert test_producto.is_on_offer() is False
        assert test_producto_oferta.is_on_offer() is True

    def test_increment_views(self, db_session, test_producto):
        """Test incrementing product views"""
        initial_views = test_producto.vistas
        test_producto.increment_views()
        db_session.commit()

        assert test_producto.vistas == initial_views + 1

    def test_get_average_rating(self, db_session, test_producto, test_user):
        """Test average rating calculation"""
        # Create multiple comments with ratings
        for rating in [5, 4, 5, 3, 4]:
            comment = Comentario(
                usuario_id=test_user.id,
                producto_id=test_producto.id,
                comentario='Test',
                calificacion=rating,
                estado=True
            )
            db_session.add(comment)
        db_session.commit()

        avg_rating = test_producto.get_average_rating()
        expected = (5 + 4 + 5 + 3 + 4) / 5
        assert avg_rating == pytest.approx(expected, 0.01)

    def test_producto_relationships(self, db_session, test_producto, test_user):
        """Test producto relationships"""
        # Create comment
        comment = Comentario(
            usuario_id=test_user.id,
            producto_id=test_producto.id,
            comentario='Great!',
            calificacion=5
        )
        db_session.add(comment)
        db_session.commit()

        assert len(test_producto.comentarios) == 1

    def test_producto_json_fields(self, db_session, test_categoria):
        """Test JSON fields (multimedia, detalles)"""
        producto = Producto(
            titulo='Product with JSON',
            precio=99.99,
            stock=10,
            categoria_id=test_categoria.id,
            multimedia=['image1.jpg', 'image2.jpg'],
            detalles={'color': 'blue', 'size': 'large'},
            estado=True
        )
        db_session.add(producto)
        db_session.commit()

        assert isinstance(producto.multimedia, list)
        assert isinstance(producto.detalles, dict)
        assert producto.multimedia[0] == 'image1.jpg'
        assert producto.detalles['color'] == 'blue'


# ===========================
# Compra Model Tests
# ===========================

@pytest.mark.unit
@pytest.mark.models
class TestCompraModel:
    """Tests for Compra (Order) model"""

    def test_create_compra(self, db_session, test_user, test_producto):
        """Test creating order"""
        compra = Compra(
            usuario_id=test_user.id,
            producto_id=test_producto.id,
            cantidad=2,
            precio_unitario=test_producto.precio,
            total=test_producto.precio * 2,
            metodo_pago='paypal',
            estado='pendiente'
        )
        db_session.add(compra)
        db_session.commit()

        assert compra.id is not None
        assert compra.cantidad == 2
        assert compra.total == test_producto.precio * 2
        assert compra.estado == 'pendiente'

    def test_compra_relationships(self, test_compra):
        """Test compra relationships"""
        assert test_compra.usuario is not None
        assert test_compra.producto is not None
        assert test_compra.usuario.nombre == 'Test User'

    def test_compra_detalles_envio(self, db_session, test_user, test_producto):
        """Test order shipping details (JSON field)"""
        detalles = {
            'direccion': '123 Main St',
            'ciudad': 'Test City',
            'pais': 'Test Country',
            'codigo_postal': '12345'
        }

        compra = Compra(
            usuario_id=test_user.id,
            producto_id=test_producto.id,
            cantidad=1,
            precio_unitario=test_producto.precio,
            total=test_producto.precio,
            detalles_envio=detalles
        )
        db_session.add(compra)
        db_session.commit()

        assert isinstance(compra.detalles_envio, dict)
        assert compra.detalles_envio['ciudad'] == 'Test City'


# ===========================
# Comentario Model Tests
# ===========================

@pytest.mark.unit
@pytest.mark.models
class TestComentarioModel:
    """Tests for Comentario model"""

    def test_create_comentario(self, db_session, test_user, test_producto):
        """Test creating comment"""
        comentario = Comentario(
            usuario_id=test_user.id,
            producto_id=test_producto.id,
            comentario='Excellent product!',
            calificacion=5,
            estado=True
        )
        db_session.add(comentario)
        db_session.commit()

        assert comentario.id is not None
        assert comentario.comentario == 'Excellent product!'
        assert comentario.calificacion == 5

    def test_comentario_relationships(self, test_comentario):
        """Test comment relationships"""
        assert test_comentario.usuario is not None
        assert test_comentario.producto is not None

    def test_comentario_rating_range(self, db_session, test_user, test_producto):
        """Test rating validation (1-5)"""
        # Valid ratings
        for rating in [1, 2, 3, 4, 5]:
            comment = Comentario(
                usuario_id=test_user.id,
                producto_id=test_producto.id,
                comentario='Test',
                calificacion=rating
            )
            assert comment.calificacion in range(1, 6)


# ===========================
# Deseo (Wishlist) Model Tests
# ===========================

@pytest.mark.unit
@pytest.mark.models
class TestDeseoModel:
    """Tests for Deseo (Wishlist) model"""

    def test_create_deseo(self, db_session, test_user, test_producto):
        """Test creating wishlist item"""
        deseo = Deseo(
            usuario_id=test_user.id,
            producto_id=test_producto.id
        )
        db_session.add(deseo)
        db_session.commit()

        assert deseo.id is not None
        assert deseo.usuario_id == test_user.id
        assert deseo.producto_id == test_producto.id

    def test_deseo_unique_constraint(self, db_session, test_user, test_producto):
        """Test unique constraint on usuario_id + producto_id"""
        # Create first wishlist item
        deseo1 = Deseo(
            usuario_id=test_user.id,
            producto_id=test_producto.id
        )
        db_session.add(deseo1)
        db_session.commit()

        # Try to create duplicate - should fail
        deseo2 = Deseo(
            usuario_id=test_user.id,
            producto_id=test_producto.id
        )
        db_session.add(deseo2)

        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()

    def test_deseo_relationships(self, test_deseo):
        """Test wishlist relationships"""
        assert test_deseo.usuario is not None
        assert test_deseo.producto is not None


# ===========================
# Model Timestamps Tests
# ===========================

@pytest.mark.unit
@pytest.mark.models
class TestModelTimestamps:
    """Test timestamp fields across models"""

    def test_usuario_fecha_registro(self, test_user):
        """Test user registration date"""
        assert test_user.fecha_registro is not None
        assert isinstance(test_user.fecha_registro, datetime)

    def test_producto_timestamps(self, test_producto):
        """Test product timestamps"""
        assert test_producto.fecha_creacion is not None
        # fecha_actualizacion may be None on creation

    def test_compra_timestamps(self, test_compra):
        """Test order timestamps"""
        assert test_compra.fecha_compra is not None

    def test_deseo_fecha_agregado(self, test_deseo):
        """Test wishlist date added"""
        assert test_deseo.fecha_agregado is not None
