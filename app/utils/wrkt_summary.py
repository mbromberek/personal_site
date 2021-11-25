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
