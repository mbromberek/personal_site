# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# Third party imports
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app

# Custom imports
from app import app
from app.main import bp

@bp.route('/')
@bp.route('/index')
def index():
    user = {'displayname': 'Mike'}
    workouts = [{'type':'Running', 'duration':'20m 56s', 'distance': '3.11', 'pace': '6m 44s'}]
    result = '''
<html>
    <head>
        <title>Home Page - Mike Bromberek</title>
    </head>
    <body>
        <h1>Hello, ''' + user['displayname'] + '''!</h1>
    </body>
</html>'''

    return render_template('index.html', title='Home Page', user=user, workouts=workouts)
