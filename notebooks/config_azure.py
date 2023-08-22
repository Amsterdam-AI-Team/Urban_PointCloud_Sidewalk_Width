# Input paths notebook 5
pc_data_folder = "/home/azureuser/cloudfiles/code/blobfuse/ovl/pointcloud/Unlabeled/Amsterdam/Cyclomedia_overview/"
out_folder = "/home/azureuser/cloudfiles/code/blobfuse/sidewalk/"
obstacle_file = f'{out_folder}sidewalks_with_obstacles_all.gpkg'  # sidewalks_with_obstacles.gpkg or sidewalks_with_obstacles_all.gpkg

# Intermediate output path (in case of errors, notebook 5)
tmp_file = f'{out_folder}sw_seg_tmp.pkl'

# Output path notebook 5 / input path notebook 6
segments_file = f'{out_folder}processed_data/output/sidewalk_segments.gpkg'  # sidewalk_segments_small.gpkg or sidewalk_segments.gpkg
segments_image = f'{out_folder}processed_data/output/images/sidewalk_segments_all.png' # sidewalk_segments.png or sidewalk_segments_all.png

# BGT path
bgt_road_file = f'{out_folder}processed_data/bgt/bgt_voetpad.gpkg'  # bgt_voetpad_small.gpkg or bgt_voetpad.gpkg

# Intermedia files notebook 6
bgt_cl_file = f'{out_folder}processed_data/output/bgt_cl.pkl'  # bgt_cl_east.pkl or bgt_cl.pkl
bgt_fw_file = f'{out_folder}processed_data/output/bgt_fw.pkl'  # bgt_fw_east.pkl or bgt_fw.pkl
final_df_file = f'{out_folder}processed_data/output/final_df_tmp_all.pkl' # final_df_tmp.pkl or final_df_tmp_all.pkl

# Final output paths
output_file = f'{out_folder}processed_data/output/final_output_segments.gpkg'  # final_output_segments_small.gpkg or final_output_segments.gpkg
output_image = f'{out_folder}processed_data/output/images/final_output_image.png'  # final_output_image_small.png or final_output_image.png
output_image_no = f'{out_folder}processed_data/output/images/final_output_image_no.png'  # final_output_image_no_small.png or final_output_image_no.png

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