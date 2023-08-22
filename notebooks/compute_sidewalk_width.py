# Select where to run notebook: "azure" or "local"
my_run = "azure"

# Select whether or not to do parallel processing
parallel = True

import set_path  # add project src to path

import numpy as np
import os
import pathlib
import pickle
import pandas as pd
import geopandas as gpd
from tqdm.notebook import tqdm_notebook
tqdm_notebook.pandas()
import shapely.ops as so
import shapely.geometry as sg

import upcp.utils.bgt_utils as bgt_utils
import upcp.utils.las_utils as las_utils

import upc_sw.poly_utils as poly_utils

if my_run == "azure":
    import config_azure as cf
elif my_run == "local":
    import config as cf

if parallel:
    import dask_geopandas as dgpd
    from dask.diagnostics import ProgressBar
    pbar = ProgressBar()
    pbar.register()

import warnings  # temporary, to supress deprecationwarnings from shapely
warnings.filterwarnings('ignore')

# Create folder if it doesn't exist
pathlib.Path(cf.out_folder).mkdir(parents=True, exist_ok=True)

print('start reading obstacle data')
# Read sidewalk with obstacle data
df = gpd.read_file(cf.obstacle_file, geometry='geometry', crs=cf.CRS)
print('done reading obstacle data')

if cf.merge_sidewalks:
    # Merge sidewalk polygons
    df = gpd.GeoDataFrame(geometry=gpd.GeoSeries([geom for geom in df.unary_union.geoms]), crs=cf.CRS)
    df['ogc_fid'] = range(0, len(df))  
    
else:
    # Explode MultiPolygons into their parts
    df = df.explode(index_parts=False)

# Ignore sidewalk polygons that are too small
df = df[df.area > cf.min_area_size]


def get_points_on_line(line, distance_delta):  
    # Generate equidistant points
    distances = np.arange(0, line.length, distance_delta)
    points = sg.MultiPoint([line.interpolate(distance) for distance in distances])
    return points

def split_line_by_points(line, points, tolerance: float=0.001):
    return so.split(so.snap(line, points, tolerance), points)


def get_segments_width_cut(row, max_seg_length):
    # Get centerlines.
    cl = poly_utils.get_centerlines(row.geometry)
    # Merge linestrings.
    cl = so.linemerge(cl)
    # Remove short line ends and dead-ends.
    cl = poly_utils.remove_short_lines(cl, cf.min_se_length)
    # Simplify lines.
    cl = cl.simplify(cf.simplify_tolerance, preserve_topology=True)
    # Segment lines 
    segments_long = poly_utils.get_segments(cl)   
    # Cut segments (with maximum segment length)
    segments = []
    for seg in segments_long:
        points_on_line = get_points_on_line(seg, max_seg_length)
        seg_cut = split_line_by_points(seg, points_on_line)
        segments.extend(seg_cut)
    # Compute avg and min width per cut segment   
    avg_width, min_width = poly_utils.get_avg_width(
                    row.geometry, segments, cf.width_resolution, cf.width_precision)
    return {'segments_long': segments_long, 'segments': segments, 
            'avg_width': avg_width, 'min_width': min_width, 'sidewalk_id': row.ogc_fid}      

print('start getting segments and width')
# if you get an error here, make sure you use tqdm>=4.61.2
if parallel:
    ddf = dgpd.from_geopandas(df, npartitions=24)
    segment_df = pd.DataFrame((ddf.apply(get_segments_width_cut, 
                                         max_seg_length=cf.max_seg_length,
                                         axis=1, meta=(object)).compute().values.tolist()))
else:
    segment_df = pd.DataFrame(df.progress_apply(get_segments_width_cut, 
                                                max_seg_length=cf.max_seg_length,                                                     
                                                axis=1).values.tolist())

with open(cf.tmp_file, 'wb') as f:
    pickle.dump(segment_df.to_dict(), f)  
    
print('done getting segments and width')      

segment_df = pd.concat([gpd.GeoDataFrame({'geometry': row.segments,
                                          'avg_width': row.avg_width,
                                          'min_width': row.min_width,
                                          'sidewalk_id': row.sidewalk_id} 
                                        )
                         for _, row in segment_df.iterrows()],
                       ignore_index=True)
segment_df.set_crs(crs=cf.CRS, inplace=True);

with open(cf.tmp_file, 'wb') as f:
    pickle.dump(segment_df.to_dict(), f)

# Get a list of all tilecodes for which we have two runs
if my_run == "azure":
    df1 = pd.read_csv(f'{cf.pc_data_folder}AMS_run1_tiles_list.csv')
    df2 = pd.read_csv(f'{cf.pc_data_folder}AMS_run2_tiles_list.csv')
    all_tiles = set(list(df1['tilecode'])).intersection(set(list(df2['tilecode'])))
elif my_run == "local":
    all_tiles = (las_utils.get_tilecodes_from_folder(f'{cf.pc_data_folder}run1/', las_prefix='processed')
                .intersection(las_utils.get_tilecodes_from_folder(f'{cf.pc_data_folder}run2/', las_prefix='processed')))

# Get polygon of all these tiles
all_tiles_poly = so.unary_union([poly_utils.tilecode_to_poly(tile) for tile in all_tiles])

# Check whether segments are within polygon of tiles
segment_df['pc_coverage'] = segment_df.intersects(all_tiles_poly)
segment_df['pc_coverage'].value_counts()

# Store
segment_df.to_file(cf.segments_file, driver='GPKG')

# Delete intermediate output
if os.path.exists(cf.tmp_file):
    os.remove(cf.tmp_file)

