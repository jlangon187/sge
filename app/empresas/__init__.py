from flask import Blueprint
empresas_bp = Blueprint('empresas', __name__)
from . import routes