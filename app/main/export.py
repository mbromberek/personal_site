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
import zipfile
from pathlib import Path

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
Returns directory export was created in and name of the zip file containing export data
'''
def wrkt_lst_to_json(wrkt_lst, user_id):
    wrkt_dict_lst = []
    exportDirectoryStr = 'Export_' + str(user_id) + '_' + datetime.now().strftime('%Y-%m-%d_%H%M%S')
    exportFullDirectory = os.path.join(current_app.config['WRKT_FILE_DIR'], str(user_id), 'export', exportDirectoryStr)
    if not os.path.exists(exportFullDirectory):
        # os.makedirs(os.path.join(current_app.config['WRKT_FILE_DIR'], str(user_id), 'export'), exportDirectoryStr)
        os.makedirs(exportFullDirectory)
    # exportFile = os.path.join(exportFullDirectory, 'export.json')
    thumbDir = os.path.join(current_app.config['WRKT_FILE_DIR'], str(user_id), current_app.config['USER_THUMBNAIL_DIR'])

    for wrkt in wrkt_lst:
        wrkt_dict = wrkt.to_dict(include_calc_fields=True)
        wrkt_dict['intervals'] = []
        for interval in wrkt.workout_intervals:
            wrkt_dict['intervals'].append(interval.to_dict())
        wrktYear = wrkt.wrkt_dttm.strftime('%Y')
        wrktId = wrkt.wrkt_dttm.strftime('%Y-%m-%d_%H%M%S') + '_' + wrkt.type_det.nm
        wrktDir = os.path.join(exportFullDirectory, wrktYear, wrktId)
        if not os.path.exists(wrktDir):
            os.makedirs(wrktDir)
        exportFileName = os.path.join(wrktDir, wrktId+'.json')
        with open(exportFileName, 'w') as fp:
            json.dump(wrkt_dict, fp)

        # Get .fit file to save in directory
        if wrkt.wrkt_dir != None:
            workoutFullDir = os.path.join(current_app.config['WRKT_FILE_DIR'], str(user_id), wrkt.wrkt_dir)
            for file in os.listdir(workoutFullDir):
                # Get and uncompress zip files
                if file.lower().endswith('.zip'):
                    folderName = Path(file).stem
                    # print(folderName)
                    z = zipfile.ZipFile(os.path.join(workoutFullDir,file), mode='r')
                    z.extractall(path=os.path.join(workoutFullDir,folderName))
                    # print(os.listdir(os.path.join(workoutFullDir,folderName)))
                    copyFitFile(fromDirectory=os.path.join(workoutFullDir,folderName), toDirectory=wrktDir)
                    deleteDirectory(os.path.join(workoutFullDir,folderName))
        
        # Get thumbnail to save in directory
        if wrkt.thumb_path != None:
            # logger.info(wrkt.thumb_path)
            shutil.copyfile(os.path.join(thumbDir, wrkt.thumb_path), os.path.join(wrktDir, wrkt.thumb_path))
    
    # Zip Export directory and remove directory that was zipped
    print('exportFullDirectory:' + exportFullDirectory)
    exportZipDesintationDirectory = os.path.join(current_app.config['WRKT_FILE_DIR'], str(user_id), 'export')
    print(exportZipDesintationDirectory)
    zipDirectory(exportFullDirectory, os.path.join(exportZipDesintationDirectory, exportDirectoryStr+'.zip'))
    deleteDirectory(exportFullDirectory)
    
    # return os.path.join('..',current_app.config['WRKT_FILE_DIR'], str(user_id), 'export'), exportDirectoryStr+'.zip'
    # read zip file into memory then delete zip file
    exportZipFileFullPath = os.path.join(current_app.config['WRKT_FILE_DIR'], str(user_id), 'export', exportDirectoryStr+'.zip')
    with open(exportZipFileFullPath, 'rb') as f:
        zipContents = f.read()
    os.remove(exportZipFileFullPath)
    return zipContents, exportDirectoryStr+'.zip'
    
def copyFitFile(fromDirectory, toDirectory):
    for file in os.listdir(fromDirectory):
        if file.lower().endswith('.fit'):
            shutil.copyfile(os.path.join(fromDirectory, file), os.path.join(toDirectory, file))

def deleteDirectory(directory):
    shutil.rmtree(directory)

def zip_directory(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, mode='w', compression=zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                # Arcname is the name in the zip file.
                # We want to avoid storing the full path, so we use relative paths.
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)

def zipDirectory(directory_to_zip, zip_path):
    # Get the parent directory and the folder name
    parent_dir = os.path.dirname(directory_to_zip)
    folder_name = os.path.basename(directory_to_zip)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Walk through the directory
        for root, dirs, files in os.walk(directory_to_zip):
            # Create the archive name by taking the path relative to the parent directory
            # This preserves the original folder name as the root in the zip
            for file in files:
                file_path = os.path.join(root, file)
                # arcname is the path within the zip. This makes `folder_name` the root.
                arcname = os.path.join(folder_name, os.path.relpath(file_path, directory_to_zip))
                zipf.write(file_path, arcname)