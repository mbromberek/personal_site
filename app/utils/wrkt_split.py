# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# 3rd Party classes
import pandas as pd
import numpy as np

# Custom Classes from github
import NormalizeWorkout.WrktSplits as wrktSplits

def split_lap(wrkt_pickle, lap_nbr, split_dist):
    wrkt_df = pd.read_pickle(wrkt_pickle)

    min_lap_dist_m = wrkt_df.loc[wrkt_df['lap'] == lap_nbr]['dist_m'].min()

    # convert split_dist from miles to meters
    split_dist_meters = float(split_dist) * 1609.344

    # Add min_dist to dist split_dist to get split_tot_dist
    tot_split_dist_m = min_lap_dist_m + split_dist_meters

    # Update lap where dist >= split_tot_dist to lap+1 
    #    (this takes care of creating new lap and incrementing existing ones)
    wrkt_df['lap_updt'] = wrkt_df.loc[wrkt_df['dist_m'] >= tot_split_dist_m]['lap'] +1
    wrkt_df['lap'] = np.where(pd.notnull(wrkt_df['lap_updt']), wrkt_df['lap_updt'], wrkt_df['lap']).astype('int')
    # wrkt_df.drop('lap_updt', axis=1, inplace=True)

    # Calculate interval splits
    lap_df = wrktSplits.group_actv(wrkt_df, 'lap')

    # Get two updated/new laps and return them as a list
    lap_df.rename(columns={'avg_hr':'hr'}, inplace=True)

    lap_to_ret = lap_df[lap_df['lap'].isin([lap_nbr, lap_nbr+1])]
    laps = lap_to_ret.to_dict(orient='records')

    return laps