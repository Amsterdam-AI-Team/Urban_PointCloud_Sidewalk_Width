# Input paths notebook 5
pc_data_folder = '../datasets/pointclouds/'
out_folder = '../datasets/output/'
obstacle_file = f'{out_folder}sidewalks_with_obstacles.gpkg'

# Intermediate output path (in case of errors, notebook 5)
tmp_file = f'{out_folder}sw_seg_tmp.pkl'

# Output path notebook 5 / input path notebook 6
segments_file = f'{out_folder}sidewalk_segments.gpkg'
segments_image = f'{out_folder}sidewalk_segments_all.png'

# BGT path
bgt_road_file = '../datasets/bgt/bgt_voetpad.gpkg' 

# Intermedia files notebook 6
bgt_cl_file = f'{out_folder}bgt_cl.pkl'
bgt_fw_file = f'{out_folder}bgt_fw.pkl'
final_df_file = f'{out_folder}final_df_tmp_all.pkl'

# Final output paths 
output_file = f'{out_folder}final_output_segments_all.gpkg'
output_image = f'{out_folder}final_output_image_all.png'
output_image_no = f'{out_folder}final_output_image_no_all.png'

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

# Boundaries between the final colors (in meters)
width_1 = 0.9 
width_2 = 1.5
width_3 = 2.0
width_4 = 2.2
width_5 = 2.9
width_6 = 3.6

# Maximum distance between intended start point and start node (in meters)
max_dist = 3 

# Maximum length of linestring (in meters), otherwise cut
max_ls_length = 10

# Minimum length for short-ends (in meters), otherwise removed (in full width calculation)
min_se_length_fw = 10

# Minimum interior size to remain in BGT data
min_interior_size = 10