import shapely.geometry as sg
import shapely.ops as so

from shapely.geometry import LineString, Point, MultiPoint, MultiLineString, Polygon # TODO: align with above
from shapely.ops import nearest_points

import numpy as np
import pandas as pd

import geopandas as gpd
from geopandas import GeoDataFrame

from upcp.utils import las_utils


def tilecode_to_poly(tilecode):
    ((x1, y2), (x2, y1)) = las_utils.get_bbox_from_tile_code(
                                                    tilecode, padding=0)
    return sg.box(x1, y1, x2, y2)


def fix_invalid(poly):
    orig_multi = type(poly) == sg.MultiPolygon
    if ~poly.is_valid:
        poly = poly.buffer(0)
        if type(poly) == sg.Polygon and orig_multi:
            poly = sg.MultiPolygon([poly])
    return poly


def remove_short_lines(line, max_line_length=5):
    if line.type == 'MultiLineString':
        passing_lines = []

        for i, linestring in enumerate(line.geoms):
            other_lines = sg.MultiLineString(
                            [x for j, x in enumerate(line.geoms) if j != i])

            p0 = sg.Point(linestring.coords[0])
            p1 = sg.Point(linestring.coords[-1])

            is_deadend = False

            if p0.disjoint(other_lines):
                is_deadend = True
            if p1.disjoint(other_lines):
                is_deadend = True

            if not is_deadend or linestring.length > max_line_length:
                passing_lines.append(linestring)

        return sg.MultiLineString(passing_lines)

    if line.type == 'LineString':
        # TODO: if line.length > max_line_length ?
        return line


def linestring_to_segments(linestring):
    return [sg.LineString([linestring.coords[i], linestring.coords[i+1]])
            for i in range(len(linestring.coords) - 1)]


def get_segments(line):
    line_segments = []

    if line.type == 'MultiLineString':
        for linestring in line.geoms:
            line_segments.extend(linestring_to_segments(linestring))

    if line.type == 'LineString':
        line_segments.extend(linestring_to_segments(line))

    return line_segments


def interpolate_by_distance(linestring, resolution=1):
    all_points = []
    count = round(linestring.length / resolution) + 1

    if count == 1:
        all_points.append(linestring.interpolate(linestring.length / 2))
    else:
        for i in range(count):
            all_points.append(linestring.interpolate(resolution * i))

    return all_points


def interpolate(line, resolution=1):
    if line.type == 'MultiLineString':
        all_points = []

        for linestring in line:
            all_points.extend(interpolate_by_distance(linestring, resolution))

        return sg.MultiPoint(all_points)

    if line.type == 'LineString':
        return sg.MultiPoint(interpolate_by_distance(line, resolution))


def polygon_to_multilinestring(polygon):
    return sg.MultiLineString([polygon.exterior]
                              + [line for line in polygon.interiors])


def get_avg_width(row, resolution=1, precision=2):
    avg_width = []
    min_width = []

    sidewalk_lines = polygon_to_multilinestring(row.geometry)

    for segment in row.segments:
        points = interpolate(segment, resolution)

        distances = []

        for point in points.geoms:
            p1, p2 = so.nearest_points(sidewalk_lines, point)
            distances.append(p1.distance(p2))

        avg_width.append(sum(distances) / len(distances) * 2)
        min_width.append(min(distances) * 2)

    return pd.Series([np.round(avg_width, precision),
                      np.round(min_width, precision)])


def get_route_color(route_weight):
    if route_weight == 0: 
        final_color = 'black'  
    elif (route_weight > 0) & (route_weight < 1000): 
        final_color = 'lightgreen'    
    elif (route_weight >= 1000) & (route_weight < 1000000): 
        final_color = 'orange'
    elif route_weight >= 1000000:
        final_color = 'red'
    else:
        final_color = 'purple'
    return final_color


def preprocess_bgt_data(df_raw):
    # Clean polygon format
    df_raw['polygon_clean'] = df_raw['polygon'].str.replace(r'[', '')
    df_raw['polygon_clean'] = df_raw['polygon_clean'].str.replace(r']', '')
    df_raw['polygon_clean'] = df_raw['polygon_clean'].str.replace(r' ', '')
    df_raw['polygon_clean'] = df_raw['polygon_clean'].apply(lambda x: x.split(',')) 

    # Create lon and lat coordinates
    df_raw['lon'] = df_raw['polygon_clean'].apply(lambda x: np.array(x[0:][::2], dtype=np.float32))
    df_raw['lat'] = df_raw['polygon_clean'].apply(lambda x: np.array(x[1:][::2], dtype=np.float32))

    # Create proper polygon geometry from lon and lat
    df_raw['geometry'] = df_raw.apply(lambda x: Polygon(zip(x['lon'], x['lat'])), axis = 1)
    df_raw = GeoDataFrame(df_raw, geometry = 'geometry', crs='epsg:28992')

    # Drop unneccesary columns
    df = df_raw.drop(['polygon', 'polygon_clean', 'lon', 'lat'], axis = 1)
    
    return df


def create_df_centerlines(centerline):
    centerline_list = []
    
    # Create list of all centerlines
    if centerline.type == 'LineString':
        centerline_list.append(centerline)
        
    if centerline.type == 'MultiLineString':
        for line in centerline:
            centerline_list.append(line) 
    
    # Create dataframe from list
    centerline_df = GeoDataFrame(centerline_list, columns=['geometry'])
    
    return centerline_df


def cut(line, distance):
    # Cut a line in two at a distance from its starting point
    if distance <= 0.0 or distance >= line.length:
        return [LineString(line)]
    coords = list(line.coords)
    for i, p in enumerate(coords):
        pd = line.project(Point(p))
        if pd == distance:
            return [
                LineString(coords[:i+1]),
                LineString(coords[i:])]
        if pd > distance:
            cp = line.interpolate(distance)
            return [
                LineString(coords[:i] + [(cp.x, cp.y)]),
                LineString([(cp.x, cp.y)] + coords[i:])]
        

def shorten_linestrings(centerline_df, max_ls_length):
    # Check if we have a linestring that is too long
    while centerline_df['length'].max() > max_ls_length:

        # Select longest linestring
        id_longest_ls = centerline_df['length'].idxmax()
        longest_ls = centerline_df.iloc[[id_longest_ls]]['geometry'].values[0]

        # Cut linestring 
        cut_ls = cut(longest_ls, max_ls_length-0.01)

        # Create dataframe from cut linestrings, including length
        cut_ls_df = GeoDataFrame(cut_ls, columns = ['geometry'])
        cut_ls_df['length'] = cut_ls_df['geometry'].length

        # Remove long linestring that was cut from original dataframe
        centerline_df = centerline_df.drop(index=id_longest_ls)

        # Add dataframe with cut linestrings to original dataframe
        centerline_df = centerline_df.append(cut_ls_df).reset_index(drop=True)
    
    return centerline_df
