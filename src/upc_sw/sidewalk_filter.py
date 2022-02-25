import numpy as np

from upcp.utils import clip_utils

def get_label_mask(points, mask, tilecode, sidewalk_polygons, ahn_reader, max_obstacle_height):    
    label_mask = np.zeros((len(points),), dtype=bool)

    if mask is None:
        mask = np.ones((len(points),), dtype=bool)
    mask_ids = np.where(mask)[0]

    obstacle_mask = np.zeros((len(mask_ids),), dtype=bool)
    for polygon in sidewalk_polygons:
        clip_mask = clip_utils.poly_clip(points[mask, :], polygon)
        obstacle_mask = obstacle_mask | clip_mask

    if ahn_reader is not None:
        bld_z = ahn_reader.interpolate(
            tilecode, points[mask, :], mask, 'ground_surface')
        bld_z_valid = np.isfinite(bld_z)
        # Every point between 0 and max_obstacle_height above ground plane
        ahn_mask = ((bld_z[bld_z_valid] < points[mask_ids[bld_z_valid], 2]) &
                    (points[mask_ids[bld_z_valid], 2] <= bld_z[bld_z_valid] + max_obstacle_height))
        obstacle_mask[bld_z_valid] = obstacle_mask[bld_z_valid] & ahn_mask

    label_mask[mask_ids[obstacle_mask]] = True

    return label_mask

def create_mask(labels, exclude_labels):
    """Create mask based on `exclude_labels`."""
    mask = np.ones((len(labels),), dtype=bool)
    if len(exclude_labels) > 0:
        for exclude_label in exclude_labels:
            mask = mask & (labels != exclude_label)
    return mask