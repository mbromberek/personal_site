from app import app


@app.route('/')
@app.route('/index')
def index():
    return "Mike Bromberek Personal Website!"
