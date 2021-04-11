# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# First party classes
from datetime import datetime
import math
import re

# Custom classes
from app.utils.const import SECONDS_IN_HOUR, SECONDS_IN_MINUTE

def sec_to_time(tm_sec, format='hms'):
    '''
    Convert passed in time from seconds to time string in format ##h ##m ##s
    '''
    hours = math.floor(tm_sec / SECONDS_IN_HOUR)
    minutes = math.floor((tm_sec % SECONDS_IN_HOUR) / SECONDS_IN_MINUTE)
    seconds = (tm_sec % SECONDS_IN_HOUR) % SECONDS_IN_MINUTE

    tm_str = str(hours) + 'h ' + str(minutes).zfill(2) + 'm ' + str(seconds).zfill(2) + 's'
    return tm_str

def time_str_to_sec(tm_str):
    '''
    Convert passed in time string from format ##h ##m ##s to seconds
    '''

    hours_sec = int(re.search('(\d*)h', tm_str).group(1))*SECONDS_IN_HOUR if re.search('(\d*)h', tm_str) else 0
    minutes_sec = int(re.search('(\d*)m', tm_str).group(1))*SECONDS_IN_MINUTE if re.search('(\d*)m', tm_str) else 0
    seconds = int(re.search('(\d*)s', tm_str).group(1)) if re.search('(\d*)s', tm_str) else 0

    tm_sec = hours_sec + minutes_sec + seconds

    return tm_sec

def time_to_sec(h=0, m=0, s=0):
    if h == '':
        h=0
    if m == '':
        m=0
    if s == '':
        s=0
    duration = time_str_to_sec(
        str(h) + 'h ' + str(m) + 'm ' + str(s) + 's'
    )
    return duration