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
from app.utils.const import METERS_TO_MILES

def dist_to_meters(dist_orig, dist_orig_uom):
  if dist_orig_uom.lower() in ['mile','miles']:
    return dist_orig / METERS_TO_MILES
  elif dist_orig_uom.lower() in ['meter','meters']:
    return dist_orig
  return dist_orig