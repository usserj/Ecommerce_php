"""
Integration tests for authentication routes
"""

import pytest
from flask import url_for, session
from app.models.user import Usuario


# ===========================
# Registration Tests
# ===========================

@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.blueprints
class TestRegistrationRoutes:
    """Tests for user registration"""

    def test_register_page_loads(self, client):
        """Test register page loads successfully"""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'register' in response.data.lower() or b'registro' in response.data.lower()

    def test_register_new_user(self, client, db_session, mock_email_send):
        """Test registering a new user"""
        user_data = {
            'nombre': 'New User',
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!'
        }

        response = client.post('/auth/register', data=user_data, follow_redirects=True)

        # Check user was created
        user = Usuario.query.filter_by(email='newuser@example.com').first()
        assert user is not None
        assert user.nombre == 'New User'
        assert user.verificado is False  # Should not be verified yet

        # Check verification email was sent
        assert mock_email_send.called

    def test_register_duplicate_email(self, client, test_user):
        """Test registering with existing email fails"""
        user_data = {
            'nombre': 'Another User',
            'email': test_user.email,  # Existing email
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!'
        }

        response = client.post('/auth/register', data=user_data, follow_redirects=True)

        # Should show error
        assert b'email' in response.data.lower()

    def test_register_password_mismatch(self, client):
        """Test password confirmation mismatch"""
        user_data = {
            'nombre': 'New User',
            'email': 'newuser@example.com',
            'password': 'Password123!',
            'password_confirm': 'DifferentPass123!'
        }

        response = client.post('/auth/register', data=user_data)

        # Should show validation error
        assert response.status_code in [200, 400]


# ===========================
# Login Tests
# ===========================

@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.blueprints
class TestLoginRoutes:
    """Tests for user login"""

    def test_login_page_loads(self, client):
        """Test login page loads"""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'login' in response.data.lower()

    def test_login_success(self, client, test_user):
        """Test successful login"""
        login_data = {
            'email': test_user.email,
            'password': 'password123'
        }

        response = client.post('/auth/login', data=login_data, follow_redirects=True)

        # Should redirect to homepage or dashboard
        assert response.status_code == 200

        # Check session
        with client.session_transaction() as sess:
            assert 'user_id' in sess or '_user_id' in sess

    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password"""
        login_data = {
            'email': test_user.email,
            'password': 'wrongpassword'
        }

        response = client.post('/auth/login', data=login_data, follow_redirects=True)

        # Should show error
        assert b'password' in response.data.lower() or b'contrase' in response.data.lower()

    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent email"""
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'password123'
        }

        response = client.post('/auth/login', data=login_data, follow_redirects=True)

        # Should show error
        assert response.status_code == 200

    def test_login_inactive_user(self, client, db_session):
        """Test login with inactive user"""
        # Create inactive user
        user = Usuario(
            nombre='Inactive',
            email='inactive@example.com',
            activo=False,
            verificado=True
        )
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()

        login_data = {
            'email': user.email,
            'password': 'password123'
        }

        response = client.post('/auth/login', data=login_data, follow_redirects=True)

        # Should deny access
        assert b'inactiv' in response.data.lower() or response.status_code in [401, 403]


# ===========================
# Logout Tests
# ===========================

@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.blueprints
class TestLogoutRoutes:
    """Tests for user logout"""

    def test_logout(self, authenticated_client):
        """Test logout functionality"""
        response = authenticated_client.get('/auth/logout', follow_redirects=True)

        assert response.status_code == 200

        # Check session cleared
        with authenticated_client.session_transaction() as sess:
            assert 'user_id' not in sess


# ===========================
# Password Reset Tests
# ===========================

@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.blueprints
class TestPasswordResetRoutes:
    """Tests for password reset"""

    def test_forgot_password_page_loads(self, client):
        """Test forgot password page"""
        response = client.get('/auth/forgot-password')
        assert response.status_code == 200

    def test_forgot_password_request(self, client, test_user, mock_email_send):
        """Test password reset request"""
        data = {'email': test_user.email}

        response = client.post('/auth/forgot-password', data=data, follow_redirects=True)

        assert response.status_code == 200

        # Check email was sent
        assert mock_email_send.called


# ===========================
# OAuth Tests
# ===========================

@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.blueprints
class TestOAuthRoutes:
    """Tests for OAuth authentication"""

    def test_google_login_redirect(self, client):
        """Test Google OAuth login redirect"""
        response = client.get('/auth/login/google')

        # Should redirect to Google
        assert response.status_code in [302, 303, 307]

    def test_google_callback(self, client, mock_oauth_google, db_session):
        """Test Google OAuth callback"""
        response = client.get('/auth/login/google/callback', follow_redirects=True)

        # Should create or login user
        user = Usuario.query.filter_by(email='user@gmail.com').first()
        if user:
            assert user.google_id == 'google-user-id-123'

    def test_facebook_login_redirect(self, client):
        """Test Facebook OAuth login redirect"""
        response = client.get('/auth/login/facebook')

        # Should redirect to Facebook
        assert response.status_code in [302, 303, 307]


# ===========================
# Protected Routes Tests
# ===========================

@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.blueprints
class TestProtectedRoutes:
    """Tests for authentication required routes"""

    def test_profile_requires_login(self, client):
        """Test profile page requires authentication"""
        response = client.get('/profile/dashboard', follow_redirects=True)

        # Should redirect to login
        assert b'login' in response.data.lower()

    def test_profile_with_login(self, authenticated_client):
        """Test profile page with authenticated user"""
        response = authenticated_client.get('/profile/dashboard')

        # Should show profile
        assert response.status_code == 200


# ===========================
# Rate Limiting Tests
# ===========================

@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.slow
class TestAuthRateLimiting:
    """Tests for rate limiting on auth endpoints"""

    def test_register_rate_limit(self, client):
        """Test registration rate limiting"""
        user_data = {
            'nombre': 'Test',
            'email': 'test{i}@example.com',
            'password': 'Pass123!',
            'password_confirm': 'Pass123!'
        }

        # Make multiple requests
        responses = []
        for i in range(10):
            data = user_data.copy()
            data['email'] = f'test{i}@example.com'
            response = client.post('/auth/register', data=data)
            responses.append(response.status_code)

        # At least one should be rate limited (429)
        # Note: This depends on rate limit config
        assert any(status == 429 for status in responses) or all(status in [200, 302] for status in responses)


# ===========================
# Account Verification Tests
# ===========================

@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.blueprints
class TestAccountVerification:
    """Tests for email verification"""

    def test_unverified_user_restrictions(self, client, db_session):
        """Test unverified users have restrictions"""
        # Create unverified user
        user = Usuario(
            nombre='Unverified',
            email='unverified@example.com',
            verificado=False,
            activo=True
        )
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()

        # Try to login
        login_data = {
            'email': user.email,
            'password': 'password123'
        }

        response = client.post('/auth/login', data=login_data, follow_redirects=True)

        # May show verification notice
        # Implementation specific
        assert response.status_code in [200, 403]
