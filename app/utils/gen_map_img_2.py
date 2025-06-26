# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# First party classes
import os, sys

# Third party classes
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio

THUMB_DIM = {'height':200, 'width':200}
IMG_DIM_DFT = {'height':1500, 'width':1500}

def calc_center(lons: tuple, lats: tuple) -> (dict):
    lon_max, lon_min = max(lons), min(lons)
    lat_max, lat_min = max(lats), min(lats)
    center_lat = (lat_max + lat_min) /2
    center_lon = (lon_max + lon_min) /2

    map_center={'lat':center_lat, 'lon':center_lon}
    return map_center

def calc_zoom(lons: tuple, lats: tuple, projection: str='mercator',
        img_dim=IMG_DIM_DFT) -> (float):
    # Function is based on solution from code from https://stackoverflow.com/questions/63787612/plotly-automatic-zooming-for-mapbox-maps
    """Finds optimal zoom and centering for a plotly mapbox.
    Parameters
    --------
    lons: tuple, required, longitude component of each location
    lats: tuple, required, latitude component of each location
    projection: str, only accepting 'mercator' at the moment,
        raises `NotImplementedError` if other is passed

    Returns
    --------
    zoom: float, from 1 to 20

    >>> print(zoom_center((-109.031387, -103.385460),
    ...     (25.587101, 31.784620)))
    (5.75, {'lon': -106.208423, 'lat': 28.685861})
    """

    maxlon, minlon = max(lons), min(lons)
    maxlat, minlat = max(lats), min(lats)

    # longitudinal range by zoom level (20 to 1)
    # in degrees, if centered at equator and output image is 1500x1500
    lon_zoom_range = np.array([
        0.0007, 0.0014, 0.003, 0.006, 0.012, 0.024, 0.048, 0.096,
        0.192, 0.3712, 0.768, 1.536, 3.072, 6.144, 11.8784, 23.7568,
        47.5136, 98.304, 190.0544, 360.0
    ])

    if projection == 'mercator':
        height_dim_ratio = IMG_DIM_DFT['height'] / img_dim['height']
        width_dim_ratio = IMG_DIM_DFT['width'] / img_dim['width']
        # print('Height ratio: ' + str(height_dim_ratio) + ' Width ratio: ' + str(width_dim_ratio))
        width_to_height = img_dim['width'] / img_dim['height']
        margin = 1.2
        # margin=0.5
        height = (maxlat - minlat) * margin * width_to_height * height_dim_ratio
        width = (maxlon - minlon) * margin  * width_dim_ratio
        # print('Height: ' + str(height) + ' Width: ' + str(width))

        lon_zoom = np.interp(width , lon_zoom_range, range(20, 0, -1))
        lat_zoom = np.interp(height, lon_zoom_range, range(20, 0, -1))
        # print('lon_zoom: ' + str(lon_zoom) + ' lat_zoom: ' + str(lat_zoom))
        zoom = round(min(lon_zoom, lat_zoom), 2)
    else:
        raise NotImplementedError(
            f'{projection} projection is not implemented'
        )

    return zoom

def generate_map_img(df, img_dest, img_dim=IMG_DIM_DFT, img_name='image.png'):
    run_df = df.copy()

    lat_max = run_df['latitude'].max()
    lat_min = run_df['latitude'].min()
    lon_max = run_df['longitude'].max()
    lon_min = run_df['longitude'].min()

    map_center = calc_center(lats=[lat_max, lat_min], lons=[lon_max, lon_min])
    map_zoom = calc_zoom(lats=[lat_min, lat_max], lons=[lon_min, lon_max], img_dim=img_dim)

    print('zoom: ' + str(map_zoom))
    print('center:' + str(map_center))

    run_line_map = px.line_mapbox(run_df, lat="latitude", lon="longitude", center=map_center, mapbox_style="open-street-map", zoom=map_zoom, height = img_dim['height'], width = img_dim['width'])
    run_line_map.layout.margin = dict(t=0, b=0, l=0, r=0)
    run_line_map.update_traces(line=dict(color="Red", width=2))
    run_line_map.write_image(os.path.join(img_dest, img_name))

def main(argv):
    # print(argv[0])
    run_df = pd.read_pickle(os.path.join(argv[0], 'workout.pickle'))
    img_dest = argv[0]
    generate_map_img(run_df, img_dest, img_dim=THUMB_DIM, img_name='thumb.png')

if __name__ == '__main__':
	main(sys.argv[1:])
