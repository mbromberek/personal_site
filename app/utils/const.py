# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

SECONDS_IN_DAY = 86400
SECONDS_IN_HOUR = 3600
SECONDS_IN_MINUTE = 60
NBR_WK_COMP = 10
MIN_YR_COMP = 2018
NBR_MO_COMP = 15
SLOWEST_PACE = 1800

EXPORT_FIELDS = ['Type','Date','Duration h:m:s','Duration Seconds','Distance','Pace', 'Pace Seconds', 'Gear','HR','Category','Calories', 'Notes','Notes+','Elevation', 'Elevation Up', 'Elevation Down', 'Location', 'Training Type', 'Weather','Clothes']
EXPORT_FIELD_MAPPING = {
    'Type':'type',
    'Date':'wrkt_dttm',
    'Duration h:m:s':'duration',
    'Duration Seconds':'dur_sec',
    'Distance':'dist_mi',
    'Pace':'pace',
    'Pace Seconds':'pace_sec',
    'Gear':'gear',
    'HR':'hr',
    'Category':'category',
    'Calories':'cal_burn',
    'Elevation Up':'ele_up',
    'Elevation Down':'ele_down',
    'Elevation':'elevation',
    'Location':'location',
    'Training Type':'training_type',
    'Weather':'weather',
    'Notes+':'notes+',
    'Notes':'notes',
    'Clothes':'clothes'
}
