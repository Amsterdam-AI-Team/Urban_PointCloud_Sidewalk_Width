import numpy as np
import laspy

from upcp.utils import clip_utils


def sidewalk_clip(points, tilecode, sw_poly_reader,
                  ahn_reader=None, max_height=2.0):
    sw_mask = np.zeros((len(points),), dtype=bool)

    sw_polys = sw_poly_reader.filter_tile(tilecode, bgt_types=['voetpad'],
                                          merge=True)
    if len(sw_polys) == 0:
        print(f'No sidewalk polygons for tile {tilecode}.')
        return sw_mask

    for polygon in sw_polys:
        clip_mask = clip_utils.poly_clip(points, polygon)
        sw_mask = sw_mask | clip_mask

    if ahn_reader is not None:
        sw_ids = np.where(sw_mask)[0]
        ahn_mask = np.zeros((len(sw_ids),), dtype=bool)
        gnd_z = ahn_reader.interpolate(tilecode, points[sw_ids, :],
                                       surface='ground_surface')
        gnd_z_valid = np.isfinite(gnd_z)
        gnd_z_val_ids = np.where(gnd_z_valid)[0]
        # Every point between 0 and max_height above ground plane.
        # First, check points with valid elevation data.
        valid_mask = ((gnd_z[gnd_z_valid] < points[sw_ids[gnd_z_valid], 2])
                      & (points[sw_ids[gnd_z_valid], 2]
                         <= gnd_z[gnd_z_valid] + max_height))
        ahn_mask[gnd_z_val_ids[valid_mask]] = True
        # TODO: do something clever for points without AHN data.
        # Next, check remaining points to lie between min and max elevation.
        # if np.count_nonzero(gnd_z_valid) > 0:
        #     gnd_min = np.min(gnd_z)
        #     gnd_max = np.max(gnd_z)
        #     inval_mask = ((gnd_min < points[sw_ids[~gnd_z_valid], 2])
        #                   & (points[sw_ids[~gnd_z_valid], 2]
        #                      <= gnd_max + max_height))
        #     ahn_mask[~gnd_z_valid][inval_mask] = True
        sw_mask[sw_ids] = ahn_mask

    print(f'{np.count_nonzero(sw_mask)} points clipped in '
          + f'{len(sw_polys)} sidewalk polygons.')

    return sw_mask


def create_label_mask(labels, target_labels=None, exclude_labels=None):
    """Create mask based on `target_labels` or `exclude_labels`."""
    if (target_labels is not None) and (exclude_labels is not None):
        print('Please provide either target_labels or exclude_labels, '
              + 'but not both.')
        return None
    elif target_labels is not None:
        mask = np.zeros((len(labels),), dtype=bool)
        for label in target_labels:
            mask = mask | (labels == label)
        return mask
    else:
        mask = np.ones((len(labels),), dtype=bool)
        for label in exclude_labels:
            mask = mask & (labels != label)
        return mask


def read_las(las_path, extra_val='label', extra_val_dtype='uint16'):
    pointcloud = laspy.read(las_path)

    if extra_val not in pointcloud.point_format.dimension_names:
        values = np.zeros((pointcloud.header.point_count,),
                          dtype=extra_val_dtype)
    else:
        values = pointcloud[extra_val]

    points = np.vstack((pointcloud.x, pointcloud.y, pointcloud.z)).T

    return points, values


def write_las(points, las_path, extra_val='label', extra_val_dtype='uint16',
              extra_val_desc='Labels', values=None):
    outfile = laspy.create(file_version="1.2", point_format=3)
    outfile.x = points[:, 0]
    outfile.y = points[:, 1]
    outfile.z = points[:, 2]
    if values is not None:
        outfile.add_extra_dim(laspy.ExtraBytesParams(name=extra_val,
                                                     type=extra_val_dtype,
                              description=extra_val_desc))
        outfile[extra_val] = values
    outfile.write(las_path)
