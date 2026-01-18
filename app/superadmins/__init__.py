from flask import Blueprint

superadmins_bp = Blueprint('superadmins', __name__)

from . import routes