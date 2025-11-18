"""Analytics and visit tracking service."""
from flask import request
from app.models.visit import VisitaPais, VisitaPersona
from app.models.notification import Notificacion
import requests


def get_country_from_ip(ip):
    """Get country from IP address using external API."""
    try:
        # Using ipapi.co (free tier)
        response = requests.get(f'https://ipapi.co/{ip}/json/', timeout=2)
        if response.status_code == 200:
            data = response.json()
            return {
                'country': data.get('country_name', 'Unknown'),
                'code': data.get('country_code', 'XX')
            }
    except Exception:
        pass

    return {'country': 'Unknown', 'code': 'XX'}


def track_visit(ip):
    """Track visitor."""
    if not ip or ip == '127.0.0.1':
        return

    # Get country info
    country_info = get_country_from_ip(ip)

    # Track by IP
    VisitaPersona.track_visit(ip, country_info['country'])

    # Track by country
    VisitaPais.increment_visit(country_info['country'], country_info['code'])

    # Update notifications (every 10 visits)
    total_visits = VisitaPersona.get_total_visits()
    if total_visits % 10 == 0:
        Notificacion.increment_new_visits()
