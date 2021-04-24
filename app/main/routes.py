# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# First party classes
from datetime import datetime
# from datetime import combine

# Third party classes
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required

# Custom classes
from app.main import bp
from app.main.forms import EmptyForm, WorkoutForm
from app.models import User, Workout
from app import db
from app.utils import utils, const
from app import logger

@bp.route('/')
@bp.route('/index')
# @login_required
def index():
    logger.info('index')
    # user = {'displayname': 'Mike'}
    workouts = [{'type':'Running', 'duration':'20m 56s', 'distance': '3.11', 'pace': '6m 44s'}, {'type':'Running', 'duration':'3h 35m 53s', 'distance': '26.2', 'pace': '8m 13s'}]

    return render_template('index.html', title='Home Page', workouts=workouts)

@bp.route('/workouts', methods=['GET','POST'])
@login_required
def workouts():
    logger.info('workouts')
    form = EmptyForm()
    if form.validate_on_submit():
        print("redirect(url_for('main.edit_workout'))")
        return redirect(url_for('main.edit_workout'))

    form.submit.label.text = 'New Workout'

    page = request.args.get('page', 1, type=int)
    workoutPages = \
        Workout.query.filter_by(user_id=current_user.id).order_by(Workout.wrkt_dttm.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = flask.url_for('main.workouts', page=workoutPages.next_num) \
        if workoutPages.has_next else None
    prev_url = flask.url_for('main.workouts', page=workoutPages.prev_num) \
        if workoutPages.has_prev else None

    workouts = workoutPages.items
    for workout in workouts:
        workout.duration = workout.dur_str()
        workout.pace = workout.pace_str()
    return render_template('workouts.html', title='Workouts', workouts=workouts, form=form, next_url=next_url, prev_url=prev_url)

@bp.route('/edit_workout', methods=['GET','POST'])
@login_required
def edit_workout():
    logger.info('edit_workout')
    form = WorkoutForm()
    if form.validate_on_submit():
        duration = utils.time_to_sec(form.duration_h.data, form.duration_m.data, form.duration_s.data)
        wrkt_dttm = datetime.combine(form.wrkt_dt.data, form.wrkt_tm.data)

        workout = Workout(author=current_user, type=form.type.data, dur_sec=duration, dist_mi=form.distance.data, notes=form.notes.data, wrkt_dttm=wrkt_dttm)
        db.session.add(workout)
        db.session.commit()
        flash('Your workout has been created/updated')
        return redirect(url_for('main.workouts'))
    # elif request.method == 'GET':
    #     form.username.data = current_user.username
    #     form.about_me.data = current_user.about_me
    return render_template('edit_workout.html', title='Edit Workout', form=form)
