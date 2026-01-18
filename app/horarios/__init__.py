from flask import Blueprint
horarios_bp = Blueprint('horarios', __name__)
from . import routes