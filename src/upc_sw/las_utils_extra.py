import laspy
import numpy as np

def read_las(las_path):
    pointcloud = laspy.read(las_path)

    if 'label' not in pointcloud.point_format.extra_dimension_names:
        labels = np.zeros((len(pointcloud.x),), dtype='uint16')
    else:
        labels = pointcloud.label

    points = np.vstack((pointcloud.x, pointcloud.y, pointcloud.z)).T

    return points, labels

def read_las_m3c2(las_path):
    pointcloud = laspy.read(las_path)

    m3c2 = pointcloud.m3c2

    points = np.vstack((pointcloud.x, pointcloud.y, pointcloud.z)).T

    return points, m3c2
    
def write_las(points, las_path, labels=None):
    """
    Saving the ndarray points data into a .las file.
    :param content: ndarray
    :param las_path: string, path to save the las file
    """
    print('Saving LAS lidar data')
    
    outfile = laspy.create(file_version="1.2", point_format=3)
    outfile.x = points[:, 0]
    outfile.y = points[:, 1]
    outfile.z = points[:, 2]
    if labels is not None:
        outfile.add_extra_dim(laspy.ExtraBytesParams(name="label", type="uint16",
                              description="Labels"))
        outfile.label = labels
    outfile.write(las_path)

def write_las_m3c2(points, las_path, distances):
    """
    Saving the ndarray points data into a .las file.
    :param content: ndarray
    :param las_path: string, path to save the las file
    """
    print('Saving LAS lidar data')
    
    outfile = laspy.create(file_version="1.2", point_format=3)
    outfile.x = points[:, 0]
    outfile.y = points[:, 1]
    outfile.z = points[:, 2]
    if distances is not None:
        outfile.add_extra_dim(laspy.ExtraBytesParams(name="m3c2", type="float",
                              description="M3C2 distance"))
        outfile.m3c2 = distances
    outfile.write(las_path)

# TODO remove this function?
def merge_las(arr1, arr2):
    # Concatenating operation
    # axis = 1 implies that it is being done column-wise
    merged = np.concatenate((arr1, arr2), axis=0)
    return merged[:, [0,1,2]], merged[:, 3]
