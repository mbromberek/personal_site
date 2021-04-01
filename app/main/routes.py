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

    form.submit.label.text = 'New Workout'
    # workouts = [{'type':'Running', 'duration':'20m 56s', 'distance': '3.11', 'pace': '6m 44s'}, {'type':'Running', 'duration':'3h 35m 53s', 'distance': '26.2', 'pace': '8m 13s'}]

    page = request.args.get('page', 1, type=int)
    workouts = Workout.query.order_by(Workout.wrkt_dttm.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = flask.url_for('main.workouts', page=workouts.next_num) \
        if workouts.has_next else None
    prev_url = flask.url_for('main.workouts', page=workouts.prev_num) \
        if workouts.has_prev else None

    return render_template('workouts.html', title='Workouts', workouts=workouts.items, form=form, next_url=next_url, prev_url=prev_url)

@bp.route('/edit_workout', methods=['GET','POST'])
@login_required
def edit_workout():
    print('edit_workout')
    form = WorkoutForm()
    if form.validate_on_submit():
        duration = utils.time_to_sec(form.duration_h.data, form.duration_m.data, form.duration_s.data)
        print("Duration: " + str(duration))
        wrkt_dttm = datetime.combine(form.wrkt_dt.data, form.wrkt_tm.data)
        print("wrkt_dt: " + str(form.wrkt_dt.data))
        print("wrkt_tm: " + str(form.wrkt_tm.data))
        print("wrkt_dttm: " + str(wrkt_dttm))

        workout = Workout(author=current_user, type=form.type.data, dur_sec=duration, dist_mi=form.distance.data, notes=form.notes.data, wrkt_dttm=wrkt_dttm)
        db.session.add(workout)
        db.session.commit()
        flash('Your workout has been created/updated')
        return redirect(url_for('main.workouts'))
    # elif request.method == 'GET':
    #     form.username.data = current_user.username
    #     form.about_me.data = current_user.about_me
    return render_template('edit_workout.html', title='Edit Workout', form=form)
