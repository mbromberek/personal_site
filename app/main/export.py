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

'''
Generate a CSV formatted file in memory of the workouts passed
'''
def wrkt_lst_to_csv(wrkt_lst, export_fields):
    # Fields will be in same order on csv as in the export_fields list

    # out_file_path = os.path.join(current_app.config['FILE_DOWNLOAD_DIR'],out_fname)

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
