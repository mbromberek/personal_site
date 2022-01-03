# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# First party classes
from datetime import datetime, timedelta, date
# from datetime import combine

# Third party classes
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app, send_file
from flask_login import current_user, login_required
from sqlalchemy import or_
import pandas as pd

# Custom classes
from app.main import bp
from app.main.forms import EmptyForm, WorkoutCreateBtnForm, WorkoutForm, WorkoutFilterForm, WorkoutIntervalForm, WorkoutExportForm
from app.models import User, Workout, Workout_interval, Gear_usage, Wrkt_sum, Wkly_mileage, Yrly_mileage
from app import db
from app.utils import tm_conv, const, nbrConv, dt_conv
from app import logger
from app.utils import wrkt_summary
from app.main import export, filtering

@bp.route('/')
@bp.route('/index')
# @login_required
def index():
    logger.info('index')
    # user = {'displayname': 'Mike'}
    # workouts = [{'type':'Running', 'duration':'20m 56s', 'distance': '3.11', 'pace': '6m 44s'}, {'type':'Running', 'duration':'3h 35m 53s', 'distance': '26.2', 'pace': '8m 13s'}]

    dash_lst_dict = {}

    # min_yrly_dt = datetime(date.today().year, 1, 1)
    min_yrly_dt = datetime(2021, 1, 1)
    query = Yrly_mileage.query.filter_by(user_id=1)
    query = query.filter(Yrly_mileage.type.in_(['Running','Cycling']))
    query = query.filter(Yrly_mileage.dt_by_yr >=min_yrly_dt)
    yrly_mileage_results = sorted(query, reverse=True)
    yrly_mileage_lst = []
    for yr_mileage in yrly_mileage_results:
        yr_mileage.duration = yr_mileage.dur_str()
        yr_mileage.pace = yr_mileage.pace_str()
        yrly_mileage_lst.append(yr_mileage)
    dash_lst_dict['yrly_mileage_lst'] = yrly_mileage_lst

    wrkt_sum_results = Wrkt_sum.query.filter_by(user_id=1, type='Running')
    wrkt_sum_lst = []
    for wrkt_sum in wrkt_sum_results:
        wrkt_sum.duration = wrkt_sum.dur_str()
        i = getInsertPoint(wrkt_sum, wrkt_sum_lst)
        wrkt_sum_lst.insert(i,wrkt_sum)
    dash_lst_dict['wrkt_sum_lst'] = wrkt_sum_lst

    return render_template('index.html', title='Home Page', dash_lst_dict=dash_lst_dict, destPage='home')

@bp.route('/workouts', methods=['GET','POST'])
@login_required
def workouts():
    logger.info('workouts')
    wrktCreateBtn = WorkoutCreateBtnForm()
    wrkt_filter_form = WorkoutFilterForm()
    wrkt_export_form = WorkoutExportForm()

    # if wrkt_export_form.download_csv_btn.data:
        # logger.debug("download csv button popover pressed")

    # if New Workout button was pressed
    if wrktCreateBtn.workt_create_btn.data:
        logger.debug('Create Workout Pressed')
        return redirect(url_for('main.edit_workout'))

    url_change = False
    usingSearch = False
    filterValFromPost = {}
    filterValFromUrl = filtering.getFilterValuesFromUrl()

    if wrkt_filter_form.submit_search_btn.data:
        logger.debug('Search Submit Pressed')
        usingSearch=True
        url_change = True
        filterValFromPost = filtering.getFilterValuesFromPost(wrkt_filter_form)
        filterVal = filterValFromPost
        filterVal['type'] = filterValFromUrl['type']
        filterVal['category'] = filterValFromUrl['category']
    else:
        filterVal = filterValFromUrl

    # Redirect if type button was pressed
    if wrkt_filter_form.category_run_btn.data:
        logger.debug('Run Type Pressed')
        url_change = True
        filterVal['type'] = 'run'
    elif wrkt_filter_form.category_cycle_btn.data:
        logger.debug('Cycle Type Pressed')
        url_change = True
        filterVal['type'] = 'cycle'
    elif wrkt_filter_form.category_swim_btn.data:
        logger.debug('Swim Type Pressed')
        url_change = True
        filterVal['type']='swim'

    # Redirect if category button was pressed
    if wrkt_filter_form.category_training_btn.data:
        url_change = True
        filterVal['category']='training'
    elif wrkt_filter_form.category_long_btn.data:
        url_change = True
        filterVal['category'] = 'long'
    elif wrkt_filter_form.category_easy_btn.data:
        url_change = True
        filterVal['category'] = 'easy'
    elif wrkt_filter_form.category_race_btn.data:
        url_change = True
        filterVal['category'] = 'race'

    # Redirect if Clear button was pressed
    if wrkt_filter_form.clear_filter_btn.data:
        logger.debug('Clear Pressed')
        return redirect(url_for('main.workouts'))

    if url_change:
        if filterVal['strt_dt'] == '' or filterVal['strt_dt'] == None:
            strt_dt_str = ''
        elif isinstance(filterVal['strt_dt'], datetime):
            strt_dt_str = filterVal['strt_dt'].strftime('%Y-%m-%d')
        else:
            strt_dt_str = filterVal['strt_dt']

        if filterVal['end_dt'] == '' or filterVal['end_dt'] == None:
            end_dt_str = ''
        elif isinstance(filterVal['end_dt'], datetime):
            end_dt_str = filterVal['end_dt'].strftime('%Y-%m-%d')
        else:
            end_dt_str = filterVal['end_dt']

        return redirect(url_for('main.workouts', page=1, type=filterVal['type'], category=filterVal['category'], temperature=filterVal['temperature'], distance=filterVal['distance'], text_search=filterVal['txt_search'], min_strt_temp=filterVal['min_strt_temp'], max_strt_temp=filterVal['max_strt_temp'], min_dist=filterVal['min_dist'], max_dist=filterVal['max_dist'],
        strt_dt=strt_dt_str,
        end_dt=end_dt_str   ))

    type_filter = []
    category_filter = []
    btn_classes = {}
    if filterVal['type'] == 'run':
        type_filter.extend(['Running','Indoor Running'])
        # run_btn_class = 'btn btn-primary'
        btn_classes['run'] = 'btn btn-primary'
    if filterVal['type'] == 'cycle':
        type_filter.extend(['Cycling','Indoor Cycling'])
        btn_classes['cycle'] = 'btn btn-primary'
    if filterVal['type'] == 'swim':
        type_filter.extend(['Swimming','Indoor Swimming'])
        btn_classes['swim'] = 'btn btn-primary'

    if filterVal['category'] == 'training':
        category_filter.extend(['Training', 'Hard'])
        # run_btn_class = 'btn btn-primary'
        btn_classes['training'] = 'btn btn-primary'
    if filterVal['category'] == 'long':
        category_filter.extend(['Long Run', 'Long'])
        btn_classes['long'] = 'btn btn-primary'
    if filterVal['category'] == 'easy':
        category_filter.extend(['Easy'])
        btn_classes['easy'] = 'btn btn-primary'
    if filterVal['category'] == 'race':
        category_filter.extend(['Race', 'Virtual Race'])
        btn_classes['race'] = 'btn btn-primary'

    logger.info('type_filter ' + str(type_filter))

    query, usingSearch = filtering.get_workouts_from_filter(current_user.id, type_filter, category_filter, filterVal, wrkt_filter_form)

    if wrkt_export_form.download_csv_btn.data:
        logger.debug('Export as CSV Pressed')
        query = query.order_by(Workout.wrkt_dttm.desc())
        if wrkt_export_form.max_export_records.data != None:
            workout_list = query.paginate(0,wrkt_export_form.max_export_records.data, False).items
        else:
            workout_list = query.all()
        # field_lst = ['Date','Type','Duration','Distance','Pace', 'Notes+', 'Category','Gear','Elevation','HR','Calories']
        export_file = export.wrkt_lst_to_csv(workout_list, wrkt_export_form)

        export_file_nm = 'workouts.export.' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.csv'

        return send_file(export_file, as_attachment=True, mimetype='text/csv', attachment_filename=export_file_nm)


    workoutPages = query.order_by(Workout.wrkt_dttm.desc()).paginate(filterVal['page'], current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.workouts', page=workoutPages.next_num, type=filterVal['type'], category=filterVal['category'], temperature=filterVal['temperature'], distance=filterVal['distance'], text_search=filterVal['txt_search'], min_strt_temp=filterVal['min_strt_temp'], max_strt_temp=filterVal['max_strt_temp'], min_dist=filterVal['min_dist'], max_dist=filterVal['max_dist'], strt_dt=filterVal['strt_dt'],
    end_dt=filterVal['end_dt'] ) \
        if workoutPages.has_next else None
    prev_url = url_for('main.workouts', page=workoutPages.prev_num, type=filterVal['type'], category=filterVal['category'], temperature=filterVal['temperature'], distance=filterVal['distance'], text_search=filterVal['txt_search'], min_strt_temp=filterVal['min_strt_temp'], max_strt_temp=filterVal['max_strt_temp'], min_dist=filterVal['min_dist'], max_dist=filterVal['max_dist'], strt_dt=filterVal['strt_dt'],
    end_dt=filterVal['end_dt']) \
        if workoutPages.has_prev else None

    workouts = workoutPages.items
    for workout in workouts:
        workout.duration = workout.dur_str()
        workout.pace = workout.pace_str()
        if workout.clothes == None:
            workout.clothes = ''
        if workout.notes != None:
            workout.notes_summary = workout.notes[:current_app.config['SIZE_NOTES_SUMMARY']] + '...' if len(workout.notes) > current_app.config['SIZE_NOTES_SUMMARY'] else workout.notes
            # workout.notes_summmary = workout.notes
        else:
            workout.notes_summary = ""
    return render_template('workouts.html', title='Workouts', workouts=workouts, form=wrktCreateBtn, wrkt_filter_form=wrkt_filter_form, btn_classes=btn_classes, next_url=next_url, prev_url=prev_url, using_search=usingSearch, destPage='search', wrkt_export_form=wrkt_export_form)

@bp.route('/edit_workout', methods=['GET','POST'])
@login_required
def edit_workout():
    logger.info('edit_workout: ' + str(request.args.get('workout')))
    form = WorkoutForm()

    gear_lst = sorted(Gear_usage.query.filter_by(user_id=current_user.id), reverse=True)
    gear_select_lst = []
    for g in gear_lst:
        gear_select_lst.append([g.gear_id, g.nm])
    form.gear_lst.choices = gear_select_lst

    label_val = {}
    usr_id = current_user.id

    logger.debug("Request Method: " + request.method)
    # logger.debug("Request Args workout: " + request.args.get('workout'))
    logger.debug("Workout ID: " + str(form.wrkt_id.data))

    if form.wrkt_id.data == None or form.wrkt_id.data == "":
        logger.info('Create Workout')
        label_val['title'] = 'Create Workout'
    else:
        logger.info('Update Workout')
        logger.info(form.wrkt_id.data)
        label_val['title'] = 'Update Workout'
        del form.wrkt_dt

    if form.cancel.data:
        logger.debug('cancel')
        return redirect(url_for('main.workouts'))
    if form.edit_interval.data:
        logger.debug('edit_interval')
        return redirect(url_for('main.edit_workout_interval', workout=form.wrkt_id.data))
    if form.delete_btn.data:
        wrkt_id = form.wrkt_id.data
        logger.debug('delete workout: ' + str(wrkt_id) + ' for user ' + str(usr_id))
        wrktIntrvlLst = Workout_interval.query.filter_by(id=wrkt_id, user_id=usr_id)
        for wrktIntrvl in wrktIntrvlLst:
            db.session.delete(wrktIntrvl)
        wrkt = Workout.query.filter_by(id=wrkt_id, user_id = usr_id).one()
        db.session.delete(wrkt)
        db.session.commit()
        flash("Workout Deleted")
        return redirect(url_for('main.workouts'))
    if form.validate_on_submit():
        logger.debug('validate_on_submit')
        if form.wrkt_id.data == "":
            logger.info('new workout')
            duration = tm_conv.time_to_sec(form.duration_h.data, form.duration_m.data, form.duration_s.data)
            logger.info(form.wrkt_dt)
            logger.info(form.wrkt_tm)
            wrkt_dttm = datetime.combine(form.wrkt_dt.data, form.wrkt_tm.data)
            wrkt = Workout(author=current_user, wrkt_dttm=wrkt_dttm)
        else:
            logger.info('update workout')
            # usr_id = current_user.id
            wrkt_id = form.wrkt_id.data
            wrkt = Workout.query.filter_by(id=wrkt_id, user_id=usr_id).first_or_404(id)
        wrkt.dur_sec = tm_conv.time_to_sec(form.duration_h.data, form.duration_m.data, form.duration_s.data)
        wrkt.type = form.type.data
        wrkt.dist_mi = form.distance.data
        wrkt.notes = form.notes.data

        # wrkt.gear = form.gear.data
        wrkt.gear_id = form.gear_lst.data
        wrkt.clothes = form.clothes.data
        wrkt.ele_up = form.ele_up.data
        wrkt.ele_down = form.ele_down.data
        wrkt.hr = form.hr.data
        wrkt.cal_burn = form.cal_burn.data
        wrkt.category = form.category.data
        wrkt.location = form.location.data
        wrkt.training_type = form.training_type.data

        wrkt.temp_strt = form.temp_strt.data
        wrkt.dew_point_strt = form.dew_point_strt.data
        wrkt.temp_feels_like_strt = form.temp_feels_like_strt.data
        wrkt.wethr_cond_strt = form.wethr_cond_strt.data
        wrkt.hmdty_strt = form.hmdty_strt.data
        wrkt.wind_speed_strt = form.wind_speed_strt.data
        wrkt.wind_gust_strt = form.wind_gust_strt.data

        wrkt.temp_end = form.temp_end.data
        wrkt.dew_point_end = form.dew_point_end.data
        wrkt.temp_feels_like_end = form.temp_feels_like_end.data
        wrkt.wethr_cond_end = form.wethr_cond_end.data
        wrkt.hmdty_end = form.hmdty_end.data
        wrkt.wind_speed_end = form.wind_speed_end.data
        wrkt.wind_gust_end = form.wind_gust_end.data

        wrkt.warm_up_tot_tm_sec = tm_conv.time_to_sec(form.warm_up_dur_h.data, form.warm_up_dur_m.data, form.warm_up_dur_s.data)
        wrkt.warm_up_tot_dist_mi = form.warm_up_tot_dist.data

        wrkt.cool_down_tot_tm_sec = tm_conv.time_to_sec(        form.cool_down_dur_h.data, form.cool_down_dur_m.data, form.cool_down_dur_s.data)
        wrkt.cool_down_tot_dist_mi = form.cool_down_tot_dist.data

        wrkt.intrvl_tot_tm_sec = tm_conv.time_to_sec(form.intrvl_dur_h.data, form.intrvl_dur_m.data, form.intrvl_dur_s.data)
        wrkt.intrvl_tot_dist_mi = form.intrvl_tot_dist.data

        wrkt.show_pause = form.show_pause.data

        if form.wrkt_id.data == "":
            db.session.add(wrkt)
            db.session.commit()
            flash('Workout has been created!')
        else:
            db.session.commit()
            flash('Workout has been updated!')

        return redirect(url_for('main.workouts'))
    elif request.method == 'GET' and request.args.get('workout') != None:
        usr_id = current_user.id
        wrkt_id = request.args.get('workout')
        logger.info('Update Workout: ' + str(wrkt_id)+' for user: '+str(usr_id))


        label_val['title'] = 'Update Workout'
        del form.wrkt_dt
        wrkt = Workout.query.filter_by(id=wrkt_id, \
            user_id=usr_id).first_or_404(id)

        form.gear_lst.default = wrkt.gear_det.id
        form.process() # Need to run after setting the default and needs to be before other fields are populated
        # form.gear.data = wrkt.gear_det.nm

        form.type.data = wrkt.type
        label_val['wrkt_dttm'] = wrkt.wrkt_dttm

        form.wrkt_tm.data = wrkt.wrkt_dttm

        form.duration_h.data, form.duration_m.data, form.duration_s.data = tm_conv.split_sec_to_time(wrkt.dur_sec)
        form.distance.data = wrkt.dist_mi
        form.notes.data = wrkt.notes
        form.wrkt_id.data = wrkt_id

        form.clothes.data = wrkt.clothes
        form.ele_up.data = wrkt.ele_up
        form.ele_down.data = wrkt.ele_down
        form.hr.data = wrkt.hr
        form.cal_burn.data = wrkt.cal_burn
        form.category.data = wrkt.category
        form.location.data = wrkt.location
        form.training_type.data = wrkt.training_type

        form.temp_strt.data = wrkt.temp_strt
        form.dew_point_strt.data = wrkt.dew_point_strt
        form.temp_feels_like_strt.data = wrkt.temp_feels_like_strt
        form.wethr_cond_strt.data = wrkt.wethr_cond_strt
        form.hmdty_strt.data = wrkt.hmdty_strt
        form.wind_speed_strt.data = wrkt.wind_speed_strt
        form.wind_gust_strt.data = wrkt.wind_gust_strt

        form.temp_end.data = wrkt.temp_end
        form.dew_point_end.data = wrkt.dew_point_end
        form.temp_feels_like_end.data = wrkt.temp_feels_like_end
        form.wethr_cond_end.data = wrkt.wethr_cond_end
        form.hmdty_end.data = wrkt.hmdty_end
        form.wind_speed_end.data = wrkt.wind_speed_end
        form.wind_gust_end.data = wrkt.wind_gust_end

        form.warm_up_dur_h.data, form.warm_up_dur_m.data, form.warm_up_dur_s.data = tm_conv.split_sec_to_time(wrkt.warm_up_tot_tm_sec)
        form.warm_up_tot_dist.data = wrkt.warm_up_tot_dist_mi

        form.cool_down_dur_h.data, form.cool_down_dur_m.data, form.cool_down_dur_s.data = tm_conv.split_sec_to_time(wrkt.cool_down_tot_tm_sec)
        form.cool_down_tot_dist.data = wrkt.cool_down_tot_dist_mi

        form.intrvl_dur_h.data, form.intrvl_dur_m.data, form.intrvl_dur_s.data = tm_conv.split_sec_to_time(wrkt.intrvl_tot_tm_sec)
        form.intrvl_tot_dist.data = wrkt.intrvl_tot_dist_mi

        form.show_pause.data = wrkt.show_pause

    # else:
        # logger.debug('Create Workout')
        # label_val['title'] = 'Create Workout'

    return render_template('edit_workout.html', label_val=label_val, form=form, destPage = 'edit')

# @bp.route('/testing', methods=['GET','POST'])
# @login_required
# def testing():
#     logger.info('testing')
#     title="Testing page"
#     form = EmptyForm()
#
#     return render_template('testing.html', title=title, form=form)

@bp.route('/calculate', methods=['GET'])
def calculate():
    logger.info('calculate')
    title="Calculate Pace and Time"
    form = EmptyForm()

    onLoad = 'reloadCalculationValues();'


    return render_template('calculate.html', title=title, form=form, onLoad=onLoad)

@bp.route('/workout', methods=['GET'])
@login_required
def workout():
    logger.info('workout')
    usr_id = current_user.id
    wrkt_id = request.args.get('workout')
    logger.info('wrkt: ' + str(wrkt_id) + ' for user: ' + str(usr_id))
    workout = Workout.query.filter_by(id=wrkt_id, user_id=usr_id).first_or_404(description="Workout not found for current user")
    workout.duration = workout.dur_str()
    workout.intrvl_dur_str = workout.intrvl_dur_str()
    workout.warm_up_dur_str = workout.warm_up_dur_str()
    workout.cool_down_dur_str = workout.cool_down_dur_str()

    workout.pace = workout.pace_str()
    workout.warm_up_pace = workout.warm_up_pace_str()
    workout.cool_down_pace = workout.cool_down_pace_str()
    workout.intrvl_pace = workout.intrvl_pace_str()

    intvl_lst = sorted(Workout_interval.query.filter_by( \
      workout_id=wrkt_id, user_id=usr_id))

    intrvl_dict = {}
    mile_intrvl_lst = []
    segment_intrvl_lst = []
    pause_intrvl_lst = []
    lap_intrvl_lst = []
    for intrvl in intvl_lst:
        intrvl.duration = intrvl.dur_str()
        intrvl.pace = intrvl.pace_str()
        if intrvl.break_type == 'mile':
            intrvl.det = intrvl.interval_order +1
            mile_intrvl_lst.append(intrvl)
        elif intrvl.break_type == 'segment':
            if intrvl.interval_desc == None or intrvl.interval_desc == '':
                intrvl.det = intrvl.interval_order
            else:
                intrvl.det = intrvl.interval_desc
            segment_intrvl_lst.append(intrvl)
        elif intrvl.break_type == 'resume' and workout.show_pause == True:
            if intrvl.interval_desc == None or intrvl.interval_desc == '':
                intrvl.det = intrvl.interval_order
            else:
                intrvl.det = intrvl.interval_desc
            pause_intrvl_lst.append(intrvl)
        elif intrvl.break_type == 'lap':
            if intrvl.interval_desc == None or intrvl.interval_desc == '':
                intrvl.det = intrvl.interval_order
            else:
                intrvl.det = intrvl.interval_desc
            lap_intrvl_lst.append(intrvl)
    if len(lap_intrvl_lst) >1:
        intrvl_dict['lap_sum'] = wrkt_summary.get_lap_sum(lap_intrvl_lst)
    if len(segment_intrvl_lst) >1:
        intrvl_dict['segment_sum'] = wrkt_summary.get_lap_sum(segment_intrvl_lst)
    if len(mile_intrvl_lst) >1:
        intrvl_dict['mile_sum'] = wrkt_summary.get_mile_sum(mile_intrvl_lst)



    return render_template('workout.html', workout=workout, \
      mile_intrvl_lst=mile_intrvl_lst, segment_intrvl_lst=segment_intrvl_lst, destPage = 'edit', pause_intrvl_lst=pause_intrvl_lst, lap_intrvl_lst=lap_intrvl_lst, intrvls=intrvl_dict)


@bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    logger.info('dashboard')
    title="Dashboard"

    dash_lst_dict = {}

    gear_results = sorted(Gear_usage.query.filter_by(user_id=current_user.id, retired=False), reverse=True)
    gear_lst = []
    for gear in gear_results:
        if gear.type == 'Shoe' and gear.tot_dist >const.SHOE_MILE_AGE_SHOULD_RETIRE:
            gear.age_cond_class = 'gear_age_should_retire'
        elif gear.type == 'Shoe' and gear.tot_dist >const.SHOE_MILE_AGE_WARNING:
            gear.age_cond_class = 'gear_age_warning'
        else:
            gear.age_cond_class = ''
        gear_lst.append(gear)
    # gear_lst = gear_results
    dash_lst_dict['gear_lst'] = gear_lst

    wrkt_sum_results = Wrkt_sum.query.filter_by(user_id=current_user.id, type='Running')
    wrkt_sum_lst = []
    for wrkt_sum in wrkt_sum_results:
        wrkt_sum.duration = wrkt_sum.dur_str()
        i = getInsertPoint(wrkt_sum, wrkt_sum_lst)
        wrkt_sum_lst.insert(i,wrkt_sum)
    dash_lst_dict['wrkt_sum_lst'] = wrkt_sum_lst

    min_wkly_dt = date.today() - timedelta((const.NBR_WK_COMP+1) * 7)
    query = Wkly_mileage.query.filter_by(user_id=current_user.id, type='Running')
    query = query.filter(Wkly_mileage.dt_by_wk >=min_wkly_dt)
    wkly_mileage_results = sorted(query, reverse=True)
    wkly_mileage_lst = []
    for wk_mileage in wkly_mileage_results:
        wk_mileage.duration = wk_mileage.dur_str()
        wkly_mileage_lst.append(wk_mileage)
    dash_lst_dict['wkly_mileage_lst'] = wkly_mileage_lst

    min_yrly_dt = datetime(const.MIN_YR_COMP, 1, 1)
    query = Yrly_mileage.query.filter_by(user_id=current_user.id)
    query = query.filter(Yrly_mileage.type.in_(['Running','Cycling']))
    query = query.filter(Yrly_mileage.dt_by_yr >=min_yrly_dt)
    yrly_mileage_results = sorted(query, reverse=True)
    yrly_mileage_lst = []
    for yr_mileage in yrly_mileage_results:
        yr_mileage.duration = yr_mileage.dur_str()
        yr_mileage.pace = yr_mileage.pace_str()
        yrly_mileage_lst.append(yr_mileage)
    dash_lst_dict['yrly_mileage_lst'] = yrly_mileage_lst

    return render_template('dashboard.html', title=title, dash_lst_dict=dash_lst_dict)

def getInsertPoint(wrkt_sum, wrkt_sum_lst):
    i=0
    while i <len(wrkt_sum_lst):
        if wrkt_sum_lst[i].rng == 'Past 7 days':
            if wrkt_sum.rng == 'Current Week':
                return i
        elif wrkt_sum_lst[i].rng == 'Current Month':
            if wrkt_sum.rng in ['Past 7 days','Current Week']:
                return i
        elif wrkt_sum_lst[i].rng == 'Past 30 days':
            if wrkt_sum.rng in ['Past 7 days','Current Week','Current Month']:
                return i
        elif wrkt_sum_lst[i].rng == 'Current Year':
            if wrkt_sum.rng in ['Past 7 days','Current Week','Current Month','Past 30 days']:
                return i
        elif wrkt_sum_lst[i].rng == 'Past 365 days':
            if wrkt_sum.rng in ['Past 7 days','Current Week','Current Month','Past 30 days','Current Year']:
                return i
        i=i+1
    return i


@bp.route('/edit_workout_interval', methods=['GET','POST'])
@login_required
def edit_workout_interval():
    logger.info('edit_workout_interval: ' + str(request.args.get('workout')))
    wrktDict = {}

    form = WorkoutForm()

    if request.method == 'GET' and request.args.get('workout') != None:
        usr_id = current_user.id
        wrktDict['wrkt_id'] = request.args.get('workout')
        form.wrkt_id.data = request.args.get('workout')
        logger.info('Update Workout: ' + str(wrktDict['wrkt_id'])+' for user: '+str(usr_id))
        # Get Workout Intervals for workout based on wrktDict['wrkt_id']
        #   Currently only get for break_type='segment' order by interval_order
        # intvl_lst = sorted(Workout_interval.query.filter_by( \
          # workout_id=wrktDict['wrkt_id'], user_id=usr_id, break_type='segment'))
        query = Workout_interval.query.filter_by( \
            workout_id=wrktDict['wrkt_id'], user_id=usr_id)
        query = query.filter(Workout_interval.break_type.in_(['segment','lap']))
        intvl_lst = sorted(query)
        segment_intrvl_lst = []
        # form.wrkt_intrvl_segment_form = []
        for intrvl in intvl_lst:
            intrvl_form = WorkoutIntervalForm()
            intrvl_form.wrkt_intrvl_id = intrvl.id
            intrvl_form.interval_order = intrvl.interval_order
            intrvl_form.interval_desc = intrvl.interval_desc
            intrvl_form.dur_h, intrvl_form.dur_m, intrvl_form.dur_s = tm_conv.split_sec_to_time(intrvl.dur_sec)
            intrvl_form.dist = intrvl.dist_mi
            intrvl_form.hr = intrvl.hr
            intrvl_form.ele_up = intrvl.ele_up
            intrvl_form.ele_down = intrvl.ele_down
            intrvl_form.notes = intrvl.notes
            # intrvl.duration = intrvl.dur_str()
            # intrvl.pace = intrvl.pace_str()
            # if intrvl.break_type == 'mile':
            #     mile_intrvl_lst.append(intrvl)
            # elif intrvl.break_type == 'segment':
            #     if intrvl.interval_desc == None:
            #         intrvl.det = intrvl.interval_order
            #     else:
            #         intrvl.det = intrvl.interval_desc
            if intrvl.break_type == 'segment' or intrvl.break_type == 'lap':
                segment_intrvl_lst.append(intrvl_form)
                form.wrkt_intrvl_segment_form.append_entry(intrvl_form)

        # Create List of forms based on the intervals
        wrktDict['segment_intrvl_lst'] = segment_intrvl_lst
        # logger.debug(form.wrkt_intrvl_segment_form.entries)
    elif request.method == 'POST' and form.cancel.data:
        logger.debug('cancel')
        flash("Workout Intervals update canceled")
        wrkt_id = request.args.get('workout')
        return redirect(url_for('main.workout', workout=wrkt_id))
    elif request.method == 'POST':
        logger.debug('edit_workout_interval: validate_on_submit')
        usr_id = current_user.id
        wrkt_id = request.args.get('workout')
        for intrvl_form in form.wrkt_intrvl_segment_form.entries:
            # logger.debug(intrvl_form.interval_desc.data)
            # logger.debug(intrvl_form.wrkt_intrvl_id.data)
            wrktIntrvl = Workout_interval.query.filter_by(id=intrvl_form.wrkt_intrvl_id.data, user_id=usr_id, workout_id=wrkt_id).first_or_404()
            # logger.debug("Interval Order: " + str(wrktIntrvl.interval_order))
            if intrvl_form.interval_desc.data != '':
                wrktIntrvl.interval_desc = intrvl_form.interval_desc.data
            if intrvl_form.hr.data != '':
                wrktIntrvl.hr = intrvl_form.hr.data
        db.session.commit()
        flash("Workout Intervals updated")
        return redirect(url_for('main.workout', workout=wrkt_id))


    logger.debug('edit_workout_interval pre-render_template')
    return render_template('edit_workout_interval.html', form=form, wrktDet=wrktDict)
