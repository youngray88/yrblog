from flask import Blueprint

bp = Blueprint('admin',__name__,static_folder='static',template_folder='templates',url_prefix='/admin')

from app.admin import routes