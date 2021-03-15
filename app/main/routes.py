# Custom imports
from app import app
from app.main import bp

@bp.route('/')
@bp.route('/index')
def index():
    return "Mike Bromberek Personal Website!"
