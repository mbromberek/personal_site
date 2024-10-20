# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# First party classes
from datetime import datetime, timedelta, date
import time
import os, math, json, csv
# from datetime import combine

# Third party classes
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app, send_file, send_from_directory
from flask_login import current_user, login_required
import pandas as pd
import numpy as np

# Custom classes from GitHub
import GenerateMapImage.gen_map_img as genMap

# Custom classes
from app.main import bp
from app.main.forms import EmptyForm, WorkoutCreateBtnForm, WorkoutForm, WorkoutFilterForm, WorkoutIntervalForm, WorkoutExportForm, UserSettingsForm, GearForm, LocForm
from app.models import User, Workout, Workout_interval, Gear, Gear_usage, Wrkt_sum, Wkly_mileage, Moly_mileage, User_setting, Workout_type, Workout_category
from app import db
from app.utils import tm_conv, const, nbrConv, dt_conv
from app import logger, basedir
from app.utils import wrkt_summary
from app.utils import wrkt_split
from app.main import export, filtering
from app.model.goals import Yrly_goal
from app.model.workout_zones import Workout_zones
from app.model.location import Location
from app.model.yrly_mileage import Yrly_mileage
from app.model.book import Book
from app.model.book import CURR_READING_VAL, READ_VAL
from app.model.tag import Workout_tag, Tag, Tag_usage

@bp.route('/')
@bp.route('/index')
# @login_required
def index():
    logger.info('index')
    # user = {'displayname': 'Mike'}
    # workouts = [{'type':'Running', 'duration':'20m 56s', 'distance': '3.11', 'pace': '6m 44s'}, {'type':'Running', 'duration':'3h 35m 53s', 'distance': '26.2', 'pace': '8m 13s'}]

    dash_lst_dict = {}

    min_yrly_dt = datetime(int(datetime.now().strftime('%Y')), 1, 1)
    query = Yrly_mileage.query.filter_by(user_id=1)
    query = query.filter(Yrly_mileage.type.in_(['Running','Cycling']))
    query = query.filter(Yrly_mileage.dt_by_yr >=min_yrly_dt)
    yrly_mileage_results = sorted(query, reverse=True)
    yrly_goals_lst = []
    yrly_mileage_lst = []
    for yr_mileage in yrly_mileage_results:
        if yr_mileage.dt_year() == datetime.now().strftime('%Y'):
            goal = Yrly_goal.create_goal(yr_mileage)
            if len(goal) >0:
                yrly_goals_lst.extend(goal)

        yr_mileage.duration = yr_mileage.dur_str()
        yr_mileage.pace = yr_mileage.pace_str()
        yrly_mileage_lst.append(yr_mileage)
    yrly_goals_lst = Yrly_goal.generate_nonstarted_goals(yrly_goals_lst)
    dash_lst_dict['yrly_goals_lst'] = yrly_goals_lst
    dash_lst_dict['yrly_goals_dict_lst'] = Yrly_goal.lst_to_dict(yrly_goals_lst)
    # dash_lst_dict['yrly_mileage_lst'] = yrly_mileage_lst

    wrkt_sum_results = Wrkt_sum.query.filter_by(user_id=1, type='Running').all()
    wrkt_sum_mod_lst = Wrkt_sum.generate_missing_summaries(wrkt_sum_results, 'Running')
    wrkt_sum_lst = []
    for wrkt_sum in wrkt_sum_mod_lst:
        wrkt_sum.duration = wrkt_sum.dur_str()
        i = Wrkt_sum.getInsertPoint(wrkt_sum, wrkt_sum_lst)
        wrkt_sum_lst.insert(i,wrkt_sum)
    dash_lst_dict['wrkt_sum_lst'] = wrkt_sum_lst

    books={}
    # Get Currently Reading books
    # TODO should I sort?
    book_query = Book.query.filter_by(user_id=1).filter_by(status=CURR_READING_VAL)
    books['current'] = book_query

    # Get Read books
    # Store in dictionary of two lists (current read list, and read list)
    book_query = Book.query.filter_by(user_id=1).filter_by(status=READ_VAL)
    books['read'] = sorted(book_query, reverse=True)


    return render_template('index.html', title='Home Page', dash_lst_dict=dash_lst_dict \
        , destPage='home', books=books)

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
    page = filterValFromUrl['page']

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
        filterVal['type'] = {'run'}
    elif wrkt_filter_form.category_cycle_btn.data:
        logger.debug('Cycle Type Pressed')
        url_change = True
        filterVal['type'] = {'cycle'}
    elif wrkt_filter_form.category_swim_btn.data:
        logger.debug('Swim Type Pressed')
        url_change = True
        filterVal['type']={'swim'}
    if 'endurance' in filterVal['type']:
        filterVal['type'].discard('endurance')
        # filterVal['type'] = {'run','cycle','swim'}
        filterVal['type'] = filterVal['type'].union({'run','cycle','swim'})

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

        return redirect(url_for('main.workouts', page=1, type=','.join(filterVal['type']), category=filterVal['category'], temperature=filterVal['temperature'], distance=filterVal['distance'], txt_search=filterVal['txt_search'], min_strt_temp=filterVal['min_strt_temp'], max_strt_temp=filterVal['max_strt_temp'], min_dist=filterVal['min_dist'], max_dist=filterVal['max_dist'],
        strt_dt=strt_dt_str,
        end_dt=end_dt_str   ))

    type_filter = []
    category_filter = []
    btn_classes = {}
    logger.debug("type: " + str(filterVal['type']))
    for filter_type_grp in filterVal['type']:
        filter_type_lst = Workout_type.query.filter_by(grp=filter_type_grp)
        for filter_type in filter_type_lst:
            type_filter.append(filter_type.id)
    if 'run' in filterVal['type']:
        btn_classes['run'] = 'btn btn_selected'
    if 'cycle' in filterVal['type']:
        btn_classes['cycle'] = 'btn btn_selected'
    if 'swim' in filterVal['type']:
        btn_classes['swim'] = 'btn btn_selected'
    filterVal['type'] = list(filterVal['type'])

    if filterVal['category'] == 'training':
        filter_cat_lst = Workout_category.query.filter( Workout_category.nm.in_(['Training', 'Hard']))
        for filter_cat in filter_cat_lst:
            category_filter.append(filter_cat.id)
        btn_classes['training'] = 'btn btn_selected'
    if filterVal['category'] == 'long':
        filter_cat_lst = Workout_category.query.filter( Workout_category.nm.in_(['Long Run', 'Long']))
        for filter_cat in filter_cat_lst:
            category_filter.append(filter_cat.id)
        btn_classes['long'] = 'btn btn_selected'
    if filterVal['category'] == 'easy':
        filter_cat_lst = Workout_category.query.filter( Workout_category.nm.in_(['Easy']))
        for filter_cat in filter_cat_lst:
            category_filter.append(filter_cat.id)
        btn_classes['easy'] = 'btn btn_selected'
    if filterVal['category'] == 'race':
        filter_cat_lst = Workout_category.query.filter( Workout_category.nm.in_(['Race', 'Virtual Race']))
        for filter_cat in filter_cat_lst:
            category_filter.append(filter_cat.id)
        btn_classes['race'] = 'btn btn_selected'

    # logger.info('type_filter ' + str(type_filter))

    if wrkt_export_form.download_csv_btn.data:
        logger.debug('Export as CSV Pressed')
        query, usingSearch = filtering.get_workouts_from_filter(current_user.id, type_filter, category_filter, filterVal, wrkt_filter_form)

        query = query.order_by(Workout.wrkt_dttm.desc())
        if wrkt_export_form.max_export_records.data != None:
            workout_list = query.paginate(page=0, per_page=wrkt_export_form.max_export_records.data, error_out=False).items
        else:
            workout_list = query.all()
        # field_lst = ['Date','Type','Duration','Distance','Pace', 'Notes+', 'Category','Gear','Elevation','HR','Calories']
        export_file = export.wrkt_lst_to_csv(workout_list, wrkt_export_form)

        export_file_nm = 'workouts.export.' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.csv'

        return send_file(export_file, as_attachment=True, mimetype='text/csv', download_name=export_file_nm)

    wrkts_data = filtering.get_workouts(current_user.id, page, current_app.config['POSTS_PER_PAGE'], filterVal, 'main.workout', wrkt_filter_form)
    usingSearch = wrkts_data['_meta']['using_extra_search_fields']
    logger.debug(filterVal['type'])
    more_wrkt_filter = {'page':wrkts_data['_meta']['next_page'], 'type':filterVal['type'], 'category':filterVal['category'], 'temperature':filterVal['temperature'], 'distance':filterVal['distance'], 'txt_search':filterVal['txt_search'], 'min_strt_temp':filterVal['min_strt_temp'], 'max_strt_temp':filterVal['max_strt_temp'], 'min_dist':filterVal['min_dist'], 'max_dist':filterVal['max_dist'], 'strt_dt':filterVal['strt_dt'], 'end_dt':filterVal['end_dt'] } if 'next_page' in wrkts_data['_meta'] else None
    next_url = url_for('main.workouts', page=wrkts_data['_meta']['next_page'], type=filterVal['type'], category=filterVal['category'], temperature=filterVal['temperature'], distance=filterVal['distance'], txt_search=filterVal['txt_search'], min_strt_temp=filterVal['min_strt_temp'], max_strt_temp=filterVal['max_strt_temp'], min_dist=filterVal['min_dist'], max_dist=filterVal['max_dist'], strt_dt=filterVal['strt_dt'],
    end_dt=filterVal['end_dt'] ) \
        if 'next_page' in wrkts_data['_meta'] else None
    prev_url = url_for('main.workouts', page=wrkts_data['_meta']['previous_page'], type=filterVal['type'], category=filterVal['category'], temperature=filterVal['temperature'], distance=filterVal['distance'], txt_search=filterVal['txt_search'], min_strt_temp=filterVal['min_strt_temp'], max_strt_temp=filterVal['max_strt_temp'], min_dist=filterVal['min_dist'], max_dist=filterVal['max_dist'], strt_dt=filterVal['strt_dt'],
    end_dt=filterVal['end_dt']) \
        if wrkts_data['_meta']['previous_page'] != None else None

    return render_template('workouts.html', title='Workouts', workouts=wrkts_data, form=wrktCreateBtn, wrkt_filter_form=wrkt_filter_form, btn_classes=btn_classes, next_url=next_url, more_wrkt_filter=more_wrkt_filter, prev_url=prev_url, using_search=usingSearch, destPage='search', wrkt_export_form=wrkt_export_form)


@bp.route('/more_workouts', methods=['GET'])
@login_required
def more_workouts():
    logger.info('more_workouts')
    # time.sleep(2)

    filterVal = filtering.getFilterValuesFromGet(request)
    logger.info(filterVal)
    page = filterVal['page']
    filterVal.pop('page',None)

    data = filtering.get_workouts(current_user.id, page, current_app.config['POSTS_PER_PAGE'], filterVal, 'main.workout')
    return jsonify(data)

@bp.route('/split_intrvl', methods=['GET'])
@login_required
def split_intrvl():
    logger.info('split_intrvl')

    # logger.info(str(request.args))

    usr_id = current_user.id
    wrkt_id = request.args.get('wrkt_id')

    intrvl_split_lst = json.loads(request.args.get('intrvl_split_lst'))
    logger.info(intrvl_split_lst)

    split_laps = []
    wrkt = Workout.query.filter_by(id=wrkt_id, user_id=usr_id).first_or_404(id)
    # Read in the workout
    wrkt_pickle = os.path.join(current_app.config['WRKT_FILE_DIR'], str(usr_id), wrkt.wrkt_dir, 'workout.pickle')
    logger.debug(wrkt.wrkt_dir)

    for intrvl_split in intrvl_split_lst:
        logger.debug(intrvl_split)
        intrvl_id = intrvl_split['id']
        wrkt_intrvl = Workout_interval.query.filter_by(id=intrvl_id, user_id=usr_id).first_or_404(id)
        logger.debug(wrkt_intrvl)

        wrkt_df = pd.read_pickle(wrkt_pickle)

        if 'split_dist' in intrvl_split:
            split_dist = intrvl_split['split_dist']
            lap_updates = wrkt_split.split_lap(wrkt_df, wrkt_intrvl.interval_order, split_dist)['laps']
        elif 'merge' in intrvl_split:
            logger.debug('merge: ' + intrvl_id)
            lap_updates = wrkt_split.merge_laps(wrkt_df, wrkt_intrvl.interval_order)['laps']
        for lap in lap_updates:
            lap['dur_str'] = tm_conv.sec_to_time(lap['dur_sec'], format='hms-auto')
            if math.isnan(lap['lat']):
                lap.pop('lat')
            if math.isnan(lap['lon']):
                lap.pop('lon')
        split_laps.append({'laps':lap_updates, 'wrkt_id':wrkt_id, 'intrvl_id':intrvl_id})
            
    logger.info({'split_laps':split_laps})
    return jsonify({'split_laps':split_laps})

@bp.route('/edit_workout', methods=['GET','POST'])
@login_required
def edit_workout():
    logger.info('edit_workout: ' + str(request.args.get('workout')))
    form = WorkoutForm()

    gear_lst = sorted(Gear_usage.query.filter_by(user_id=current_user.id), reverse=True)
    gear_select_lst = []
    retired_gear = False
    for g in gear_lst:
        if g.retired == True and retired_gear == False:
            gear_select_lst.append([-1, '──────────'])
            retired_gear = True
        gear_select_lst.append([g.gear_id, g.nm])
    form.gear_lst.choices = gear_select_lst

    wrkt_type_lst = sorted(Workout_type.query)
    type_select_lst = []
    for g in wrkt_type_lst:
        type_select_lst.append([g.id, g.nm])
    form.type_lst.choices = type_select_lst

    wrkt_cat_lst = sorted(Workout_category.query)
    cat_select_lst = []
    for g in wrkt_cat_lst:
        cat_select_lst.append([g.id, g.nm])
    cat_select_lst.append([-1, '──────────'])
    form.cat_lst.choices = cat_select_lst


    label_val = {}
    usr_id = current_user.id

    training_type_lst = []
    training_type_query = db.session.query(Workout.training_type).distinct().filter_by(user_id=usr_id).all()
    for trn_typ_rec in training_type_query:
        if trn_typ_rec[0] != None:
            training_type_lst.append(trn_typ_rec[0])

    loc_lst = []
    location_query = db.session.query(Location.name).distinct().filter_by(user_id=usr_id).all()
    for loc_rec in location_query:
        loc_lst.append(loc_rec[0])
    logger.debug(str(loc_lst))

    logger.debug("Request Method: " + request.method)
    # logger.debug("Request Args workout: " + request.args.get('workout'))
    logger.debug("Workout ID: " + str(form.wrkt_id.data))

    if form.wrkt_id.data == None or form.wrkt_id.data == "":
        logger.info('Create Workout')
        label_val['title'] = 'Create Workout'
        nxt_shoe_prediction = Gear.get_next_shoe(usr_id, '')
        if nxt_shoe_prediction['id'] != '':
            form.gear_lst.default = nxt_shoe_prediction['id']
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
            wrkt.t_zone = form.t_zone.data
        else:
            logger.info('update workout')
            # usr_id = current_user.id
            wrkt_id = form.wrkt_id.data
            wrkt = Workout.query.filter_by(id=wrkt_id, user_id=usr_id).first_or_404(id)
        wrkt.dur_sec = tm_conv.time_to_sec(form.duration_h.data, form.duration_m.data, form.duration_s.data)
        # wrkt.type = form.type.data
        if form.type_lst.data == -1:
            wrkt.type_id = None
        else:
            wrkt.type_id = form.type_lst.data
        # wrkt.category = form.category.data
        if form.cat_lst.data == -1:
            wrkt.category_id = None
        else:
            wrkt.category_id = form.cat_lst.data

        wrkt.dist_mi = form.distance.data
        wrkt.notes = form.notes.data

        if form.gear_lst.data == -1:
            wrkt.gear_id = None
        else:
            wrkt.gear_id = form.gear_lst.data
        wrkt.clothes = form.clothes.data
        wrkt.ele_up = form.ele_up.data
        wrkt.ele_down = form.ele_down.data
        wrkt.hr = form.hr.data
        wrkt.cal_burn = form.cal_burn.data

        if wrkt.location != form.location.data and wrkt.lat_strt != '' and form.location.data != None and form.location.data != '':
            Location.create_loc_if_not_exist(form.location.data, usr_id, wrkt.lat_strt, wrkt.long_strt)
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
        wrkt.show_map_laps = form.show_map_laps.data
        wrkt.show_map_miles = form.show_map_miles.data

        if form.wrkt_id.data == "":
            db.session.add(wrkt)
            db.session.commit()
            flash('Workout has been created!')
        else:
            db.session.commit()
            flash('Workout has been updated!')
            return redirect(url_for('main.workout', workout=form.wrkt_id.data))

        return redirect(url_for('main.workouts'))
    elif request.method == 'GET' and request.args.get('workout') != None:
        usr_id = current_user.id
        wrkt_id = request.args.get('workout')
        logger.info('Update Workout: ' + str(wrkt_id)+' for user: '+str(usr_id))


        label_val['title'] = 'Update Workout'
        del form.wrkt_dt
        wrkt = Workout.query.filter_by(id=wrkt_id, \
            user_id=usr_id).first_or_404(id)

        if wrkt.gear_det != None:
            form.gear_lst.default = wrkt.gear_det.id
        else:
            form.gear_lst.default = -1
        # form.type.data = wrkt.type
        form.type_lst.default = wrkt.type_det.id
        # form.category.data = wrkt.category
        if wrkt.category_det != None:
            form.cat_lst.default = wrkt.category_det.id
        else:
            form.cat_lst.default = -1
        form.process() # Need to run after setting the default and needs to be before other fields are populated
        # form.gear.data = wrkt.gear_det.nm

        label_val['wrkt_dttm'] = wrkt.wrkt_dttm
        label_val['t_zone'] = wrkt.t_zone

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
        form.show_map_laps.data = wrkt.show_map_laps
        form.show_map_miles.data = wrkt.show_map_miles


    # else:
        # logger.debug('Create Workout')
        # label_val['title'] = 'Create Workout'
    # form.gear_lst.default = 44
    if label_val['title'] == 'Create Workout':
        # Need to do this at the end to prevent issues with data after Create submit. The process is needed to set default shoe
        form.process() # Need to run after setting the default and needs to be before other fields are populated


    return render_template('edit_workout.html', label_val=label_val, form=form, destPage = 'edit', training_type_lst=training_type_lst, location_lst=loc_lst)

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

    # Get workouts tags and sort by when tag was added to workout
    tags_query = Workout_tag.query.filter_by(workout_id=wrkt_id, user_id=usr_id)
    tags = sorted(tags_query, key=lambda x: x.isrt_ts)
    for tag in tags:
        logger.info(tag)
        logger.info(tag.workout_tag.nm)
    workout.tags = tags

    intvl_lst = sorted(Workout_interval.query.filter_by( \
      workout_id=wrkt_id, user_id=usr_id))
    # zone_dict = Workout_zone.get_zones(usr_id)
    wrkt_zones = Workout_zones(usr_id)

    intrvl_dict = {}
    mile_intrvl_lst = []
    segment_intrvl_lst = []
    pause_intrvl_lst = []
    lap_intrvl_lst = []
    wrkt_stats_lst = []

    lap_marker_lst = []
    mile_marker_lst = []
    segment_marker_lst = []
    pause_marker_lst = []

    for intrvl in intvl_lst:
        intrvl.duration = intrvl.dur_str()
        intrvl.pace = intrvl.pace_str()
        intrvl.hr_zone = wrkt_zones.hr_zone(intrvl.hr)
        intrvl.pace_zone = wrkt_zones.pace_zone(intrvl.pace_sec())
        if intrvl.break_type == 'mile':
            intrvl.det = intrvl.interval_order +1
            if intrvl.lat != None:
                mile_marker_lst.append({'nbr':intrvl.det, 'lat':intrvl.lat, 'lon':intrvl.lon})
            mile_intrvl_lst.append(intrvl)
        elif intrvl.break_type == 'segment':
            if intrvl.interval_desc == None or intrvl.interval_desc == '':
                intrvl.det = intrvl.interval_order
            else:
                intrvl.det = intrvl.interval_desc
            if intrvl.lat != None:
                segment_marker_lst.append({'nbr':intrvl.interval_order, 'lat':intrvl.lat, 'lon':intrvl.lon})
            segment_intrvl_lst.append(intrvl)
        elif intrvl.break_type == 'resume' and workout.show_pause == True:
            if intrvl.interval_desc == None or intrvl.interval_desc == '':
                intrvl.det = intrvl.interval_order
            else:
                intrvl.det = intrvl.interval_desc
            if intrvl.lat != None:
                pause_marker_lst.append({'nbr':intrvl.interval_order, 'lat':intrvl.lat, 'lon':intrvl.lon})
            pause_intrvl_lst.append(intrvl)
        elif intrvl.break_type == 'lap':
            if intrvl.interval_desc == None or intrvl.interval_desc == '':
                intrvl.det = intrvl.interval_order
            else:
                intrvl.det = intrvl.interval_desc
            intrvl.nbr = intrvl.interval_order
            if intrvl.lat != None:
                lap_marker_lst.append({'nbr':intrvl.interval_order, 'lat':intrvl.lat, 'lon':intrvl.lon})
            lap_intrvl_lst.append(intrvl)

    if len(lap_intrvl_lst) >1:
        intrvl_dict['lap_sum'] = wrkt_summary.get_lap_sum(lap_intrvl_lst)
        wrkt_stats_lst.extend(intrvl_dict['lap_sum'])
    if len(segment_intrvl_lst) >1:
        intrvl_dict['segment_sum'] = wrkt_summary.get_lap_sum(segment_intrvl_lst)
        wrkt_stats_lst.extend(intrvl_dict['segment_sum'])

    # Set default tab to show on workout page
    if len(lap_intrvl_lst) >1 and workout.show_map_laps and (\
        workout.category_det.nm == 'Training' or not workout.show_map_miles):
        intrvl_dict['default_lap_tab'] = 'id=defaultOpen'
    elif len(segment_intrvl_lst) >1 and (\
        workout.category_det.nm == 'Training' or not workout.show_map_miles):
        intrvl_dict['default_segment_tab'] = 'id=defaultOpen'
    else:
        intrvl_dict['default_mile_tab'] = 'id=defaultOpen'
        

    map_dict = {}
    wrkt_data_lst = []
    wrkt_miles_dict = {}

    if workout.wrkt_dir != None:
        try:
            wrkt_df = pd.read_pickle(os.path.join(current_app.config['WRKT_FILE_DIR'], str(workout.user_id), workout.wrkt_dir, 'workout.pickle'))
            
            
            '''
            wrkt_df['lat_lon'] = wrkt_df[['latitude','longitude']].apply(tuple, axis=1)
            lap_dur_min_max = wrkt_df.groupby('lap')[['dur_sec']].agg(['min','max'])
            lap_dur_min_max.columns = [c[0] + '_' + c[1] for c in lap_dur_min_max.columns]
            lap_lat_lon = wrkt_df.groupby('lap').agg({'lat_lon': lambda x:list(x)})
            lap_agg = pd.merge(lap_dur_min_max, lap_lat_lon, how='inner', left_index=True, right_index=True)
            lap_dict = lap_agg.to_dict('records')
            '''
            
            
            
            intrvl_dict['mile_sum'] = wrkt_summary.get_mile_sum_from_df(wrkt_df)
            workout.pos_neg_splits = intrvl_dict['mile_sum'][2]['det']
            workout.pos_neg_splits_amt = intrvl_dict['mile_sum'][2]['duration']
            if workout.pos_neg_splits == 'Negative Splits':
                workout.pos_neg_splits_icon = '✅'
            elif workout.pos_neg_splits == 'Positive Splits':
                workout.pos_neg_splits_icon = '👍'
            else:
                workout.pos_neg_splits_icon = '😮'
            wrkt_stats_lst.extend(intrvl_dict['mile_sum'])

            lat_max = wrkt_df['latitude'].max()
            lat_min = wrkt_df['latitude'].min()
            lon_max = wrkt_df['longitude'].max()
            lon_min = wrkt_df['longitude'].min()

            if not math.isnan(lat_max):
                map_dict = {}
                map_dict['key'] = current_app.config['MAPBOX_API_KEY']
                map_dict['max_zoom'] = current_app.config['MAP_MAX_ZOOM']

                map_dict['center'] = genMap.calc_center(lats=[lat_max, lat_min], lons=[lon_max, lon_min])
                map_dict['zoom'] = genMap.calc_zoom(lats=[lat_min, lat_max], lons=[lon_min, lon_max], img_dim={'height':1300, 'width':1600})

                # print('zoom: ' + str(map_dict['zoom']))
                # print('center:' + str(map_dict['center']))

                map_dict['lat_lon'] = wrkt_df[['latitude', 'longitude']].dropna().values.tolist()

                wrkt_df['altitude_ft'].fillna(method='ffill', inplace=True)
                wrkt_df['altitude_ft'].fillna(method='bfill', inplace=True)
                wrkt_df['ele_roll'] = wrkt_df['altitude_ft'].rolling(15).mean()
                wrkt_df['hr'].fillna(method='ffill', inplace=True)
                wrkt_df['hr'].fillna(method='bfill', inplace=True)

                # Get Current pace in minutes with decimal for seconds
                wrkt_df['dist_mi_diff'] = wrkt_df['dist_mi'].diff()
                wrkt_df['dist_mi_roll'] = wrkt_df['dist_mi_diff'].rolling(min_periods=1, window=11).sum()
                wrkt_df['dur_sec_diff'] = wrkt_df['dur_sec'].diff()
                wrkt_df['dur_sec_roll'] = wrkt_df['dur_sec_diff'].rolling(min_periods=1, window=11).sum()
                wrkt_df['curr_pace_sec'] = wrkt_df['dur_sec_roll'] / wrkt_df['dist_mi_roll']
                # Set infinite or NaN to 0
                wrkt_df['curr_pace_sec'].replace(np.inf, 0, inplace=True)
                wrkt_df['curr_pace_sec'].fillna(0, inplace=True)
                # If pace was slower than slowest pace set to that
                wrkt_df['curr_pace_sec'].values[wrkt_df['curr_pace_sec'].values >const.SLOWEST_PACE] = const.SLOWEST_PACE 
                # Set curr_pace_sec of first 10 records to pace for 11th record
                wrkt_df.iloc[:10, wrkt_df.columns.get_loc('curr_pace_sec')] = wrkt_df.iloc[10:11, wrkt_df.columns.get_loc('curr_pace_sec')].values[0]
                wrkt_df['curr_pace_minute'] = wrkt_df['curr_pace_sec'] / 60
                wrkt_df['curr_pace_minute'] = wrkt_df['curr_pace_minute'].rolling(15).mean()
                # Remove calculation columns that are no longer needed
                wrkt_df.drop(['dist_mi_diff','dist_mi_roll','dur_sec_diff','dur_sec_roll'], axis=1, inplace=True)

                wrkt_data_lst = wrkt_df[['ele_roll','dist_mi','hr','curr_pace_minute']].to_dict('records')

                wrkt_miles_df = wrkt_df.copy()
                wrkt_miles_df['curr_pace_str'] = wrkt_miles_df.apply(\
                    lambda x: tm_conv.sec_to_time(x['curr_pace_sec'], format='ms'), axis=1\
                )
                wrkt_miles_df['dur_str'] = wrkt_miles_df.apply(\
                    lambda x: tm_conv.sec_to_time(x['dur_sec'], format='hms-auto'), axis=1\
                )

                wrkt_miles_df['dist'] = wrkt_miles_df.round({'dist_mi':2})[['dist_mi']].astype(str)
                wrkt_miles_df.set_index('dist', inplace=True)
                wrkt_miles_df.drop_duplicates(keep='first', inplace=True)
                wrkt_miles_dict = wrkt_miles_df[~wrkt_miles_df.index.duplicated(keep='first')][[\
                    'dist_mi','dur_str','ele_roll','hr'\
                    ,'curr_pace_str','latitude','longitude','lap'\
                    # ,'dur_sec','curr_pace_minute','altitude_ft'\ # fields are not currently used 
                ]].to_dict('index')

                if len(lap_marker_lst) >0:
                    # Remove last record for lap since that is the end of the workout
                    map_dict['lap_markers'] = lap_marker_lst[:-1]
                else:
                    # If get_splits_by_group is removed then need to set lap_markers to empty list
                    # map_dict['lap_markers'] = get_splits_by_group(wrkt_df, 'lap')
                    map_dict['lap_markers'] = []
                if len(mile_marker_lst) >0:
                    map_dict['mile_markers'] = mile_marker_lst[:-1]
                else:
                    # map_dict['mile_markers'] = get_splits_by_group(wrkt_df, 'mile')
                    map_dict['mile_markers'] = []
                map_dict['pause_markers'] = []
        except Exception as e:
            logger.error(e, exc_info=True)
            logger.error('missing pickle file: {}'.format(workout.wrkt_dir))

    elif len(mile_intrvl_lst) >1:
        intrvl_dict['mile_sum'] = wrkt_summary.get_mile_sum(mile_intrvl_lst)
        wrkt_stats_lst.extend(intrvl_dict['mile_sum'])

    if 'map_full' in request.args and request.args.get('map_full') == 'Y':
        logger.info('map_full')
        return render_template('map_full.html', workout=workout, \
            mile_intrvl_lst=mile_intrvl_lst, segment_intrvl_lst=segment_intrvl_lst, destPage = 'workout', \
            pause_intrvl_lst=pause_intrvl_lst, lap_intrvl_lst=lap_intrvl_lst, intrvls=intrvl_dict, map_dict=map_dict, \
            wrkt_data_lst=wrkt_data_lst, wrkt_miles_dict=wrkt_miles_dict,\
            wrkt_stats_lst=wrkt_stats_lst
        )

    logger.info(wrkt_stats_lst)
    return render_template('workout.html', workout=workout, \
      mile_intrvl_lst=mile_intrvl_lst, segment_intrvl_lst=segment_intrvl_lst, destPage = 'workout', pause_intrvl_lst=pause_intrvl_lst, lap_intrvl_lst=lap_intrvl_lst, intrvls=intrvl_dict, map_dict=map_dict, \
      wrkt_data_lst=wrkt_data_lst, wrkt_miles_dict=wrkt_miles_dict, \
      wrkt_stats_lst=wrkt_stats_lst
    )


def get_splits_by_group(df, group_field, skip_first=True):
    '''
    Get first row for each value in group_field column
    Returns list of dictionaries.
        Each record contains
            nbr: number for the grouped field
            lat: latitue
            lon: longitude
    '''
    df_group = df.groupby(group_field).first().iloc[1:, :]
    if skip_first:
        df_group['nbr'] = df_group.index -1
    else:
        df_group['nbr'] = df_group.index
    df_group.rename(columns={'latitude': 'lat', 'longitude': 'lon'}, inplace=True)
    return df_group[['nbr','lat','lon']].to_dict(orient='records')

@bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    logger.info('dashboard')
    title="Dashboard"
    destPage="dashboard"
    usr_id = current_user.id
    user = User.query.get_or_404(usr_id)
    settings = user.get_settings()

    dash_lst_dict = {}

    gear_results = sorted(Gear_usage.query.filter_by(user_id=current_user.id, retired=False), reverse=True)
    gear_lst = []
    for gear in gear_results:
        if gear.type == 'Shoe' and gear.tot_dist >settings.get_field('shoe_mile_max'):
            gear.age_cond_class = 'gear_age_should_retire'
        elif gear.type == 'Shoe' and gear.tot_dist >settings.get_field('shoe_mile_warning'):
            gear.age_cond_class = 'gear_age_warning'
        else:
            gear.age_cond_class = ''
        gear_lst.append(gear)
    # gear_lst = gear_results
    dash_lst_dict['gear_lst'] = gear_lst

    wrkt_sum_results = Wrkt_sum.query.filter_by(user_id=current_user.id, type='Running').all()
    wrkt_sum_mod_lst = Wrkt_sum.generate_missing_summaries(wrkt_sum_results, 'Running')
    wrkt_sum_lst = []
    for wrkt_sum in wrkt_sum_mod_lst:
        wrkt_sum.duration = wrkt_sum.dur_str()
        i = Wrkt_sum.getInsertPoint(wrkt_sum, wrkt_sum_lst)
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

    '''
    min_yrly_dt = datetime(const.MIN_YR_COMP, 1, 1)
    query = Yrly_mileage.query.filter_by(user_id=current_user.id)
    # query = query.filter(Yrly_mileage.type.in_(['Running','Cycling','Strength Training']))
    query = query.filter(Yrly_mileage.type.in_(['Running','Cycling']))
    query = query.filter(Yrly_mileage.dt_by_yr >=min_yrly_dt)
    yrly_mileage_results = sorted(query, reverse=True)
    yrly_goals_lst = []
    yrly_mileage_lst = []
    for yr_mileage in yrly_mileage_results:
        if yr_mileage.dt_year() == datetime.now().strftime('%Y'):
            goal = Yrly_goal.create_goal(yr_mileage)
            if len(goal) >0:
                yrly_goals_lst.extend(goal)
        yr_mileage.duration = yr_mileage.dur_str()
        yr_mileage.pace = yr_mileage.pace_str()
        yrly_mileage_lst.append(yr_mileage)
    yrly_goals_lst = Yrly_goal.generate_nonstarted_goals(yrly_goals_lst)
    dash_lst_dict['yrly_goals_lst'] = yrly_goals_lst
    dash_lst_dict['yrly_goals_dict_lst'] = Yrly_goal.lst_to_dict(yrly_goals_lst)
    dash_lst_dict['yrly_mileage_lst'] = yrly_mileage_lst
    '''
    
    '''
    query = Yrly_mileage.query.filter_by(user_id=current_user.id)
    query = query.filter(Yrly_mileage.type.in_(['Strength Training']))
    query = query.filter(Yrly_mileage.dt_by_yr >=min_yrly_dt)
    yrly_strength_results = sorted(query, reverse=True)
    yrly_strength_lst = []
    for yr_mileage in yrly_strength_results:
        yr_mileage.duration = yr_mileage.dur_str()
        # yr_mileage.pace = yr_mileage.pace_str()
        yrly_strength_lst.append(yr_mileage)
    dash_lst_dict['yrly_workout_lst'] = {}
    dash_lst_dict['yrly_workout_lst']['header'] = 'Strength Training'
    dash_lst_dict['yrly_workout_lst']['data'] = yrly_strength_lst
    '''
    
    
    # Get total workouts and duration by year
    # Get yearly totals of all workouts 
    # Sum up Count and Duration for all workouts by year
    min_yrly_dt = datetime(const.MIN_YR_COMP, 1, 1)
    query = Yrly_mileage.query.filter_by(user_id=current_user.id)
    # query = query.filter(Yrly_mileage.type.in_(['Strength Training']))
    query = query.filter(Yrly_mileage.dt_by_yr >=min_yrly_dt)
    # yrly_results = sorted(query, reverse=True)
    yrly_results = sorted(query, key=lambda x: x.dt_by_yr, reverse=True)
    yrly_strength_lst = []
    yrly_running_lst = []
    yrly_cycling_lst = []
    yrly_swimming_lst = []
    yrly_workout_lst = []
    curr_yr_total = ''
    curr_yr_dict = {}
    yrly_goals_lst = []
    for idx, yr_workout_result in enumerate(yrly_results):
        if yr_workout_result.dt_year() == datetime.now().strftime('%Y'):
            goal = Yrly_goal.create_goal(yr_workout_result)
            if len(goal) >0:
                yrly_goals_lst.extend(goal)

        
        yr_workout_result.duration = yr_workout_result.dur_str()
        yr_workout_result.pace = yr_workout_result.pace_str()
        if curr_yr_total == '':
            curr_yr_total = yr_workout_result
        elif yr_workout_result.dt_year() != curr_yr_total.dt_year():
            curr_yr_total.duration = curr_yr_total.dur_str()
            # curr_yr_total.pace = curr_yr_total.pace_str()
            yrly_workout_lst.append(curr_yr_total)
            
            if 'Strength Training' in curr_yr_dict:
                yrly_strength_lst.append(yrly_results[curr_yr_dict['Strength Training']])
            if 'Running' in curr_yr_dict:
                yrly_running_lst.append(yrly_results[curr_yr_dict['Running']])
            if 'Cycling' in curr_yr_dict:
                yrly_cycling_lst.append(yrly_results[curr_yr_dict['Cycling']])
            if 'Swimming' in curr_yr_dict:
                yrly_swimming_lst.append(yrly_results[curr_yr_dict['Swimming']])
            
            curr_yr_total = yr_workout_result
            curr_yr_dict = {}
        else:
            curr_yr_total = curr_yr_total + yr_workout_result
        curr_yr_dict[yr_workout_result.type] = idx

    curr_yr_total.duration = curr_yr_total.dur_str()
    yrly_workout_lst.append(curr_yr_total)
    if 'Strength Training' in curr_yr_dict:
        yrly_strength_lst.append(yrly_results[curr_yr_dict['Strength Training']])
    if 'Running' in curr_yr_dict:
        yrly_running_lst.append(yrly_results[curr_yr_dict['Running']])
    if 'Cycling' in curr_yr_dict:
        yrly_cycling_lst.append(yrly_results[curr_yr_dict['Cycling']])
    if 'Swimming' in curr_yr_dict:
        yrly_swimming_lst.append(yrly_results[curr_yr_dict['Swimming']])
        
    yrly_goals_lst = Yrly_goal.generate_nonstarted_goals(yrly_goals_lst)
    yrly_goals_lst = sorted(yrly_goals_lst)
    dash_lst_dict['yrly_goals_lst'] = yrly_goals_lst
    dash_lst_dict['yrly_goals_dict_lst'] = Yrly_goal.lst_to_dict(yrly_goals_lst)
        
    dash_lst_dict['yrly_workout_lst'] = {}
    dash_lst_dict['yrly_workout_lst']['header'] = 'Workouts'
    dash_lst_dict['yrly_workout_lst']['data'] = yrly_workout_lst
    
    dash_lst_dict['yrly_strength_lst'] = {}
    dash_lst_dict['yrly_strength_lst']['header'] = 'Strength Training'
    dash_lst_dict['yrly_strength_lst']['data'] = yrly_strength_lst

    dash_lst_dict['yrly_running_lst'] = {}
    dash_lst_dict['yrly_running_lst']['header'] = 'Running'
    dash_lst_dict['yrly_running_lst']['data'] = yrly_running_lst
    dash_lst_dict['yrly_cycling_lst'] = {}
    dash_lst_dict['yrly_cycling_lst']['header'] = 'Cycling'
    dash_lst_dict['yrly_cycling_lst']['data'] = yrly_cycling_lst
    dash_lst_dict['yrly_swimming_lst'] = {}
    dash_lst_dict['yrly_swimming_lst']['header'] = 'Swimming'
    dash_lst_dict['yrly_swimming_lst']['data'] = yrly_swimming_lst


    # End of Get total workouts by year
    

    min_moly_dt = date.today() - timedelta((const.NBR_MO_COMP+1) * 31) # TODO probably not the best way to do this
    query = Moly_mileage.query.filter_by(user_id=current_user.id, type='Running')
    query = query.filter(Moly_mileage.dt_by_mo >=min_moly_dt)
    moly_mileage_results = sorted(query, reverse=True)
    moly_mileage_lst = []
    for mo_mileage in moly_mileage_results:
        mo_mileage_dict = mo_mileage.to_dict()
        moly_mileage_lst.append(mo_mileage_dict)
    dash_lst_dict['moly_run_mileage'] = {}
    dash_lst_dict['moly_run_mileage']['header'] = 'Running'
    dash_lst_dict['moly_run_mileage']['data'] = moly_mileage_lst

    query = Moly_mileage.query.filter_by(user_id=current_user.id, type='Cycling')
    query = query.filter(Moly_mileage.dt_by_mo >=min_moly_dt)
    moly_mileage_results = sorted(query, reverse=True)
    moly_mileage_lst = []
    for mo_mileage in moly_mileage_results:
        mo_mileage_dict = mo_mileage.to_dict()
        moly_mileage_lst.append(mo_mileage_dict)
    dash_lst_dict['moly_cycle_mileage'] = {}
    dash_lst_dict['moly_cycle_mileage']['header'] = 'Cycling'
    dash_lst_dict['moly_cycle_mileage']['data'] = moly_mileage_lst

    dash_lst_dict['nxt_gear'] = {}
    dash_lst_dict['nxt_gear']['training'] = Gear.get_next_shoe(usr_id, Workout_category.get_wrkt_cat_id('Training'))
    dash_lst_dict['nxt_gear']['easy'] = Gear.get_next_shoe(usr_id, Workout_category.get_wrkt_cat_id('Easy'))

    return render_template('dashboard.html', title=title, destPage=destPage, dash_lst_dict=dash_lst_dict)

@bp.route('/edit_workout_interval', methods=['GET','POST'])
@login_required
def edit_workout_interval():
    logger.info('edit_workout_interval: ' + str(request.args.get('workout')))
    wrktDict = {}

    form = WorkoutForm()
    usr_id = current_user.id

    if request.method == 'GET' and request.args.get('workout') != None:
        wrktDict['wrkt_id'] = request.args.get('workout')
        form.wrkt_id.data = request.args.get('workout')
        logger.info('Get Workout Intrvl: ' + str(wrktDict['wrkt_id'])+' for user: '+str(usr_id))
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
            intrvl_form.dur_h, intrvl_form.dur_m, intrvl_form.dur_s = \
                tm_conv.split_sec_to_time(intrvl.dur_sec)
            intrvl_form.dist = intrvl.dist_mi
            intrvl_form.hr = intrvl.hr
            intrvl_form.ele_up = intrvl.ele_up
            intrvl_form.ele_down = intrvl.ele_down
            intrvl_form.notes = intrvl.notes
            intrvl_form.split_dist = None
            intrvl_form.merge_laps_chk = False
            # intrvl_form.split_btn.render_kw = {"onclick":"split_interval_function()"}
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
    elif request.method == 'POST' and form.restore_btn.data:
        logger.debug('restore intervals')
        flash("Workout Intervals restored to original")
        wrkt_id = request.args.get('workout')
        # Get workouts pickle file
        wrkt = Workout.query.filter_by(id=wrkt_id, user_id=usr_id).first_or_404(id)
        wrkt_pickle = os.path.join(current_app.config['WRKT_FILE_DIR'], str(usr_id), wrkt.wrkt_dir, 'workout.pickle')
        wrkt_df = pd.read_pickle(wrkt_pickle)

        # delete intervals for the workout id
        wrktIntrvlLst = Workout_interval.query.filter_by(workout_id=wrkt_id, user_id=usr_id, break_type='lap')
        logger.debug(str(wrkt_id) + ' ' + str(usr_id))
        logger.debug(str(wrktIntrvlLst))
        for wrktIntrvl in wrktIntrvlLst:
            logger.debug('Delete: ' + str(wrktIntrvl))
            db.session.delete(wrktIntrvl)

        restore_laps = wrkt_split.restore_original_laps(wrkt_df)
        wrkt_df = restore_laps['wrkt_df']
        laps = restore_laps['laps']

        # save laps to DB
        for indx, lap in enumerate(laps):
            wkrt_Intrvl = Workout_interval()
            wkrt_Intrvl.from_dict(lap, usr_id, wrkt_id, 'lap')
            wkrt_Intrvl.interval_order = indx +1
            db.session.add(wkrt_Intrvl)

        # Commit delete and add to DB and Save new DF to pickle file
        db.session.commit()
        wrkt_df.to_pickle(wrkt_pickle)

        return redirect(url_for('main.edit_workout_interval', workout=wrkt_id))
    elif request.method == 'POST':
        logger.debug('edit_workout_interval: validate_on_submit')
        
        wrkt_id = request.args.get('workout')
        updt_ord = 0

        
        wrkt_df = None
        wrkt_pickle = None
        del_nxt_rec = False

        for intrvl_form in form.wrkt_intrvl_segment_form.entries:
            # Check and update interval description
            wrktIntrvl = Workout_interval.query.filter_by(id=intrvl_form.wrkt_intrvl_id.data, user_id=usr_id, workout_id=wrkt_id).first_or_404()
            if intrvl_form.interval_desc.data != '':
                wrktIntrvl.interval_desc = intrvl_form.interval_desc.data
            # Increment workout intervals order by updt_ord, will not change if no updates to order needed
            wrktIntrvl.interval_order = wrktIntrvl.interval_order + updt_ord

            split_dist = intrvl_form.split_dist.data
            merge_lap = intrvl_form.merge_laps_chk.data
            if del_nxt_rec == True:
                db.session.delete(wrktIntrvl)
                del_nxt_rec = False
            elif split_dist != '' and split_dist != None:
                logger.debug('split: ' + str(wrktIntrvl))
                if wrkt_pickle == None:
                    # Get workouts pickle file
                    wrkt = Workout.query.filter_by(id=wrkt_id, user_id=usr_id).first_or_404(id)
                    # Read in the workout
                    wrkt_pickle = os.path.join(current_app.config['WRKT_FILE_DIR'], str(usr_id), wrkt.wrkt_dir, 'workout.pickle')
    
                    # Load wrkt_df
                    wrkt_df = pd.read_pickle(wrkt_pickle)

                # process splitting interval
                wrkt_split_dict = wrkt_split.split_lap(wrkt_df, wrktIntrvl.interval_order, split_dist)
                wrkt_df = wrkt_split_dict['wrkt_df']
                laps = wrkt_split_dict['laps']
                
                # Increment update order for intervals
                updt_ord += 1
                
                # create two new intervals with previous intervals order
                for i in [0,1]:
                    newIntrvl = Workout_interval()
                    newIntrvl.from_dict(laps[i], usr_id, wrkt_id, 'lap')
                    newIntrvl.interval_order = wrktIntrvl.interval_order+i
                    newIntrvl.interval_desc = wrktIntrvl.interval_desc
                    db.session.add(newIntrvl)
                
                # delete interval that is being split
                db.session.delete(wrktIntrvl)
            elif merge_lap == True:
                if wrkt_pickle == None:
                    # Get workouts pickle file
                    wrkt = Workout.query.filter_by(id=wrkt_id, user_id=usr_id).first_or_404(id)
                    # Read in the workout
                    wrkt_pickle = os.path.join(current_app.config['WRKT_FILE_DIR'], str(usr_id), wrkt.wrkt_dir, 'workout.pickle')
    
                    # Load wrkt_df
                    wrkt_df = pd.read_pickle(wrkt_pickle)

                # process merging interval
                wrkt_split_dict = wrkt_split.merge_laps(wrkt_df, wrktIntrvl.interval_order)
                wrkt_df = wrkt_split_dict['wrkt_df']
                laps = wrkt_split_dict['laps']
                
                # Increment update order for intervals
                updt_ord -= 1 #TODO not sure if this works

                
                # Create one new merged interval with previous intervals order
                newIntrvl = Workout_interval()
                newIntrvl.from_dict(laps[0], usr_id, wrkt_id, 'lap')
                newIntrvl.interval_order = wrktIntrvl.interval_order
                newIntrvl.interval_desc = wrktIntrvl.interval_desc
                db.session.add(newIntrvl)

                # Remove interval that was merged and mark next interval to be removed
                db.session.delete(wrktIntrvl)
                del_nxt_rec = True

        db.session.commit()
        # save updated df to pickle file
        if wrkt_pickle != None:
            wrkt_df.to_pickle(wrkt_pickle)
        flash("Workout Intervals updated")
        return redirect(url_for('main.workout', workout=wrkt_id))


    logger.debug('edit_workout_interval pre-render_template')
    return render_template('edit_workout_interval.html', form=form, wrktDet=wrktDict)

@bp.route('/wrkt_images/<path:filename>', methods=['GET'])
@login_required
def wrkt_img_file(filename):
    # logger.info('wrkt_img_file')
    return send_from_directory(os.path.join(current_app.config['MEDIA_DIR'], \
        str(current_user.id),'thumbnails'), filename, as_attachment=False)

@bp.route('/public_images/<path:filename>', methods=['GET'])
def public_img_file(filename):
    # logger.info('public_img_file')
    return send_from_directory(os.path.join(current_app.config['PUBLIC_FILE_DIR'], \
        '1','thumbnails'), filename, as_attachment=False)

@bp.route('/settings', methods=['GET','POST'])
@login_required
def settings():
    logger.info('settings')
    usr_id = current_user.id

    setting_form = UserSettingsForm()
    user = User.query.get_or_404(usr_id)

    if request.method == 'GET':
        logger.info('settings GET')
    elif request.method == 'POST' and setting_form.cancel.data:
        logger.info('settings POST Cancel button pressed')
        return redirect(url_for('main.settings'))
    elif request.method == 'POST' and setting_form.submit.data:
        logger.info('settings POST Submit button pressed')
        user = User.query.get_or_404(usr_id)
        settings = user.get_settings()
        settings.shoe_mile_warning = setting_form.shoe_mile_warning.data
        settings.shoe_mile_max = setting_form.shoe_mile_max.data
        settings.shoe_min_brkin_ct = setting_form.shoe_min_brkin_ct.data
        if settings.user_id is None:
            settings.user_id = usr_id
            db.session.add(settings)
        db.session.commit()
        flash('Settings have been updated')
        return redirect(url_for('main.settings'))
    elif request.method == 'POST' and 'submit_full_regen' in request.form:
        logger.info('Generate new token')
        user.revoke_token()
        user.get_token()
        db.session.commit()
        flash('Generate new token')
        return redirect(url_for('main.settings'))

    setting_form.user_id.data = usr_id
    setting_form.displayname.data = user.displayname
    settings = user.get_settings()

    setting_form.shoe_mile_max.data = settings.get_field('shoe_mile_max')
    setting_form.shoe_mile_warning.data = settings.get_field('shoe_mile_warning')
    setting_form.shoe_min_brkin_ct.data = settings.get_field('shoe_min_brkin_ct')

    api_key_lst = []
    regen_btn = EmptyForm()
    regen_btn.submit.label.text = 'Regenerate'
    api_key_lst.append( {'description':'Full','key':user.token, 'key_part':user.token[:4] + '.....' + user.token[-4:], 'expiration':user.token_expiration,'regen_btn':regen_btn})


    gear_type_dict = {'1': 'Shoe', '2':'Bike', '3':'Pool', '4':'Insole', '5':'Trainer'}
    gear_type_select_lst = list(gear_type_dict.items())
    default_type = 1

    # query = Gear.query.filter_by(user_id=usr_id)
    # gear_lst = sorted(query, reverse=True)
    # gear_form_lst = []
    # for gear in gear_lst:
    #     gear_form = GearForm()
    #     for key, value in gear_type_dict.items():
    #         if value == gear.type:
    #             default_type = key
    #             break
    #     gear_form.type.choices = gear_type_select_lst
    #     gear_form.type.default = default_type
    #     gear_form.process()
    #     gear_form.id.data = gear.id
    #     gear_form.nm.data = gear.nm
    #     gear_form.prchse_dt.data = gear.prchse_dt
    #     gear_form.price.data = gear.price
    #     gear_form.retired.data = gear.retired
    #     gear_form.confirmed.data = gear.confirmed
    #     gear_form.company.data = gear.company
    #     # logger.info(gear_form)
    #     gear_form_lst.append(gear_form)

    gear_usage_lst = sorted(Gear_usage.query.filter_by(user_id=usr_id), reverse=True)
    gear_lst = []
    for gear in gear_usage_lst:
        # gear.retire_flag = 'Y' if gear.retired == True else 'N'
        gear.tot_dur = gear.tot_dur_str()
        # logger.info(gear)
        gear_lst.append(gear)

    query_loc_lst = sorted(Location.query.filter_by(user_id=usr_id))
    for loc in query_loc_lst:
        if loc.radius == None or loc.radius <=0:
            loc.radius = current_app.config['DFT_LOC_RADIUS']

    tag_usage_lst = sorted(Tag_usage.query.filter_by(user_id=usr_id))
    tag_lst = []
    for tag in tag_usage_lst:
        logger.info(tag)
        tag_lst.append(tag)

    return render_template('settings.html', user_setting_form=setting_form, destPage = 'settings', gear_lst=gear_usage_lst, loc_lst=query_loc_lst, api_key_lst=api_key_lst, tag_lst=tag_lst)

@bp.route('/edit_gear', methods=['GET','POST'])
@login_required
def edit_gear():
    usr_id = current_user.id
    gear_id = request.args.get('gear')
    logger.info('edit_gear: ' + str(gear_id))

    gear_type_dict = current_app.config['GEAR_TYPE_MAP']
    gear_type_select_lst = list(gear_type_dict.items())

    gear_form = GearForm()
    gear_form.type.choices = gear_type_select_lst

    label_val = 'Update Gear'

    if request.method == 'GET':
        logger.info('edit_gear GET')
    elif request.method == 'POST' and gear_form.cancel.data:
        logger.info('edit_gear POST Cancel button pressed')
        return redirect(url_for('main.settings'))
    elif request.method == 'POST':
        if not gear_form.validate_on_submit():
            if gear_id is not None:
                gear_usage = Gear_usage.query.filter_by(gear_id=gear_id, user_id = usr_id).one()
                gear_usage.tot_dur = gear_usage.tot_dur_str()
            else:
                gear_usage = None
            return render_template('edit_gear.html', destPage = 'settings', gear_form=gear_form, gear_usage=gear_usage, label_val=label_val)

        logger.info('edit_gear POST Submit button pressed')
        if gear_id is None:
            gear = Gear()
            gear.user_id = usr_id
        else:
            gear = Gear.query.filter_by(id=gear_id, user_id = usr_id).one()
        gear.nm = gear_form.nm.data
        gear.prchse_dt = gear_form.prchse_dt.data
        gear.price = gear_form.price.data
        gear.retired = gear_form.retired.data
        gear.no_suggest = gear_form.no_suggest.data
        gear.confirmed = gear_form.confirmed.data
        gear.type = gear_type_dict[str(gear_form.type.data)]
        gear.company = gear_form.company.data
        if gear_id is None:
            db.session.add(gear)
        db.session.commit()
        flash('Gear has been updated')
        return redirect(url_for('main.settings'))


    if gear_id is None:
        label_val = 'Create Gear'
        return render_template('edit_gear.html', destPage = 'settings', gear_form=gear_form, gear_usage=None, label_val=label_val)

    try:
        gear = Gear.query.filter_by(id=gear_id, user_id = usr_id).one()
    except:
        flash("Gear not found")
        return redirect(url_for('main.settings'))

    gear_usage = Gear_usage.query.filter_by(gear_id=gear_id, user_id = usr_id).one()
    gear_usage.tot_dur = gear_usage.tot_dur_str()

    for key, value in gear_type_dict.items():
        if value == gear.type:
            default_type = key
            break
    gear_form.type.default = default_type
    gear_form.process()
    gear_form.id.data = gear.id
    gear_form.nm.data = gear.nm
    gear_form.prchse_dt.data = gear.prchse_dt
    gear_form.price.data = gear.price
    gear_form.retired.data = gear.retired
    gear_form.no_suggest.data = gear.no_suggest
    gear_form.confirmed.data = gear.confirmed
    gear_form.company.data = gear.company
    logger.info(gear_form)

    return render_template('edit_gear.html', destPage = 'settings', gear_form=gear_form, gear_usage=gear_usage, label_val=label_val)

@bp.route('/edit_location', methods=['GET','POST'])
@login_required
def edit_location():
    usr_id = current_user.id
    loc_id = request.args.get('location')
    logger.info('edit_location: ' + str(loc_id))

    try:
        location = Location.query.filter_by(id=loc_id, user_id = usr_id).one()
    except:
        flash("Location not found")
        return redirect(url_for('main.settings'))

    loc_form = LocForm()
    label_val = 'Edit Location: {}'.format(location.name)

    if request.method == 'GET':
        logger.info('edit_location GET')
    elif request.method == 'POST' and loc_form.cancel.data:
        logger.info('edit_location POST Cancel button pressed')
        return redirect(url_for('main.settings'))
    elif request.method == 'POST' and loc_form.delete.data:
        logger.info('edit_location POST Delete button pressed')
        db.session.delete(location)
        db.session.commit()
        return redirect(url_for('main.settings'))
    elif request.method == 'POST':
        if not loc_form.validate_on_submit():
            loc_form.lat.data = location.lat
            loc_form.lon.data = location.lon
            return render_template('edit_location.html', destPage = 'settings', loc_form=loc_form, label_val=label_val)
        logger.info('edit_location POST Submit button pressed')
        location.name = loc_form.name.data
        location.radius = loc_form.radius.data
        location.updt_ts = datetime.utcnow()
        db.session.commit()
        flash('Location has been updated')
        return redirect(url_for('main.settings'))

    map_dict = {}
    map_dict['key'] = current_app.config['MAPBOX_API_KEY']
    map_dict['max_zoom'] = current_app.config['MAP_MAX_ZOOM']
    map_dict['zoom'] = current_app.config['LOCATION_MAP_ZOOM']

    loc_form.id.data = location.id
    loc_form.name.data = location.name
    loc_form.lat.data = location.lat
    loc_form.lon.data = location.lon
    loc_form.radius.data = location.radius

    return render_template('edit_location.html', destPage = 'settings', loc_form=loc_form, label_val=label_val, map_dict=map_dict)

@bp.route('/races', methods=['GET'])
def races():
    logger.info('races')
    title="Mike Races"
    destPage="races"
    usr_id = 1
    logger.info(current_user.is_authenticated)
    if current_user.is_authenticated and current_user.id == usr_id :
        usr_logged_in = True
    else:
        usr_logged_in = False

    dash_lst_dict = {}
    query = Workout.query.filter_by(user_id=usr_id).filter(Workout.category_id.in_([4,8]))
    race_results = sorted(query, reverse=False)
    race_lst = []
    race_dist_dict = {}
    for race in race_results:
        if race.training_type != None and race.training_type != '':
            race_dict = race.to_race_graph_dict(public_img_link=True)
            if race.id == 904:
                # remove map for race that was around house
                logger.info(race_dict)
                race_dict['_links'].pop('map_thumb')
            if not usr_logged_in and 'workout_link' in race_dict['_links']:
                race_dict['_links'].pop('workout_link')
            race_lst.append(race_dict)
            if race_dict['distance'] not in race_dist_dict:
                race_dist_dict[race_dict['distance']] = race_dict['dist_mi']
    dash_lst_dict['race_lst'] = race_lst
    logger.info(race_dist_dict)

    states_json_fname = os.path.join(basedir, "static/data/states-10m.json")
    with open(states_json_fname) as states_file:
        states_topo_data = json.load(states_file)
    states_csv_fname = os.path.join(basedir, "static/data/us_states.csv")
    states_data_dict = {}
    with open(states_csv_fname) as states_csv_file:
        csv_reader = csv.DictReader(states_csv_file)
        for row in csv_reader:
            states_data_dict[row['name']] = row

    return render_template('races.html.j2', title=title, 
        destPage=destPage, dash_lst_dict=dash_lst_dict, 
        race_dist_dict=race_dist_dict, 
        states_topo_data=states_topo_data, states_data=states_data_dict
    )
