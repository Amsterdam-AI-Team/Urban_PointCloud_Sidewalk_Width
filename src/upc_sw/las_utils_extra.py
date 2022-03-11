import laspy
import numpy as np


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
