# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# First party classes
import csv
import os

# Third party classes
from flask import current_app

# Custom classes
from app.main import bp
from app.models import User, Workout, Workout_interval, Gear_usage, Wrkt_sum, Wkly_mileage
from app import logger


def wrkt_lst_to_csv(wrkt_lst, export_fields, output_file, delimiter=','):
    # Fields will be in same order on csv as in the export_fields list

    # Convert passed in workouts to a list of dictionaries
    # TODO how to handle fields that are not in model like pace_str and notes w/clothes and weather
    wrkt_dict_lst = []
    for wrkt in wrkt_lst:
        wrkt_dict_lst.append(wrkt.to_dict_fields(export_fields))

    # Get CSV Header row
    # TODO should keys be based on the dictionary or using the export_fields? If using export_fields need to be sure how things work when a field is in export_fields but will not be in dictionary
    # keys = wrkt_dict_lst[0].keys()
    keys = export_fields

    # Create and populate CSV
    with open(os.path.join(current_app['FILE_DOWNLOAD_DIR'],'workouts.csv'), 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(wrkt_dict_lst)

    return True
