"""Shop blueprint."""
from flask import Blueprint

shop_bp = Blueprint('shop', __name__)

from app.blueprints.shop import routes  # noqa
