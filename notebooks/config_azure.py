# Paths
pc_data_folder = "/home/azureuser/cloudfiles/code/blobfuse/ovl/pointcloud/Unlabeled/Amsterdam/Cyclomedia_overview/"
out_folder = "/home/azureuser/cloudfiles/code/blobfuse/sidewalk/"
obstacle_file = f'{out_folder}sidewalks_with_obstacles.gpkg'  # sidewalks_with_obstacles_all.gpkg
segments_file = f'{out_folder}sidewalk_segments.gpkg'

# Save intermediate output in case of errors
tmp_file = f'{out_folder}sw_seg_tmp.pkl'

# Set Coordinate Reference System
CRS = 'epsg:28992' 

# Whether to merge sidewalks before segmentation and width computation
merge_sidewalks = True

# Tolerance for centerline simplification
simplify_tolerance = 0.2

# Min area size of a sidewalk polygon in sqm for which width will be computed
min_area_size = 5

# Minimum length for short-ends (in meters), otherwise removed
min_se_length = 5

# Max segment length in meters
max_seg_length = 2 

# Resolution (in m) for min and avg width computation
width_resolution = 1

# Precision (in decimals) for min and avg width computation
width_precision = 1