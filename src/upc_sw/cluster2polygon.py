import numpy as np
from scipy.spatial import ConvexHull

from upcp.region_growing.label_connected_comp import LabelConnectedComp

import logging
logger = logging.getLogger(__name__)


class Cluster2Polygon:
    """
    TODO
    """

    def __init__(self, grid_size=0.05, min_component_size=100):
        self.grid_size = grid_size
        self.min_component_size = min_component_size
        self.lcc = LabelConnectedComp(
                                grid_size=self.grid_size,
                                min_component_size=self.min_component_size)

    def get_obstacle_polygons(self, points):
        """
        Returns 2D polygons for each cluster in the given set of points.

        Parameters
        ----------
        points : array of shape (n_points, 3)
            The point cloud <x, y, z>.

        Returns
        -------
        A list of Shapely Polygons.
        """
        point_components = self.lcc.get_components(points[:, :2])
        cc_labels = np.unique(point_components)
        cc_labels = set(cc_labels).difference((-1,))

        # Convert clusters to polygons.
        obstacle_polygons = []
        obstacle_types = []
        for cc in cc_labels:
            # select points that belong to the cluster
            cc_mask = (point_components == cc)
            cc_points = points[cc_mask, :2]
            hull_points = cc_points[ConvexHull(cc_points).vertices]
            obstacle_polygons.append(hull_points.tolist())
            # TODO: use labels to determine obstacle type.
            obstacle_types.append('obstacle')

        logger.debug(f'{len(obstacle_polygons)} obstacles polygons extracted.')

        return obstacle_polygons, obstacle_types
