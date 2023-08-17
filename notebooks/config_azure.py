# Input paths notebook 5
pc_data_folder = "/home/azureuser/cloudfiles/code/blobfuse/ovl/pointcloud/Unlabeled/Amsterdam/Cyclomedia_overview/"
out_folder = "/home/azureuser/cloudfiles/code/blobfuse/sidewalk/"
obstacle_file = f'{out_folder}sidewalks_with_obstacles_all.gpkg'  # sidewalks_with_obstacles.gpkg or sidewalks_with_obstacles_all.gpkg

# Intermediate output path (in case of errors, notebook 5)
tmp_file = f'{out_folder}sw_seg_tmp.pkl'

# Output path notebook 5 / input path notebook 6
segments_file = f'{out_folder}processed_data/output/sidewalk_segments.gpkg'  # sidewalk_segments_small.gpkg or sidewalk_segments.gpkg

# BGT path
bgt_road_file = f'{out_folder}processed_data/bgt/bgt_voetpad_small.gpkg'  # bgt_voetpad.gpkg

# Final output paths
output_file = f'{out_folder}processed_data/output/final_output_segments_all.gpkg'
output_image = f'{out_folder}processed_data/output/final_output_image_all.png'
output_image_no = f'{out_folder}processed_data/output/final_output_image_no_all.png'

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

# Boundary for filtering out (in meters)
min_path_width = 0.4 

# Boundaries between the final colors green/orange/red (in meters)
width_lower = 0.9  
width_upper = 1.8
width_top = 2.9 

# Maximum distance between intended start point and start node (in meters)
max_dist = 3 

# Maximum length of linestring (in meters), otherwise cut
max_ls_length = 10

# Minimum length for short-ends (in meters), otherwise removed (in full width calculation)
min_se_length_fw = 10

# Minimum interior size to remain in BGT data
min_interior_size = 10