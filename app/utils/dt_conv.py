# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# First party classes
from datetime import datetime

def get_date(s_date):
    date_patterns = ['%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d']

    for pattern in date_patterns:
        try:
            return datetime.strptime(s_date, pattern)
        except:
            pass

    raise ValueError("Entered date is not in valid format")

def date_str(dttm):
    date_patterns = '%Y-%m-%d'
    return datetime.strftime(dttm, date_patterns)
