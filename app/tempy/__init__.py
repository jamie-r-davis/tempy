from flask import Blueprint

bp = Blueprint("tempy", __name__)

from app.tempy import routes  # isort:skip
