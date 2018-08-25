import json
import numpy as np
import sys, os
from kd_tree_v2 import kdTree
from probdist_v2 import probability_distribution
from area import area

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
def unwrap_func(geometries_list, ids_list, flag):
    line_list = []
    point_list = []
    
    # process the first "geometrycollection" feature,
    # extension calculation
    tmp_storage_list = []
    tmp = min_max_calculation(geometries_list[0]['type'], geometries_list[0]['coordinates'])
    # split mixed geometries to multiple individual geometries when the type is MultiPoint or MultiLineString
    if geometries_list[0]['type'] == 'MultiLineString' or geometries_list[0]['type'] == 'MultiPoint':
        type_name = ''
        if geometries_list[0]['type'] == 'MultiLineString':
            type_name = 'LineString'
        else:
            type_name = 'Point'
        for arry_ind in range(len(geometries_list[0]['coordinates'])):
            tmp_storage_list.append([type_name, geometries_list[0]['coordinates'][arry_ind]])
    else:  # A point or a line
        tmp_storage_list.append([geometries_list[0]['type'], geometries_list[0]['coordinates']])
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
                    tmp_storage_list.append([type_name, geometries_list[ind2]['coordinates'][arry_ind]])
            else:  # A point or a line
                tmp_storage_list.append([geometries_list[ind2]['type'], geometries_list[ind2]['coordinates']])
            # update the bounding box
            tmp[0] = update_function(tmp[0], tmp2[0], 0)
            tmp[1] = update_function(tmp[1], tmp2[1], 0)
            tmp[2] = update_function(tmp[2], tmp2[2], 1)
            tmp[3] = update_function(tmp[3], tmp2[3], 1)
    # record line indexes and indexes of non-empty dics
    line_record_list = np.zeros(len(ids_list))
    non_empty_dic = np.zeros(len(ids_list))
    for record_ind in range(len(ids_list)):
        if tmp_storage_list[record_ind][0] == 'LineString':
            line_record_list[record_ind] = 1
        if len(ids_list[record_ind]) != 0:
            non_empty_dic[record_ind] = 1
    # find non-zero indexes from two arrays
    nonzero_line = np.nonzero(line_record_list)[0]
    nonzero_dic = np.nonzero(non_empty_dic)[0]
    point_array =  np.where(line_record_list == 0)[0]
    # create the line list
    for elem_ind in range(len(nonzero_line)):
        line_list.append([tmp_storage_list[nonzero_line[elem_ind]][0], tmp_storage_list[nonzero_line[elem_ind]][1], flag, ids_list[nonzero_dic[elem_ind]]['osmid']])
    # create the point list
    for elem_ind in range(len(point_array)):
        point_list.append([tmp_storage_list[point_array[elem_ind]][0], tmp_storage_list[point_array[elem_ind]][1], flag, -1])
    
    #print(ids_list)
    #print(ids_list[0]['osmid'])
    #print(ids_list[1]['osmid'])
    #print(len(ids_list))
    #print(len(geometries_list[0]['coordinates']))
    #print(geometries_list[0]['type'])
    #print(len(geometries_list[0]['coordinates']))
    #print(properties_list)
    #out_list.append([geometries_list[0]['type'], geometries_list[0]['coordinates']])
    #for line_ind in range(len(geometries_list[0]['coordinates'])):
    #out_list.append(['LineString', geometries_list[0]['coordinates'][line_ind], flag, ids_list[line_ind]['osmid']])
    
    return tmp, line_list + point_list
# =======================================
# Find min_X, max_X, min_Y, and max_Y given a Geo-json file or multiple files
def bounding_box_process(in_folder_path):
    output_data = []
    bounding_box_set = []
    bounding_box = None

    start_point = 0
    end_point = 0
    
    # loop through all geojson files
    for f in os.listdir(in_folder_path):
        #print('File Name:', os.path.join(in_folder_path, f))
        
        # load the Geo-json file and ignore other files
        if os.path.splitext(os.path.join(in_folder_path, f))[1] == '.geojson':
            # open geojson files
            with open(os.path.join(in_folder_path, f), encoding='utf-8') as new_f:
                data = json.load(new_f)

            # randomly generate unique integers
            end_point = start_point + len(data['features'])
            int_array = np.arange(start_point, end_point)
            int_array = np.random.permutation(int_array)

            # find the minimum and maximum values of the 1st set of coordinates
            # determine whether or not the input type is geometrycollection. If so, invoke an unwrap function
            if data['features'][0]['geometry']['type'] == 'GeometryCollection':
                # iterates through all elements in "geometries" and find the bounding box
                bounding_box, geometry_collec = unwrap_func(data['features'][0]['geometry']['geometries'],
                                                            data['features'][0]['properties']['feature_properties'],
                                                            int_array[0])
                # ==============================
                for element in geometry_collec:
                    output_data.append(element)
                # ==============================
            else:
                bounding_box = min_max_calculation(data['features'][0]['geometry']['type'], data['features'][0]['geometry']['coordinates'])
                output_data.append([data['features'][0]['geometry']['type'], data['features'][0]['geometry']['coordinates'],
                                    int_array[0], -1])

            # process all geometries excluding the 1st one
            for index in range(len(data['features'])):
                # skip the 1st one
                if index == 0:
                    continue
                # find a bounding box given a set of coordinates
                # determine whether or not the input type is geometrycollection. If so, invoke an unwrap function
                if data['features'][index]['geometry']['type'] == 'GeometryCollection':

                    # iterates through all elements in "geometries" and find the bounding box
                    tmp_bounding_box, tmp_geometry_collec = unwrap_func(data['features'][index]['geometry']['geometries'],
                                                                        data['features'][index]['properties']['feature_properties'],
                                                                        int_array[index])
                    # ==============================
                    for element in tmp_geometry_collec:
                        output_data.append(element)
                    # ==============================
                else:
                    tmp_bounding_box= min_max_calculation(data['features'][index]['geometry']['type'],
                                                          data['features'][index]['geometry']['coordinates'])
                    output_data.append([data['features'][index]['geometry']['type'], data['features'][index]['geometry']['coordinates'],
                                        int_array[index], -1])

                # update the minimum and maximum values
                bounding_box[0] = update_function(bounding_box[0], tmp_bounding_box[0], 0)
                bounding_box[1] = update_function(bounding_box[1], tmp_bounding_box[1], 0)
                bounding_box[2] = update_function(bounding_box[2], tmp_bounding_box[2], 1)
                bounding_box[3] = update_function(bounding_box[3], tmp_bounding_box[3], 1)
            bounding_box_set.append(bounding_box)

            # update start point
            start_point = len(data['features'])
    
    return output_data, bounding_box_set
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
def geojson_write(level_val, bounding_box_collec, hist, directory_path, cell_num, initial_area):
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
        geometry_dic['coordinates'] = [[ [bounding_box_collec[index][0],bounding_box_collec[index][1]],
                                         [bounding_box_collec[index][0],bounding_box_collec[index][3]],
                                         [bounding_box_collec[index][2],bounding_box_collec[index][3]],
                                         [bounding_box_collec[index][2],bounding_box_collec[index][1]] ]]
        #geometry_dic['coordinates'] = bounding_box_collec[index]
        properties_dic['counts'] = hist[index]
        
        tmp_dic['type'] = 'Feature'
        tmp_dic['geometry'] = geometry_dic
        tmp_dic['properties'] = properties_dic
        feature_list.append(tmp_dic)
        del tmp_dic
        del geometry_dic
        del properties_dic
    json_dic['features'] = feature_list

    grid_area = initial_area / (2**(level_val + 1))
    grid_area = round(grid_area * 1e-6, 2)
    # save the dictionary structure as a Geojson file
    with open(os.path.join(directory_path, 'level-' + str(level_val) + '-' + str(cell_num) + '_area_' + str(grid_area) + '_sq_kms' + '.geojson'), 'w') as f:
        json.dump(json_dic, f)
# =======================================
# Compute cell size
def cell_size_computation(level_val, bounding_box_collec):
    print('Level ', level_val)
    print('Cell Width (X length):', bounding_box_collec[0][2] - bounding_box_collec[0][0])
    print('Cell Height (Y length):', bounding_box_collec[0][3] - bounding_box_collec[0][1])
    print('========================')
# =======================================
# The main function
def main():
    file_path = sys.argv[1]
    maximum_level = sys.argv[2]
    folder_path = sys.argv[3]
    count_num = int(sys.argv[4])
    grid_percent = float(sys.argv[5])
    
    # find an initial bounding box given all geometries
    final_BB = None
    entire_data, out_BB = bounding_box_process(file_path)
    
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

    for count in range(int(maximum_level) + 1):
        
        # build k-d tree
        tree_cons = kdTree(count, final_BB, entire_data)
        
        #out_tree, hist, bb_collec = tree_cons.tree_building()
        out_tree = tree_cons.tree_building()
        #print('tree', out_tree)
        
        # get leaves given a K-D tree
        bb_collec = tree_cons.get_leaves(out_tree)
        #print('bounding boxes', bb_collec)

        # get counts
        hist = tree_cons.counts_calculation()
        #print('histogram:', hist)
        
        # Cell size computation
        cell_size_computation(count, bb_collec)
        del tree_cons

        # probability distribution
        distribution = probability_distribution(hist)
        out_distribution, count_list, count_zero_list, cell_num = distribution.distribution_computation(count, os.path.join(folder_path, path))
        
        # write out a Geojson file
        geojson_write(count, bb_collec, hist, os.path.join(folder_path, geojson_path), cell_num, initial_area)

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
                break
        
if __name__ == "__main__":
    main()



    #ext_output = os.path.splitext(in_file_path)[1]
    #if ext_output is not '':
#        # load the Geo-json file
#        with open(in_file_path) as f:
#            data = json.load(f)
#        # find the minimum and maximum values of the 1st set of coordinates
#        bounding_box = min_max_calculation(data['features'][0]['geometry']['type'], data['features'][0]['geometry']['coordinates'])
#        output_data.append([data['features'][0]['geometry']['type'], data['features'][0]['geometry']['coordinates']])
#        # process all geometries excluding the 1st one
#        for index in range(len(data['features'])):
#            # skip the 1st one
#            if index == 0:
#                continue
#            # find a bounding box given a set of coordinates
#            tmp_bounding_box= min_max_calculation(data['features'][index]['geometry']['type'],
#                                                  data['features'][index]['geometry']['coordinates'])
#            output_data.append([data['features'][index]['geometry']['type'], data['features'][index]['geometry']['coordinates']])
#
#            # update the minimum and maximum values
#            bounding_box[0] = update_function(bounding_box[0], tmp_bounding_box[0], 0)
#            bounding_box[1] = update_function(bounding_box[1], tmp_bounding_box[1], 0)
#            bounding_box[2] = update_function(bounding_box[2], tmp_bounding_box[2], 1)
#            bounding_box[3] = update_function(bounding_box[3], tmp_bounding_box[3], 1)
#        bounding_box_set.append(bounding_box)
#    else:

