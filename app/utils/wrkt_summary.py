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

def get_lap_sum(intrvl_lst):
    sum_lst = []
    tot_df = pd.DataFrame(Workout_interval.to_intrvl_lst_dict(intrvl_lst))
    # logger.debug(tot_df.info())
    # logger.debug(tot_df)

    # Calculate summary for total intervals
    itrvl_sum_tot = summarize_workout(tot_df, 'Total')
    sum_lst.append(itrvl_sum_tot)

    # Calculate without warm up and cool down intervals
    workout_df = tot_df.loc[~tot_df['interval_desc'].isin(['Warm Up','Cool Down'])]
    itrvl_sum_wrkt = summarize_workout(workout_df, 'Workout')
    sum_lst.append(itrvl_sum_wrkt)

    return sum_lst
