from shapely.geometry import LineString
from shapely.geometry import Point, MultiPoint, MultiLineString
from shapely.ops import nearest_points


def remove_short_lines(line):
    if line.type == 'MultiLineString':
        passing_lines = []

        for i, linestring in enumerate(line.geoms):
            other_lines = MultiLineString([x for j, x in enumerate(line.geoms)
                                          if j != i])

            p0 = Point(linestring.coords[0])
            p1 = Point(linestring.coords[-1])

            is_deadend = False

            if p0.disjoint(other_lines):
                is_deadend = True
            if p1.disjoint(other_lines):
                is_deadend = True

            if not is_deadend or linestring.length > 5:
                passing_lines.append(linestring)

        return MultiLineString(passing_lines)

    if line.type == 'LineString':
        return line


def linestring_to_segments(linestring):
    return [LineString([linestring.coords[i], linestring.coords[i+1]])
            for i in range(len(linestring.coords) - 1)]


def get_segments(line):
    line_segments = []

    if line.type == 'MultiLineString':
        for linestring in line.geoms:
            line_segments.extend(linestring_to_segments(linestring))

    if line.type == 'LineString':
        line_segments.extend(linestring_to_segments(line))

    return line_segments


def interpolate_by_distance(linestring):
    distance = 1
    all_points = []
    count = round(linestring.length / distance) + 1

    if count == 1:
        all_points.append(linestring.interpolate(linestring.length / 2))
    else:
        for i in range(count):
            all_points.append(linestring.interpolate(distance * i))

    return all_points


def interpolate(line):
    if line.type == 'MultiLineString':
        all_points = []

        for linestring in line:
            all_points.extend(interpolate_by_distance(linestring))

        return MultiPoint(all_points)

    if line.type == 'LineString':
        return MultiPoint(interpolate_by_distance(line))


def polygon_to_multilinestring(polygon):
    return MultiLineString([polygon.exterior] + [line for line in
                                                 polygon.interiors])


def get_avg_distances(row):
    avg_distances = []

    sidewalk_lines = polygon_to_multilinestring(row.geometry)

    for segment in row.segments:
        points = interpolate(segment)

        distances = []

        for point in points.geoms:
            p1, p2 = nearest_points(sidewalk_lines, point)
            distances.append(p1.distance(p2))

        avg_distances.append(sum(distances) / len(distances))

    return avg_distances
