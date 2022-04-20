import shapely.geometry as sg
import shapely.ops as so
from centerline.geometry import Centerline
import numpy as np
import pandas as pd

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

    return pd.Series([np.round(avg_width, precision),
                      np.round(min_width, precision)])
