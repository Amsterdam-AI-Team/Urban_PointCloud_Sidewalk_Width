import numpy as np
from shapely.geometry import Polygon
import ast
import logging
from scipy.spatial import ConvexHull
import matplotlib.pyplot as plt

import upcp.utils.csv_utils as csv_utils
from upcp.region_growing.label_connected_comp import LabelConnectedComp
from upcp.utils.math_utils import minimum_bounding_rectangle
from upcp.utils.las_utils import get_bbox_from_tile_code
from upcp.utils.clip_utils import poly_box_clip

logger = logging.getLogger(__name__)


class Accessibility:
    """
    Parameters
    ----------
    label : int
        Class label to use for this fuser.
    ahn_reader : AHNReader object
        Elevation data reader.
    bgt_file : str or Path or None (default: None)
        File containing data files needed for this fuser. Either a file or a
        folder should be provided, but not both.
    bgt_folder : str or Path or None (default: None)
        Folder containing data files needed for this fuser. Data files are
        assumed to be prefixed by "bgt_roads", unless otherwise specified.
        Either a file or a folder should be provided, but not both.
    file_prefix : str (default: 'bgt_roads')
        Prefix used to load the correct files; only used with bgt_folder.
    """

    def __init__(self, bgt_file=None, bgt_folder=None,
    			 file_prefix='bgt_roads', grid_size=0.05,
    			 min_component_size=5000, overlap_perc=20, params={}):
        self.grid_size = grid_size
        self.min_component_size = min_component_size
        self.overlap_perc = overlap_perc

    def _label_obstacles(self, points, point_components):
        """ TODO.  """

        obstacle_mask = np.zeros(len(points), dtype=bool)
        obstacle_count = 0

        cc_labels = np.unique(point_components)

        cc_labels = set(cc_labels).difference((-1,))

        listje = []
        for cc in cc_labels:
            # select points that belong to the cluster
            cc_mask = (point_components == cc)

            pointjes = np.array(points[cc_mask])[:, :2]
            mbrect, _, mbr_width, mbr_length, _ =\
                        minimum_bounding_rectangle(pointjes)
            poly = np.vstack((mbrect, mbrect[0]))

            hull_points = pointjes[ConvexHull(pointjes).vertices]
            obstacle = Polygon(hull_points)

            poly = Polygon(poly)

            listje.append([hull_points.tolist()])
            obstacle_mask = obstacle_mask | poly_box_clip(points, poly)
            obstacle_count += 1

        csv_headers = ['obstacle']
        bgt_obstacle_file = '../datasets/bgt/bgt_obstacle_demo.csv'

        # Write the csv
        csv_utils.write_csv(bgt_obstacle_file, listje, csv_headers)

        logger.debug(f'{obstacle_count} obstacles labelled.')
        return obstacle_mask

    def get_obstacle_polygons(self, points, mask, tilecode):
        """
        Returns the label mask for the given pointcloud.

        Parameters
        ----------
        points : array of shape (n_points, 3)
            The point cloud <x, y, z>.
        mask : array of shape (n_points,) with dtype=bool
            Pre-mask used to label only a subset of the points.
        tilecode : str
            The CycloMedia tile-code for the given pointcloud.

        Returns
        -------
        An array of shape (n_points,) with dtype=bool indicating which points
        should be labelled according to this fuser.
        """

        label_mask = np.zeros((len(points),), dtype=bool)

        if mask is None:
            mask = np.ones((len(points),), dtype=bool)
        mask_ids = np.where(mask)[0]

        obstacle_mask = np.zeros((len(mask_ids),), dtype=bool)

        label = 33 # TODO
        lcc = LabelConnectedComp(label, grid_size=self.grid_size,
                                 min_component_size=self.min_component_size)
        point_components = lcc.get_components(points[mask])

        # Label obstacle clusters
        obstacle_mask = self._label_obstacles(points[mask], point_components)
        label_mask[mask_ids[obstacle_mask]] = True

        return label_mask
