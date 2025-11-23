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
import shutil
from datetime import datetime
import json

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

'''
Returns directory that export was loaded into
'''
def wrkt_lst_to_json(wrkt_lst, user_id):
    wrkt_dict_lst = []
    exportTmStr = datetime.now().strftime('%Y-%m-%d_%H%M%S') + '_' + 'export' + '_' + str(user_id)
    exportDir = os.path.join(current_app.config['WRKT_FILE_DIR'], str(user_id), 'export', exportTmStr)
    if not os.path.exists(exportDir):
        # os.makedirs(os.path.join(current_app.config['WRKT_FILE_DIR'], str(user_id), 'export'), exportTmStr)
        os.makedirs(exportDir)
    # exportFile = os.path.join(exportDir, 'export.json')
    thumbDir = os.path.join(current_app.config['WRKT_FILE_DIR'], str(user_id), current_app.config['USER_THUMBNAIL_DIR'])

    for wrkt in wrkt_lst:
        wrkt_dict = wrkt.to_dict(include_calc_fields=True)
        wrkt_dict['intervals'] = []
        for interval in wrkt.workout_intervals:
            wrkt_dict['intervals'].append(interval.to_dict())
        wrktYear = wrkt.wrkt_dttm.strftime('%Y')
        wrktId = wrkt.wrkt_dttm.strftime('%Y-%m-%d_%H%M%S') + '_' + wrkt.type_det.nm
        wrktDir = os.path.join(exportDir, wrktYear, wrktId)
        if not os.path.exists(wrktDir):
            os.makedirs(wrktDir)
        exportFileName = os.path.join(wrktDir, wrktId+'.json')
        with open(exportFileName, 'w') as fp:
            json.dump(wrkt_dict, fp)
        # Get .fit file to save in directory
        # wrkt.wrkt_dir
        
        # Get thumbnail to save in directory
        if wrkt.thumb_path != None:
            logger.info(wrkt.thumb_path)
            shutil.copyfile(os.path.join(thumbDir, wrkt.thumb_path), os.path.join(wrktDir, wrkt.thumb_path))
        
        
    return exportDir
