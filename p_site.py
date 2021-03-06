# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# Custom classes
from app import create_app, db
from app.models import User, Workout, Gear, Gear_usage
from app.utils import tm_conv

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Workout': Workout, 'utils': tm_conv, 'Gear': Gear, 'Gear_usage': Gear_usage}
