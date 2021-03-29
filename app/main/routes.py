# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# First party classes
from datetime import datetime
# Third party classes
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required

# Custom classes
from app.main import bp
from app.main.forms import EmptyForm, WorkoutForm
from app.models import User, Workout
from app import db

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    # user = {'displayname': 'Mike'}
    workouts = [{'type':'Running', 'duration':'20m 56s', 'distance': '3.11', 'pace': '6m 44s'}, {'type':'Running', 'duration':'3h 35m 53s', 'distance': '26.2', 'pace': '8m 13s'}]

    return render_template('index.html', title='Home Page', workouts=workouts)

@bp.route('/workouts', methods=['GET','POST'])
@login_required
def workouts():
    form = EmptyForm()
    if form.validate_on_submit():
        print("redirect(url_for('main.edit_workout'))")
        return redirect(url_for('main.edit_workout'))

    workouts = [{'type':'Running', 'duration':'20m 56s', 'distance': '3.11', 'pace': '6m 44s'}, {'type':'Running', 'duration':'3h 35m 53s', 'distance': '26.2', 'pace': '8m 13s'}]

    return render_template('workouts.html', title='Workouts', workouts=workouts, form=form)

@bp.route('/edit_workout', methods=['GET','POST'])
@login_required
def edit_workout():
    print("edit_workout")
    form = WorkoutForm()
    if form.validate_on_submit():
        # wrkt_dttm=datetime.strptime(form.dttm.data, '%Y-%m-%d')

        workout = Workout(author=current_user, type=form.type.data, dur_sec=form.duration.data, dist_mi=form.distance.data, notes=form.notes.data, wrkt_dttm=form.dttm.data)
        db.session.add(workout)
        db.session.commit()
        flash('Your workout has been created/updated')
        return redirect(url_for('main.edit_workout'))
    # elif request.method == 'GET':
    #     form.username.data = current_user.username
    #     form.about_me.data = current_user.about_me
    return render_template('edit_workout.html', title='Edit Workout', form=form)
