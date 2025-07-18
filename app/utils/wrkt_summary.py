# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# Third party classes
import pandas as pd

# Custom classes
from app import logger
from app.utils import tm_conv
from app.models import Workout, Workout_interval
from app.model.tag import Tag


def summarize_workout(df, sum_desc=''):
    df_edit = df.copy()
    df_edit['dist_mi'] = pd.to_numeric(df_edit.dist_mi)
    df_edit['ele_up'] = pd.to_numeric(df_edit.ele_up)
    df_edit['ele_down'] = pd.to_numeric(df_edit.ele_down)
    df_edit['hr'] = pd.to_numeric(df_edit.hr)
    grouped_df = (df_edit.groupby(
        ['workout_id','break_type'])
        .agg(dur_sec=('dur_sec','sum')
            , dist_mi=('dist_mi','sum')
            , ele_up=('ele_up','sum')
            , ele_down=('ele_down','sum')
            , hr=('hr','mean')
        ).reset_index()
    )
    grouped_df['det'] = sum_desc

    sum_row = grouped_df.to_dict(orient='index')[0]
    sum_row['duration'] = tm_conv.sec_to_time(sum_row['dur_sec'],'ms')
    sum_row['pace'] = tm_conv.sec_to_time(tm_conv.pace_calc(sum_row['dist_mi'], sum_row['dur_sec']), 'ms')

    return sum_row

def summarize_workout_section(df, sum_desc=''):
    df_edit = df.copy()
    df_edit['dist_mi'] = pd.to_numeric(df_edit.dist_mi)
    df_edit['ele_up'] = pd.to_numeric(df_edit.ele_up) if 'ele_up' in df_edit else 0
    df_edit['ele_down'] = pd.to_numeric(df_edit.ele_down) if 'ele_down' in df_edit else 0
    df_edit['hr'] = pd.to_numeric(df_edit.hr) if 'hr' in df_edit else 0
    grouped_df = (df_edit.groupby(
        ['break_type'])
        .agg(dur_sec_min=('dur_sec','min')
            , dist_mi_min=('dist_mi','min')
            , dur_sec_max=('dur_sec','max')
            , dist_mi_max=('dist_mi','max')
            , ele_up=('ele_up','sum')
            , ele_down=('ele_down','sum')
            , hr=('hr','mean')
        ).reset_index()
    )
    grouped_df['det'] = grouped_df['break_type']
    grouped_df['dur_sec'] = grouped_df['dur_sec_max'] - grouped_df['dur_sec_min']
    grouped_df['dist_mi'] = grouped_df['dist_mi_max'] - grouped_df['dist_mi_min']

    sum_lst = grouped_df.to_dict(orient='records')
    for sum_row in sum_lst:
        sum_row['duration'] = tm_conv.sec_to_time(sum_row['dur_sec'],'ms')
        sum_row['pace'] = tm_conv.sec_to_time(tm_conv.pace_calc(sum_row['dist_mi'], sum_row['dur_sec']), 'ms')

    return sum_lst

def get_lap_sum(intrvl_lst):
    sum_lst = []
    tot_df = pd.DataFrame(Workout_interval.to_intrvl_lst_dict(intrvl_lst))
    # logger.debug(tot_df.info())
    # logger.debug(tot_df)

    # Calculate without warm up and cool down intervals
    non_wrkt_lbl_lst = ['Warm Up','Cool Down','Jog','Recovery','Rest']
    if (tot_df['interval_desc'].isin(non_wrkt_lbl_lst)).any():
        workout_df = tot_df.loc[~tot_df['interval_desc'].isin(non_wrkt_lbl_lst)]
        itrvl_sum_wrkt = summarize_workout(workout_df, 'Workout')
        sum_lst.append(itrvl_sum_wrkt)

    # itrvl_sum_tot['interval_desc'].value_counts()
    # itrvl_sum_tot.group_by('interval_desc').count()
    # get_sum_by_intrvl(itrvl_sum_tot)
    sum_lst.extend(get_sum_by_intrvl(tot_df))

    # Calculate summary for total intervals
    itrvl_sum_tot = summarize_workout(tot_df, 'Total')
    sum_lst.append(itrvl_sum_tot)
    
    return sum_lst

def get_mile_sum(intrvl_lst):
    sum_lst = []
    tot_df = pd.DataFrame(Workout_interval.to_intrvl_lst_dict(intrvl_lst))

    # subtract 1 from result of (nbr rows /2) since interval_order starts at 0
    firsthalf_df = tot_df.loc[tot_df['interval_order']<=tot_df.shape[0]/2-1]
    secondhalf_df = tot_df.loc[tot_df['interval_order']>tot_df.shape[0]/2-1]

    if firsthalf_df.shape[0] > 0:
        itrvl_sum_firsthalf = summarize_workout(firsthalf_df, 'First½')
        sum_lst.append(itrvl_sum_firsthalf)
    
    if secondhalf_df.shape[0] > 0:
        itrvl_sum_secondhalf = summarize_workout(secondhalf_df, 'Sec½')
        sum_lst.append(itrvl_sum_secondhalf)

    itrvl_sum_tot = summarize_workout(tot_df, 'Total')
    sum_lst.append(itrvl_sum_tot)

    return sum_lst

def generate_workout_tags(wrkt_df):
    tag_dict = []
    split_type_map = {'Negative Splits':'Negative Splits ✅','Positive Splits':'Positive Splits 👍','Even Splits':'Even Splits 😮'}
    sum_mile = get_mile_sum_from_df(wrkt_df)
    for summary in sum_mile:
        if 'det' in summary and summary['det'] in ['Negative Splits','Positive Splits','Even Splits']:
            tag_dict.append(Tag.get_tag_id(split_type_map[summary['det']]))
    
    return tag_dict

def get_mile_sum_from_df(wrkt_df):
    sum_lst = []
    tot_df = wrkt_df.copy()

    tot_dist = tot_df['dist_mi'].values[-1]
    tot_df.loc[tot_df['dist_mi'] <=tot_dist/2, 'break_type'] = 'First½'
    tot_df.loc[tot_df['dist_mi'] >tot_dist/2, 'break_type'] = 'Sec½'
    first_second_half_split = summarize_workout_section(tot_df)
    sum_lst.extend(first_second_half_split)
    half_split_dur_sec = first_second_half_split[1]['dur_sec'] - first_second_half_split[0]['dur_sec']
    half_split_dur_str = tm_conv.sec_to_time(abs(half_split_dur_sec),'ms')
    
    if half_split_dur_sec <0:
        sum_lst.append({'det':'Negative Splits','duration':half_split_dur_str})
    elif half_split_dur_sec >0:
        sum_lst.append({'det':'Positive Splits','duration':half_split_dur_str})
    else:
        sum_lst.append({'det':'Even Splits','duration':half_split_dur_str})

    tot_df['break_type'] = 'Total'
    sum_lst.extend(summarize_workout_section(tot_df, 'Total'))

    nbr_rows = round(tot_df.shape[0]/2)
    return sum_lst

def get_sum_by_intrvl(df):
    df_edit = df.copy()

    df_edit['dist_mi'] = pd.to_numeric(df_edit.dist_mi)
    df_edit['ele_up'] = pd.to_numeric(df_edit.ele_up)
    df_edit['ele_down'] = pd.to_numeric(df_edit.ele_down)
    df_edit['hr'] = pd.to_numeric(df_edit.hr)
    grouped_df = (df_edit.groupby(
        ['workout_id','break_type','interval_desc'])
        .agg(dur_sec=('dur_sec','mean')
            , dist_mi=('dist_mi','mean')
            , ele_up=('ele_up','mean')
            , ele_down=('ele_down','mean')
            , hr=('hr','mean')
            , ct=('dur_sec','count')
        ).reset_index()
    )
    intrvl_sum_lst = grouped_df.to_dict(orient='records')
    intrvl_sum_edit_lst = []
    # print(intrvl_sum_lst)
    for intrvl_sum in intrvl_sum_lst:
        # print(intrvl_sum)
        if intrvl_sum['ct'] >1 and intrvl_sum['interval_desc'] != '':
            intrvl_sum['det'] = intrvl_sum['interval_desc']
            intrvl_sum['duration'] = tm_conv.sec_to_time(intrvl_sum['dur_sec'],'ms')
            intrvl_sum['pace'] = tm_conv.sec_to_time(tm_conv.pace_calc(intrvl_sum['dist_mi'], intrvl_sum['dur_sec']), 'ms')
            intrvl_sum_edit_lst.append(intrvl_sum)

    # print('intrvl_sum_edit_lst')
    # print(intrvl_sum_edit_lst)
    return intrvl_sum_edit_lst
