import shapely.geometry as sg
import shapely.ops as so
from centerline.geometry import Centerline
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


def extract_interior(poly):
    if poly.interiors:
        int_polys = sg.MultiPolygon([sg.Polygon(list(lr.coords))
                                     for lr in poly.interiors])
        return sg.Polygon(list(poly.exterior.coords)), int_polys
    else:
        return poly, sg.MultiPolygon()


def get_centerlines(polygon):
    ''' Save a NaN value when centerline calculation fails. '''
    try:
        x = Centerline(polygon)
    except Exception as e:
        print(e)  # TODO also print rows.name[0] ??
        x = np.nan
    return x


def remove_short_lines(line, min_se_length=5):
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

            if not is_deadend or linestring.length > min_se_length:
                passing_lines.append(linestring)

        return sg.MultiLineString(passing_lines)

    if line.type == 'LineString':
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


def get_avg_width(poly, segments, resolution=1, precision=2):
    avg_width = []
    min_width = []

    sidewalk_lines = polygon_to_multilinestring(poly)

    for segment in segments:
        points = interpolate(segment, resolution)

        distances = []

        for point in points.geoms:
            p1, p2 = so.nearest_points(sidewalk_lines, point)
            distances.append(p1.distance(p2))

        avg_width.append(sum(distances) / len(distances) * 2)
        min_width.append(min(distances) * 2)

    return np.round(avg_width, precision), np.round(min_width, precision)


def get_avg_width_cl(poly, segments, resolution=1, precision=2):

    sidewalk_lines = polygon_to_multilinestring(poly)

    points = interpolate(segments, resolution)

    distances = []

    for point in points.geoms:
        p1, p2 = so.nearest_points(sidewalk_lines, point)
        distances.append(p1.distance(p2))

    avg_width = sum(distances) / len(distances) * 2
    min_width = min(distances) * 2

    return pd.Series([np.round(avg_width, precision), np.round(min_width, precision)])


def get_route_color(route_weight):
    if route_weight == 0:
        final_color = 'black'
    elif (route_weight > 0) & (route_weight < 1000):
        final_color = 'green'
    elif (route_weight >= 1000) & (route_weight < 1000000):
        final_color = 'lightgreen'
    elif (route_weight >= 1000000) & (route_weight < 1000000000):
        final_color = 'orange'
    elif (route_weight >= 1000000000) & (route_weight < 1000000000000):
        final_color = 'red'
    elif route_weight == 1000000000000:
        final_color = 'darkred'
    elif route_weight > 1000000000000:
        final_color = 'grey'
    else:
        final_color = 'purple'
    return final_color


def create_df_centerlines(centerline):
    centerline_list = []

    # Create list of all sub-centerlines
    if centerline.type == 'LineString':
        centerline_list.append(centerline)

    if centerline.type == 'MultiLineString':
        for line in centerline:
            centerline_list.append(line)

    # Create dataframe from list
    centerline_df = gpd.GeoDataFrame(centerline_list, columns=['geometry'])

    # Add length and route weight columns
    centerline_df['length'] = centerline_df['geometry'].length
    centerline_df['route_weight'] = np.nan

    return centerline_df


def cut(line, distance):
    # Cut a line in two at a distance from its starting point
    if distance <= 0.0 or distance >= line.length:
        return [sg.LineString(line)]
    coords = list(line.coords)
    for i, p in enumerate(coords):
        pd = line.project(sg.Point(p))
        if pd == distance:
            return [
                sg.LineString(coords[:i+1]),
                sg.LineString(coords[i:])]
        if pd > distance:
            cp = line.interpolate(distance)
            return [
                sg.LineString(coords[:i] + [(cp.x, cp.y)]),
                sg.LineString([(cp.x, cp.y)] + coords[i:])]

        
def shorten_linestrings(centerline_df, max_ls_length):
       
    # Check if we have a linestring that is too long
    while centerline_df['length'].max() > max_ls_length:

        # Select longest linestring
        id_longest_ls = centerline_df['length'].idxmax()
        longest_ls = centerline_df.iloc[[id_longest_ls]]['centerlines'].values[0]
        
        # Cut linestring
        cut_ls = cut(longest_ls, max_ls_length-0.01)

        # Create dataframe from cut linestrings, including length
        cut_ls_df = gpd.GeoDataFrame(cut_ls, columns=['centerlines']).set_geometry('centerlines')
        cut_ls_df['length'] = cut_ls_df['centerlines'].length  
        
        # Add index back
        cut_ls_df['index'] = centerline_df['index'][id_longest_ls]

        # Remove long linestring that was cut from original dataframe
        centerline_df = centerline_df.drop(index=id_longest_ls)

        # Add dataframe with cut linestrings to original dataframe
        centerline_df = centerline_df.append(cut_ls_df).reset_index(drop=True)
    return centerline_df


def remove_interiors(polygon, eps):
    list_interiors = []
    
    for interior in polygon.interiors:
        p = sg.Polygon(interior)    
        if p.area > eps:
            list_interiors.append(interior)

    return(sg.Polygon(polygon.exterior.coords, holes=list_interiors))


def create_mls_per_sidewalk(df, crs):
    mls_list = []
    
    for sidewalk_id in df['sidewalk_id'].unique():
        df_segments_id = df[df['sidewalk_id'] == sidewalk_id]
        mls_id = sg.MultiLineString(list(df_segments_id['geometry']))
        mls_list.append(mls_id)
        
    return(GeoDataFrame(geometry=mls_list, crs=crs)) 
