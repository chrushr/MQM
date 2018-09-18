import json
import numpy as np
import sys, os, csv
from kd_tree_v2 import kdTree
from probdist_v2 import probability_distribution
from area import area
import pandas as pd
import argparse
#from unbal_kd_tree import unBalKdTree

def update_function(old_value, new_value, flag):
    if flag == 0:
        if new_value < old_value:
            return new_value
        else:
            return old_value
    elif flag == 1:
        if new_value > old_value:
            return new_value
        else:
            return old_value
# =======================================
def dim_3_computation(in_matrix):
    out_min_X = np.min(np.array(in_matrix[0])[:, 0])
    out_max_X = np.max(np.array(in_matrix[0])[:, 0])
    out_min_Y = np.min(np.array(in_matrix[0])[:, 1])
    out_max_Y = np.max(np.array(in_matrix[0])[:, 1])
    
    for ind in range(len(in_matrix)):
        if ind == 0:
            continue
        # update the values
        out_min_X = update_function(out_min_X, np.min(np.array(in_matrix[ind])[:, 0]), 0)
        out_max_X = update_function(out_max_X, np.max(np.array(in_matrix[ind])[:, 0]), 1)
        out_min_Y = update_function(out_min_Y, np.min(np.array(in_matrix[ind])[:, 1]), 0)
        out_max_Y = update_function(out_max_Y, np.max(np.array(in_matrix[ind])[:, 1]), 1)

    return out_min_X, out_max_X, out_min_Y, out_max_Y
# =======================================
def min_max_calculation(geo_type, in_coordinates):
    # declare variables
    tmp_min_X = tmp_max_X = tmp_min_Y = tmp_max_Y = None
    # find the minimum and maximum value based on geometry types
    if geo_type == 'Point' or geo_type == 'LineString' or geo_type == 'MultiPoint':
        np_array = np.array(in_coordinates)
        dim_value = len(np_array.shape)
        if dim_value == 1:
            # find the minimum and maximum value directly
            tmp_min_X = tmp_max_X = np_array[0]
            tmp_min_Y = tmp_max_Y = np_array[1]
        elif dim_value == 2:
            # find the minimum and maximum values through comparing all elements in individual columns
            tmp_min_X = np.min(np_array[:, 0])
            tmp_max_X = np.max(np_array[:, 0])
            tmp_min_Y = np.min(np_array[:, 1])
            tmp_max_Y = np.max(np_array[:, 1])
    elif geo_type == 'Polygon' or geo_type == 'MultiLineString': # dimension = 3
        # example: [
       #            [[35, 10], [45, 45], [15, 40], [10, 20], [35, 10]],  ==> one polygon
       #            [[20, 30], [35, 35], [30, 20], [20, 30]]             ==> the other
       #           ]
       # find the minmum and maximum values
        tmp_min_X, tmp_max_X, tmp_min_Y, tmp_max_Y = dim_3_computation(in_coordinates)
    elif geo_type == 'MultiPolygon': # dimension = 4
        for inds in range(len(in_coordinates)):
            if inds == 0:
                tmp_min_X, tmp_max_X, tmp_min_Y, tmp_max_Y = dim_3_computation(in_coordinates[inds])
            else:
                min_x, max_x, min_y, max_y = dim_3_computation(in_coordinates[inds])
                # update the values
                tmp_min_X = update_function(tmp_min_X, min_x, 0)
                tmp_max_X = update_function(tmp_max_X, max_x, 1)
                tmp_min_Y = update_function(tmp_min_Y, min_y, 0)
                tmp_max_Y = update_function(tmp_max_Y, max_y, 1)
    
    return [tmp_min_X, tmp_min_Y, tmp_max_X, tmp_max_Y]
# =======================================
# unwrap complicated geometry types
def unwrap_func(geometries_list, ids_list, flag, file_name):
#    line_list = []
#    point_list = []

    # process the first "geometrycollection" feature,
    # extension calculation
    tmp_storage_list = []
    id_count_index = 0
    tmp = min_max_calculation(geometries_list[0]['type'], geometries_list[0]['coordinates'])
    # split mixed geometries to multiple individual geometries when the type is MultiPoint or MultiLineString
    if geometries_list[0]['type'] == 'MultiLineString' or geometries_list[0]['type'] == 'MultiPoint':
        type_name = ''
        if geometries_list[0]['type'] == 'MultiLineString':
            type_name = 'LineString'
        else:
            type_name = 'Point'
        for arry_ind in range(len(geometries_list[0]['coordinates'])):
            if len(ids_list[id_count_index + arry_ind]) != 0:
                tmp_storage_list.append([type_name, geometries_list[0]['coordinates'][arry_ind], flag, ids_list[id_count_index + arry_ind]['osmid'],
                                         ids_list[id_count_index + arry_ind]['ItemId'], file_name])
        id_count_index += len(geometries_list[0]['coordinates'])
    else:  # A point or a line
        if len(ids_list[id_count_index]) != 0:
            tmp_storage_list.append([geometries_list[0]['type'], geometries_list[0]['coordinates'], flag, ids_list[id_count_index]['osmid'],
                                     ids_list[id_count_index]['ItemId'], file_name])
        id_count_index += 1
    # iterates through the remaining "geometrycollection" features in "geometries"  it is also a list.
    for ind2 in range(len(geometries_list)):
        if ind2 == 0:
            continue
        else:
            # extension calculation
            tmp2 = min_max_calculation(geometries_list[ind2]['type'], geometries_list[ind2]['coordinates'])

            if geometries_list[ind2]['type'] == 'MultiLineString' or geometries_list[ind2]['type'] == 'MultiPoint':
                type_name = ''
                if geometries_list[ind2]['type'] == 'MultiLineString':
                    type_name = 'LineString'
                else:
                    type_name = 'Point'
                for arry_ind in range(len(geometries_list[ind2]['coordinates'])):
                    if len(ids_list[id_count_index + arry_ind]) != 0:
                        tmp_storage_list.append([type_name, geometries_list[ind2]['coordinates'][arry_ind], flag,
                                                 ids_list[id_count_index + arry_ind]['osmid'], ids_list[id_count_index + arry_ind]['ItemId'],
                                                 file_name])
                id_count_index += len(geometries_list[ind2]['coordinates'])
            else:  # A point or a line
                if len(ids_list[id_count_index]) != 0:
                    tmp_storage_list.append([geometries_list[ind2]['type'], geometries_list[ind2]['coordinates'], flag,
                                             ids_list[id_count_index]['osmid'], ids_list[id_count_index]['ItemId'], file_name])
                id_count_index += 1
            # update the bounding box
            tmp[0] = update_function(tmp[0], tmp2[0], 0)
            tmp[1] = update_function(tmp[1], tmp2[1], 0)
            tmp[2] = update_function(tmp[2], tmp2[2], 1)
            tmp[3] = update_function(tmp[3], tmp2[3], 1)
    # =================================================
    # record line indexes and indexes of non-empty dics
#    line_record_list = np.zeros(len(ids_list))
#    non_empty_dic = np.zeros(len(ids_list))
    #for record_ind in range(len(ids_list)):
#        if tmp_storage_list[record_ind][0] == 'LineString':
#            line_record_list[record_ind] = 1
#        if len(ids_list[record_ind]) != 0:
#            non_empty_dic[record_ind] = 1
    # find non-zero indexes from two arrays
#    nonzero_line = np.nonzero(line_record_list)[0]
#    nonzero_dic = np.nonzero(non_empty_dic)[0]
#    point_array =  np.where(line_record_list == 0)[0]
    # create the line list
#    for elem_ind in range(len(nonzero_line)):
#        line_list.append([tmp_storage_list[nonzero_line[elem_ind]][0], tmp_storage_list[nonzero_line[elem_ind]][1], flag, ids_list[nonzero_dic[elem_ind]]['osmid']])
    # create the point list
#    for elem_ind in range(len(point_array)):
#        point_list.append([tmp_storage_list[point_array[elem_ind]][0], tmp_storage_list[point_array[elem_ind]][1], flag, -1])

    return tmp, tmp_storage_list
# =======================================
# Find min_X, max_X, min_Y, and max_Y given a Geo-json file or multiple files
def bounding_box_process(in_folder_path):
    output_data = []
    bounding_box_set = []
    bounding_box = None
    name_num_list = []
    name_num_list.append(['Check_name', 'Counts'])
    start_point = 0
    end_point = 0
    roadFile = ''
    
    # loop through all geojson files
    for f in os.listdir(in_folder_path):
        #print('File Name:', os.path.join(in_folder_path, f))
        # ==========================================
        if os.path.isdir(os.path.join(in_folder_path, f)):
            for subdir, dirs, files in os.walk(os.path.join(in_folder_path, f)):
                for file in files:
                    filepath = subdir + os.sep + file

                    if filepath.endswith('.geojson'):
                        roadFile = filepath
        # ==========================================
        # load the Geo-json file and ignore other files
        if os.path.splitext(os.path.join(in_folder_path, f))[1] == '.geojson':
            #print('name:', os.path.splitext(f)[0])
            if len(os.path.splitext(f)[0].split('-')) == 3:
                name_num_list.append([os.path.splitext(f)[0].split('-')[0], int(os.path.splitext(f)[0].split('-')[2])])
            
            # open geojson files
            with open(os.path.join(in_folder_path, f), encoding='utf-8') as new_f:
                data = json.load(new_f)

            # randomly generate unique integers (flag ids)
            end_point = start_point + len(data['features'])
            int_array = np.arange(start_point, end_point)
            int_array = np.random.permutation(int_array)

            # find the minimum and maximum values of the 1st set of coordinates
            # determine whether or not the input type is geometrycollection. If so, invoke an unwrap function
            if data['features'][0]['geometry']['type'] == 'GeometryCollection':
                # iterates through all elements in "geometries" and find the bounding box
                if len(data['features'][0]['geometry']['geometries']) != 0:
                    bounding_box, geometry_collec = unwrap_func(data['features'][0]['geometry']['geometries'],
                                                                data['features'][0]['properties']['feature_properties'],
                                                                int_array[0], f)
                    # ==============================
                    #for element in geometry_collec:
                    #    output_data.append(element)
                    output_data = output_data + geometry_collec
                # ==============================
            else:
                # discard a feature without its feature property
                if len(data['features'][0]['properties']['feature_properties']) != 0:
                    bounding_box = min_max_calculation(data['features'][0]['geometry']['type'], data['features'][0]['geometry']['coordinates'])
                    output_data.append([data['features'][0]['geometry']['type'], data['features'][0]['geometry']['coordinates'],
                                        int_array[0], data['features'][0]['properties']['feature_properties'][0]['osmid'],
                                        data['features'][0]['properties']['feature_properties'][0]['ItemId'], f])

            # process all geometries excluding the 1st one
            for index in range(len(data['features'])):
                # skip the 1st one
                if index == 0:
                    continue
                # find a bounding box given a set of coordinates
                # determine whether or not the input type is geometrycollection. If so, invoke an unwrap function
                if data['features'][index]['geometry']['type'] == 'GeometryCollection':
                    if len(data['features'][index]['geometry']['geometries']) != 0:
                        # iterates through all elements in "geometries" and find the bounding box
                        tmp_bounding_box, tmp_geometry_collec = unwrap_func(data['features'][index]['geometry']['geometries'],
                                                                            data['features'][index]['properties']['feature_properties'],
                                                                            int_array[index], f)
                        # ==============================
                        #for element in tmp_geometry_collec:
                        #    output_data.append(element)
                        output_data = output_data + tmp_geometry_collec
                    # ==============================
                else:
                    # discard a feature without its feature property
                    if len(data['features'][index]['properties']['feature_properties']) != 0:
                        tmp_bounding_box= min_max_calculation(data['features'][index]['geometry']['type'],
                                                              data['features'][index]['geometry']['coordinates'])
                        output_data.append([data['features'][index]['geometry']['type'], data['features'][index]['geometry']['coordinates'],
                                            int_array[index], data['features'][index]['properties']['feature_properties'][0]['osmid'],
                                            data['features'][index]['properties']['feature_properties'][0]['ItemId'], f])
                # update the minimum and maximum values
                bounding_box[0] = update_function(bounding_box[0], tmp_bounding_box[0], 0)
                bounding_box[1] = update_function(bounding_box[1], tmp_bounding_box[1], 0)
                bounding_box[2] = update_function(bounding_box[2], tmp_bounding_box[2], 1)
                bounding_box[3] = update_function(bounding_box[3], tmp_bounding_box[3], 1)
            bounding_box_set.append(bounding_box)

            # update start point
            start_point = len(data['features'])
    
    return output_data, bounding_box_set, name_num_list, roadFile
# =======================================
# Write out geojson file
# Polygon Format:
# [ [
#      [-180.0, 79.1713346],
#      [-180.0, 85.0511288],
#      [-135.0, 85.0511288],
#      [-135.0, 79.1713346]
#   ]
# ]
def geojson_write(level_val, bounding_box_collec, hist, directory_path, cell_num, initial_area, in_grid_ids, kd_tree_mode, flag_val):
    # declare variables
    json_dic = {}
    feature_list = []
    json_dic['type'] = 'FeatureCollection'
    
    # add all cells and counts into the feature list
    for index in range(len(hist)):
        tmp_dic = {}
        geometry_dic = {}
        properties_dic = {}
        geometry_dic['type'] = 'Polygon'
        #geometry_dic['coordinates'] = bounding_box_collec[index]
        geometry_dic['coordinates'] = [[ [bounding_box_collec[index][0],bounding_box_collec[index][1]],
                                         [bounding_box_collec[index][0],bounding_box_collec[index][3]],
                                         [bounding_box_collec[index][2],bounding_box_collec[index][3]],
                                         [bounding_box_collec[index][2],bounding_box_collec[index][1]] ]]
        
        properties_dic['counts'] = hist[index]
        if flag_val:
            if in_grid_ids is None:
                properties_dic['gridId'] = index + 1
            else:
                properties_dic['gridId'] = in_grid_ids[index]
        
        tmp_dic['type'] = 'Feature'
        tmp_dic['geometry'] = geometry_dic
        tmp_dic['properties'] = properties_dic
        feature_list.append(tmp_dic)
        del tmp_dic
        del geometry_dic
        del properties_dic
    json_dic['features'] = feature_list
    
    # save the dictionary structure as a Geojson file
    if kd_tree_mode == 'tree_v1':
        #grid_area = initial_area / (2**(level_val + 1))
        grid_area = initial_area / (2**(level_val))
        grid_area = round(grid_area * 1e-6, 2)
    
        with open(os.path.join(directory_path, 'level-' + str(level_val) + '-' + str(cell_num) + '_area_' + str(grid_area) + '_sq_kms' + '.geojson'), 'w') as f:
            json.dump(json_dic, f)
    elif kd_tree_mode == 'tree_v2':
        with open(os.path.join(directory_path, 'max-depth-' + str(level_val) + '-' + 'cell_num' + str(cell_num) + '.geojson'), 'w') as f:
            json.dump(json_dic, f)
    elif kd_tree_mode == 'cascade-kdtree':
        with open(os.path.join(directory_path, 'first-depth-' + str(level_val) + '.geojson'), 'w') as f:
            json.dump(json_dic, f)
# =======================================
# Compute cell size
def cell_size_computation(depth_val, bounding_box_collec):
    print('Level ', depth_val)
    print('Grid size ( Width (X length) x Height (Y length) ): ', (bounding_box_collec[0][2] - bounding_box_collec[0][0]
          , bounding_box_collec[0][3] - bounding_box_collec[0][1]))
    print('========================')
# =======================================
# Create a table and save it as a csv file
def csv_file_write(in_data, in_grid_collec_list, in_path, area_list):
    out_list = []
    out_list.append(['grid_id', 'atlas_id', 'osm_id', 'flag_id', 'check_name', 'area_sqkm'])
    if len(in_grid_collec_list) == 1:
        for index in range(len(in_data)):
            if in_data[index][0] == 'Point' and in_data[index][4] + '-' + in_data[index][0] in in_grid_collec_list[0]:
                out_list.append([in_grid_collec_list[0][    in_data[index][4] + '-' + in_data[index][0] ], in_data[index][4],
                                  in_data[index][3], in_data[index][2], in_data[index][5], area_list[0]
                                  ])
            elif in_data[index][0] == 'LineString' and in_data[index][4] + '-' + in_data[index][0] in in_grid_collec_list[0]:
                for elem_id in in_grid_collec_list[0][in_data[index][4] + '-' + in_data[index][0] ]:
                    out_list.append([elem_id, in_data[index][4], in_data[index][3], in_data[index][2], in_data[index][5], area_list[0]])
    else:
        for index in range(len(in_data)):
            # iterate through all grid-id dictionaries
            for dic_index in range(len(in_grid_collec_list)):
                if in_data[index][0] == 'Point' and in_data[index][4] + '-' + in_data[index][0] in in_grid_collec_list[dic_index]:
                    out_list.append([in_grid_collec_list[dic_index][in_data[index][4] + '-' + in_data[index][0] ], in_data[index][4],
                                     in_data[index][3], in_data[index][2], in_data[index][5], area_list[dic_index]
                                     ])
                elif in_data[index][0] == 'LineString' and in_data[index][4] + '-' + in_data[index][0] in in_grid_collec_list[dic_index]:
                    for elem_id in in_grid_collec_list[dic_index][in_data[index][4] + '-' + in_data[index][0] ]:
                        out_list.append([elem_id, in_data[index][4], in_data[index][3], in_data[index][2], in_data[index][5], area_list[dic_index]])
    # save the 2d list as a file
    with open(in_path, "w") as out_f:
        writer = csv.writer(out_f)
        writer.writerows(out_list)
# =======================================
# Road counts
def road_count(in_road, in_grids, in_counts, out_folder, initial_bb):
    road_data = []
    road_counts_his = np.zeros(len(in_grids), dtype=int)
    # load the Geo-json file and ignore other files
    if os.path.splitext(in_road)[1] == '.geojson':
        # open geojson files
        with open(in_road, encoding='utf-8') as new_f:
            in_data = json.load(new_f)
        
        # process all geometries excluding the 1st one
        for index in range(len(in_data['features'])):
            # discard a feature without its feature property
            if len(in_data['features'][index]['properties']) != 0:
                road_data.append([in_data['features'][index]['geometry']['type'], in_data['features'][index]['geometry']['coordinates']])

        # calculate the number of counts within a grid giving the road data
        for index2 in range(len(road_data)):
            if road_data[index2][0] == 'LineString':
                np_array = np.array(road_data[index2][1])
                tmp_array = np.zeros(len(in_grids))

                # iterate through all grids
                for ind in range(len(in_grids)):
                    for coordinate_ind in range(np_array.shape[0]):
                        if in_grids[ind][3] == initial_bb[3] and in_grids[ind][2] == initial_bb[2]:
                            if (np_array[coordinate_ind, :][0] >= in_grids[ind][0] and np_array[coordinate_ind, :][0] <= in_grids[ind][2] and
                                np_array[coordinate_ind, :][1] >= in_grids[ind][1] and np_array[coordinate_ind, :][1] <= in_grids[ind][3]):
                                tmp_array[ind] += 1
                        elif in_grids[ind][3] == initial_bb[3] and in_grids[ind][2] != initial_bb[2]:
                            if (np_array[coordinate_ind, :][0] >= in_grids[ind][0] and np_array[coordinate_ind, :][0] < in_grids[ind][2] and
                                np_array[coordinate_ind, :][1] >= in_grids[ind][1] and np_array[coordinate_ind, :][1] <= in_grids[ind][3]):
                                tmp_array[ind] += 1
                        elif in_grids[ind][3] != initial_bb[3] and in_grids[ind][2] == initial_bb[2]:
                            if (np_array[coordinate_ind, :][0] >= in_grids[ind][0] and np_array[coordinate_ind, :][0] <= in_grids[ind][2] and
                                np_array[coordinate_ind, :][1] >= in_grids[ind][1] and np_array[coordinate_ind, :][1] < in_grids[ind][3]):
                                tmp_array[ind] += 1
                        elif in_grids[ind][3] != initial_bb[3] and in_grids[ind][2] != initial_bb[2]:
                            if (np_array[coordinate_ind, :][0] >= in_grids[ind][0] and np_array[coordinate_ind, :][0] < in_grids[ind][2] and
                                np_array[coordinate_ind, :][1] >= in_grids[ind][1] and np_array[coordinate_ind, :][1] < in_grids[ind][3]):
                                tmp_array[ind] += 1
                
                #print('temp :', tmp_array)
                for ind2 in range(len(in_grids)):
                    if tmp_array[ind2] > 0:
                        road_counts_his[ind2] += 1
        # ==========================================
        # write out a csv file
        csv_matrix = []
        csv_matrix.append(['grid_id', 'err_roads', 'road_counts'])
        for index in range(len(in_grids)):
            csv_matrix.append([index + 1, in_counts[index], road_counts_his[index]])
            
        with open(os.path.join(out_folder, 'road-' + os.path.basename(out_folder) + '.csv'), "w") as out_f:
            writer = csv.writer(out_f)
            writer.writerows(csv_matrix)
# =======================================
# The main function
def main():
    # declare variables
    # declare arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--kdTreeMode', type = str, default='', help='choose either single k-d tree or multiple k-d trees')
    parser.add_argument('--folderPath', type = str, default='', help='path to an input folder')
    parser.add_argument('--maxDepth', type = str, default='', help='max depth of a k-d tree')
    parser.add_argument('--outFolder', type = str, default='', help='path to an ouput folder')
    parser.add_argument('--countNum', type = str, default='', help='a count value')
    parser.add_argument('--gridPercent', type = str, default='', help='a grid percentage')
    parser.add_argument('--maxCount', type = str, default='', help='maximum count to the second k-d tree')
    
    args = parser.parse_args()
    kd_tree_mode = args.kdTreeMode
    file_path = args.folderPath
    maximum_level = args.maxDepth
    folder_path = args.outFolder
    count_num = int(args.countNum)
    grid_percent = float(args.gridPercent)
    
    max_count = 0
    flag_val = False
    
    # find an initial bounding box given all geometries
    final_BB = None
    entire_data, out_BB, out_name_num, road_file = bounding_box_process(file_path)
    
    # save the 2d list as a file
    with open(os.path.join(folder_path, os.path.basename(file_path) + '.csv' )  , "w") as out_f:
        writer = csv.writer(out_f)
        writer.writerows(out_name_num)
        
    if len(out_BB) == 1:
        final_BB = out_BB[0]
    else:
        final_BB = out_BB[0]
        for index in range(len(out_BB)):
            # skip the 1st one
            if index == 0:
                continue
            final_BB[0] = update_function(final_BB[0], out_BB[index][0], 0)
            final_BB[1] = update_function(final_BB[1], out_BB[index][1], 0)
            final_BB[2] = update_function(final_BB[2], out_BB[index][2], 1)
            final_BB[3] = update_function(final_BB[3], out_BB[index][3], 1)

    # calculate the initial extension area
    obj = {}
    obj['type'] = 'Polygon'
    obj['coordinates'] = [[ [final_BB[0],final_BB[1]],
                            [final_BB[0],final_BB[3]],
                            [final_BB[2],final_BB[3]],
                            [final_BB[2],final_BB[1]] ]]
    initial_area = area(obj)
    
    # loop through different levels
    path = 'histogram'
    geojson_path = 'geojson'
    
    if not os.path.exists(os.path.join(folder_path, path)):
        print('Create the histogram directory !!')
        os.makedirs(os.path.join(folder_path, path))

    if not os.path.exists(os.path.join(folder_path, geojson_path)):
        print('Create the geojson directory !!')
        os.makedirs(os.path.join(folder_path, geojson_path))

    # choose the k-d tree model
    if kd_tree_mode == 'tree_v1':
        for depth_count in range(1, int(maximum_level) + 1):
            # build k-d tree
            tree_cons = kdTree(depth_count, final_BB, entire_data, 1)
            out_tree = tree_cons.tree_building()
            #print('tree', out_tree)
            
            # get leaves given a K-D tree
            bb_collec = tree_cons.get_leaves(out_tree)
            #print('bounding boxes', bb_collec)

            # get counts
            hist, gridid_collec= tree_cons.counts_calculation()
            #print('histogram:', hist)
            
            # Cell size computation
            cell_size_computation(depth_count, bb_collec)
            del tree_cons

            # probability distribution
            distribution = probability_distribution(hist)
            filename = os.path.join(os.path.join(folder_path, path), 'level-' + str(depth_count) + '.png')
            out_distribution, count_list, count_zero_list, cell_num = distribution.distribution_computation(filename)
            
            # write out a Geojson file
            geojson_write(depth_count, bb_collec, hist, os.path.join(folder_path, geojson_path), cell_num, initial_area, None, kd_tree_mode, flag_val)

            # stop condition (the over 90% (parameter) of cells is less than 10 (parameter) (the count value))
            if len(count_zero_list) != 0:
                count_list.insert(0, count_zero_list[0])
            smallest_max_count = 0
            smallest_max_count_ind = -1
            for ind, ele in enumerate(count_list):
                if ele > count_num:
                    break
                else:
                    smallest_max_count = ele
                    smallest_max_count_ind = ind

            if smallest_max_count_ind != -1:
                total_count_within_count_num = 0
                total_grids = 0
                list_length = 0
                if not count_zero_list:  # the list is empty
                    list_length = smallest_max_count_ind + 1
                    total_grids = cell_num
                else:
                    list_length = smallest_max_count_ind + 2
                    total_grids = cell_num + count_zero_list[1]

                for i in range(list_length):
                    if count_list[i] == 0:
                        total_count_within_count_num += count_zero_list[1]
                    else:
                        total_count_within_count_num += out_distribution[count_list[i]]

                if (float(total_count_within_count_num) / float(total_grids)) > grid_percent:
                    # calculate areas
                    grid_area = initial_area / (2**(depth_count))
                    grid_area = round(grid_area * 1e-6, 2)
                    # write out a csv file
                    file_path = os.path.join(folder_path, 'tree_1-log.csv')
                    csv_file_write(entire_data, [gridid_collec], file_path, [grid_area])

                    # SQL-like Query
                    sotm = pd.read_csv(file_path)
                    final_df = sotm.groupby('grid_id').agg({'atlas_id':'nunique', 'osm_id':'nunique', 'flag_id':'nunique', 'check_name':'nunique'})
                    final_df.to_csv(os.path.join(folder_path, 'tree_1-log_join_results.csv'), sep = ',', index ='grid_id')
                    
                    # write out a Geojson file
                    geojson_write(depth_count, bb_collec, hist, os.path.join(folder_path, geojson_path), cell_num, initial_area,
                                  None, kd_tree_mode, flag_val = True)
                    # road counts
                    if road_file:
                        road_count(road_file, bb_collec, hist, folder_path, final_BB)
                    break
    # ===============================
    elif kd_tree_mode == 'tree_v2':
        tree_cons = unBalKdTree(int(count_num), int(maximum_level), final_BB, entire_data)
        out_tree = tree_cons.tree_building()
        #print(out_tree)

        # get leaves given a K-D tree
        bb_collec = tree_cons.get_leaves(out_tree)

        # calculate counts
        hist = tree_cons.get_counts(bb_collec)
        #print('hist', hist)

        # probability distribution
        distribution = probability_distribution(hist)
        filename = os.path.join(os.path.join(folder_path, path), 'max-depth-' + str(maximum_level) + '.png')
        out_distribution, count_list, count_zero_list, cell_num = distribution.distribution_computation(filename)
        
        # write out a Geojson file
        geojson_write(maximum_level, bb_collec, hist, os.path.join(folder_path, geojson_path), cell_num, initial_area, kd_tree_mode, flag_val)
    # ===============================
    elif kd_tree_mode == 'cascade-kdtree':
        max_count = int(args.maxCount)
        
        optimal_count_list = None
        optimal_grid_size_list = None
        first_depth = 0
        big_initial_area = 0.0

        # determine the best depth using the K-D tree algorithm
        for depth_count in range(1, int(maximum_level) + 1):
            # build k-d tree
            tree_cons = kdTree(depth_count, final_BB, entire_data, 1)
            out_tree = tree_cons.tree_building()
            
            # get leaves and counts for given a K-D tree
            bb_collec = tree_cons.get_leaves(out_tree)
            counts_collec, gridid_collec = tree_cons.counts_calculation()
            
            # probability distribution
            distribution = probability_distribution(counts_collec)
            filename = os.path.join(os.path.join(folder_path, path), 'level-' + str(depth_count) + '.png')
            out_distribution, count_list, count_zero_list, cell_num = distribution.distribution_computation(filename)
            
            # write out a Geojson file
            geojson_write(depth_count, bb_collec, counts_collec, os.path.join(folder_path, geojson_path),
                          cell_num, initial_area, None, kd_tree_mode = 'tree_v1', flag_val = False)

            # stop condition (the over 90% (parameter) of cells is less than 10 (parameter) (the count value))
            if len(count_zero_list) != 0:
                count_list.insert(0, count_zero_list[0])
            smallest_max_count = 0
            smallest_max_count_ind = -1
            for ind, ele in enumerate(count_list):
                if ele > count_num:
                    break
                else:
                    smallest_max_count = ele
                    smallest_max_count_ind = ind

            if smallest_max_count_ind != -1:
                total_count_within_count_num = 0
                total_grids = 0
                list_length = 0
                if not count_zero_list:  # the list is empty
                    list_length = smallest_max_count_ind + 1
                    total_grids = cell_num
                else:
                    list_length = smallest_max_count_ind + 2
                    total_grids = cell_num + count_zero_list[1]

                for i in range(list_length):
                    if count_list[i] == 0:
                        total_count_within_count_num += count_zero_list[1]
                    else:
                        total_count_within_count_num += out_distribution[count_list[i]]

                if (float(total_count_within_count_num) / float(total_grids)) > grid_percent:
                    # calculate areas
                    grid_area = initial_area / (2**(depth_count))
                    grid_area = round(grid_area * 1e-6, 2)
                    big_initial_area = grid_area
                    # write out a csv file
                    file_path = os.path.join(folder_path, 'tree_1-log.csv' )
                    csv_file_write(entire_data, [gridid_collec], file_path, [grid_area])

                    # SQL-like Query
                    sotm = pd.read_csv(file_path)
                    final_df = sotm.groupby('grid_id').agg({'atlas_id':'nunique', 'osm_id':'nunique', 'flag_id':'nunique', 'check_name':'nunique'})
                    final_df.to_csv(os.path.join(folder_path, 'tree_1-log_join_results.csv'), sep = ',', index ='grid_id')
                    
                    # write out a Geojson file
                    geojson_write(depth_count, bb_collec, counts_collec, os.path.join(folder_path, geojson_path), cell_num, initial_area,
                                  None, kd_tree_mode = 'tree_v1', flag_val = True)
                    optimal_grid_size_list = bb_collec

                    optimal_count_list = counts_collec
                    first_depth = depth_count

                    # road counts
                    if road_file:
                        road_count(road_file, bb_collec, counts_collec, folder_path, final_BB)
                    break
        # ======================================
        
        big_grid_list = []
        new_grids_list = []
        new_counts_list = []
        new_area_list = []
        new_grid_id_list = []
        grid_ids = []
        gridid_start = 1
        # find all grids in which the count is greater the max count
        for index in range(len(optimal_grid_size_list)):
            if optimal_count_list[index] > max_count:
                big_grid_list.append(optimal_grid_size_list[index])
                #big_grid_ind_list.append(index)
        if len(big_grid_list) != 0:
            # refine big grids through applying the 2nd K-D tree
            for extension_ind in range(len(big_grid_list)):
                for depth_num in range(1, int(maximum_level) + 1):
                    # build k-d tree
                    new_tree_cons = kdTree(depth_num, big_grid_list[extension_ind], entire_data, gridid_start)
                    new_kd_tree = new_tree_cons.tree_building()
                    new_bb_collec = new_tree_cons.get_leaves(new_kd_tree)
                    # get counts
                    new_counts_collec, new_grid_id_collec = new_tree_cons.counts_calculation()
                    new_grid_id_list.append(new_grid_id_collec)
                    # calculate areas
                    new_area = big_initial_area / (2** depth_num)
                    new_area_list.append(new_area)

                    # update the start point of the grid id
                    gridid_start += len(new_bb_collec)

                    # stop condition
                    if len([x for x in new_counts_collec if x < max_count]) == len(new_counts_collec):
                        for small_ind in range(len(new_bb_collec)):
                            grid_ids.append(gridid_start + small_ind - len(new_bb_collec))
                            new_grids_list.append(new_bb_collec[small_ind])
                            new_counts_list.append(new_counts_collec[small_ind])
                        break
            # ======================================
            # write out a csv file
            file_path_tree_2 = os.path.join(folder_path, 'tree_2-log.csv' )
            csv_file_write(entire_data, new_grid_id_list, file_path_tree_2, new_area_list)

            # SQL-like Query
            sotm = pd.read_csv(file_path_tree_2)
            final_df = sotm.groupby('grid_id').agg({'atlas_id':'nunique', 'osm_id':'nunique', 'flag_id':'nunique', 'check_name':'nunique'})
            final_df.to_csv(os.path.join(folder_path, 'tree_2-log_join_results.csv'), sep = ',', index ='grid_id')
            
            # write out a Geojson file
            geojson_write(first_depth, new_grids_list, new_counts_list,
                          os.path.join(folder_path, geojson_path), None, None, grid_ids, kd_tree_mode, flag_val = True)
            print('Grid number after the 2nd k-d tree:', len(new_grids_list))
            print('Count number after the 2nd k-d tree:', len(new_counts_list))
if __name__ == "__main__":
    main()
