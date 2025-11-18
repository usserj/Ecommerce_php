"""
Health check endpoints for monitoring
"""

from flask import Blueprint, jsonify
from app.extensions import db
from datetime import datetime
import os

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for load balancers and monitoring

    Returns:
        JSON response with health status
    """
    try:
        # Check database connection
        db.session.execute('SELECT 1')

        health_status = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'flask-ecommerce',
            'version': os.getenv('APP_VERSION', '1.0.0'),
            'checks': {
                'database': 'ok',
                'application': 'ok'
            }
        }

        return jsonify(health_status), 200

    except Exception as e:
        health_status = {
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'flask-ecommerce',
            'error': str(e),
            'checks': {
                'database': 'failed',
                'application': 'ok'
            }
        }

        return jsonify(health_status), 503


@health_bp.route('/health/ready', methods=['GET'])
def readiness_check():
    """
    Readiness check - verifies if app is ready to receive traffic
    """
    try:
        # Check database
        db.session.execute('SELECT 1')

        # Add more checks as needed (Redis, external APIs, etc.)

        return jsonify({
            'status': 'ready',
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    except:
        return jsonify({
            'status': 'not ready',
            'timestamp': datetime.utcnow().isoformat()
        }), 503


@health_bp.route('/health/live', methods=['GET'])
def liveness_check():
    """
    Liveness check - verifies if app is alive
    """
    return jsonify({
        'status': 'alive',
        'timestamp': datetime.utcnow().isoformat()
    }), 200
