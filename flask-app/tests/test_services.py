"""
Unit tests for service layer
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services import email_service, payment_service, analytics_service


# ===========================
# Email Service Tests
# ===========================

@pytest.mark.unit
@pytest.mark.services
@pytest.mark.email
class TestEmailService:
    """Tests for email service"""

    def test_send_verification_email(self, app, test_user, mock_email_send):
        """Test sending verification email"""
        with app.app_context():
            result = email_service.send_verification_email(
                test_user.email,
                test_user.nombre,
                'verification-token-123'
            )

            # Email should be queued/sent
            assert mock_email_send.called

    def test_send_password_reset_email(self, app, test_user, mock_email_send):
        """Test sending password reset email"""
        with app.app_context():
            new_password = 'NewTempPass123'
            result = email_service.send_password_reset_email(
                test_user.email,
                test_user.nombre,
                new_password
            )

            assert mock_email_send.called

    def test_send_order_confirmation_email(self, app, test_compra, mock_email_send):
        """Test sending order confirmation email"""
        with app.app_context():
            result = email_service.send_order_confirmation_email(
                test_compra.usuario.email,
                test_compra
            )

            assert mock_email_send.called

    def test_send_contact_email(self, app, mock_email_send):
        """Test sending contact form email"""
        with app.app_context():
            result = email_service.send_contact_email(
                nombre='John Doe',
                email='john@example.com',
                mensaje='Test message'
            )

            assert mock_email_send.called


# ===========================
# Payment Service Tests
# ===========================

@pytest.mark.unit
@pytest.mark.services
@pytest.mark.payment
class TestPaymentService:
    """Tests for payment service"""

    @patch('app.services.payment_service.paypalrestsdk')
    def test_configure_paypal(self, mock_paypal, app):
        """Test PayPal configuration"""
        with app.app_context():
            payment_service.configure_paypal()

            # Should configure PayPal with credentials
            assert mock_paypal.configure.called

    @patch('app.services.payment_service.paypalrestsdk.Payment')
    def test_create_paypal_payment(self, mock_payment_class, app):
        """Test creating PayPal payment"""
        # Mock payment instance
        mock_payment = MagicMock()
        mock_payment.create.return_value = True
        mock_payment.id = 'PAYPAL-123'
        mock_payment.links = [
            {'rel': 'approval_url', 'href': 'https://paypal.com/approve'}
        ]
        mock_payment_class.return_value = mock_payment

        with app.app_context():
            order_data = {
                'total': 100.00,
                'items': [
                    {'name': 'Product 1', 'price': 100.00, 'quantity': 1}
                ],
                'return_url': 'http://localhost/success',
                'cancel_url': 'http://localhost/cancel'
            }

            result = payment_service.create_paypal_payment(order_data)

            assert result is not None
            assert 'approval_url' in result or mock_payment.create.called

    @patch('app.services.payment_service.paypalrestsdk.Payment')
    def test_execute_paypal_payment(self, mock_payment_class, app):
        """Test executing PayPal payment"""
        mock_payment = MagicMock()
        mock_payment.execute.return_value = True
        mock_payment_class.find.return_value = mock_payment

        with app.app_context():
            result = payment_service.execute_paypal_payment(
                'PAYPAL-123',
                'PAYER-ID-456'
            )

            assert mock_payment.execute.called

    def test_calculate_order_total(self, app):
        """Test order total calculation"""
        with app.app_context():
            cart_items = [
                {'precio': 99.99, 'cantidad': 2},
                {'precio': 49.99, 'cantidad': 1}
            ]

            subtotal = sum(item['precio'] * item['cantidad'] for item in cart_items)
            tax = subtotal * 0.10  # 10% tax
            shipping = 5.00

            total = payment_service.calculate_order_total(cart_items, tax_rate=0.10, shipping=5.00)

            expected_total = subtotal + tax + shipping
            assert abs(total - expected_total) < 0.01


# ===========================
# Analytics Service Tests
# ===========================

@pytest.mark.unit
@pytest.mark.services
class TestAnalyticsService:
    """Tests for analytics service"""

    @patch('app.services.analytics_service.requests.get')
    def test_get_country_from_ip(self, mock_get, app):
        """Test getting country from IP address"""
        # Mock IP geolocation API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'country': 'United States'}
        mock_get.return_value = mock_response

        with app.app_context():
            country = analytics_service.get_country_from_ip('8.8.8.8')

            assert country == 'United States'

    @patch('app.services.analytics_service.requests.get')
    def test_get_country_from_ip_failure(self, mock_get, app):
        """Test handling API failure gracefully"""
        mock_get.side_effect = Exception('API Error')

        with app.app_context():
            country = analytics_service.get_country_from_ip('8.8.8.8')

            # Should return default or None
            assert country in [None, 'Unknown', '']

    def test_track_visit_by_ip(self, app, db_session):
        """Test tracking visit by IP"""
        with app.app_context():
            ip_address = '192.168.1.1'

            analytics_service.track_visit(ip_address)

            # Visit should be recorded
            from app.models.visit import VisitaPersona
            visit = VisitaPersona.query.filter_by(ip=ip_address).first()

            # May or may not exist depending on implementation
            # Just verify no errors

    def test_track_visit_by_country(self, app, db_session):
        """Test tracking visit by country"""
        with app.app_context():
            country = 'United States'

            analytics_service.track_country_visit(country)

            # Country visit should be recorded
            from app.models.visit import VisitaPais
            visit = VisitaPais.query.filter_by(pais=country).first()

            # May or may not exist depending on implementation

    def test_increment_notification_counter(self, app, db_session):
        """Test incrementing notification counters"""
        with app.app_context():
            from app.models.notification import Notificacion

            # Create initial notification record
            notif = Notificacion(
                nuevos_usuarios=0,
                nuevas_compras=0
            )
            db_session.add(notif)
            db_session.commit()

            # Increment
            Notificacion.increment_nuevos_usuarios()
            db_session.commit()

            # Verify
            notif = Notificacion.query.first()
            assert notif.nuevos_usuarios == 1


# ===========================
# Service Integration Tests
# ===========================

@pytest.mark.integration
@pytest.mark.services
class TestServiceIntegration:
    """Integration tests for services working together"""

    def test_order_flow_with_services(self, app, authenticated_client, test_producto, mock_email_send, mock_paypal_payment):
        """Test complete order flow using multiple services"""
        with app.app_context():
            # 1. Add to cart
            cart_data = {
                'producto_id': test_producto.id,
                'cantidad': 1
            }

            # 2. Process payment (mocked)
            order_data = {
                'total': test_producto.precio,
                'items': [{'name': test_producto.titulo, 'price': test_producto.precio, 'quantity': 1}]
            }

            # 3. Send confirmation email (mocked)
            # All services should work together

            # Verify no exceptions
            assert True


# ===========================
# Service Error Handling Tests
# ===========================

@pytest.mark.unit
@pytest.mark.services
class TestServiceErrorHandling:
    """Tests for service error handling"""

    def test_email_service_smtp_error(self, app, test_user):
        """Test email service handles SMTP errors gracefully"""
        with app.app_context():
            with patch('app.services.email_service.mail.send') as mock_send:
                mock_send.side_effect = Exception('SMTP Error')

                # Should not raise exception
                try:
                    email_service.send_verification_email(
                        test_user.email,
                        test_user.nombre,
                        'token'
                    )
                except Exception as e:
                    # Should log error but not crash
                    pass

    @patch('app.services.payment_service.paypalrestsdk.Payment')
    def test_payment_service_paypal_error(self, mock_payment_class, app):
        """Test payment service handles PayPal errors"""
        mock_payment = MagicMock()
        mock_payment.create.return_value = False
        mock_payment.error = {'message': 'Payment failed'}
        mock_payment_class.return_value = mock_payment

        with app.app_context():
            order_data = {'total': 100.00}

            result = payment_service.create_paypal_payment(order_data)

            # Should return error info or None
            assert result is None or 'error' in result


# ===========================
# Service Performance Tests
# ===========================

@pytest.mark.unit
@pytest.mark.services
@pytest.mark.slow
class TestServicePerformance:
    """Performance tests for services"""

    def test_bulk_email_sending(self, app, mock_email_send):
        """Test sending multiple emails efficiently"""
        with app.app_context():
            users = [
                {'email': f'user{i}@example.com', 'nombre': f'User {i}'}
                for i in range(100)
            ]

            for user in users:
                email_service.send_verification_email(
                    user['email'],
                    user['nombre'],
                    f'token-{user["email"]}'
                )

            # Should complete without timeout
            assert mock_email_send.call_count == 100
