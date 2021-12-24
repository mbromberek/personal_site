# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# First party classes
import csv
import io
import os

# Third party classes
from flask import current_app

# Custom classes
from app.main import bp
from app.models import User, Workout, Workout_interval, Gear_usage, Wrkt_sum, Wkly_mileage
from app import logger
from app.main.forms import WorkoutExportForm

'''
Generate a CSV formatted file in memory of the workouts passed
'''
def wrkt_lst_to_csv(wrkt_lst, export_form):
    export_fields = ['Date','Type']

    # Fields will be in same order on csv as declared in the export_form
    # Loop through all items in export_form
    for attr, value in export_form.__dict__.items():
        # Check if any whose atrributes end in _chk are checked
        if attr.endswith('_chk'):
            # logger.debug('{}, {}'.format(attr, value))
            if value.data == True:
                export_fields.append(value.label.text)

    # Convert passed in workouts to a list of dictionaries
    wrkt_dict_lst = []
    for wrkt in wrkt_lst:
        wrkt_dict_lst.append(wrkt.to_dict_export(export_fields))

    # Get CSV Header row
    keys = export_fields

    # Generate CSV in the string field output_string
    output_string = io.StringIO()
    dict_writer = csv.DictWriter(output_string, keys)
    dict_writer.writeheader()
    dict_writer.writerows(wrkt_dict_lst)

    # Need to convert output_string to bytes for sending with send_file
    mem = io.BytesIO()
    mem.write(output_string.getvalue().encode())
    mem.seek(0)
    output_string.close()

    return mem
