import json
import numpy as np
import sys, os
from kd_tree import kdTree
from probdist import probability_distribution

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
# Find min_X, max_X, min_Y, and max_Y given a Geo-json file or multiple files
def bounding_box_process(in_file_path):
    output_data = []
    bounding_box_set = []
    
    ext_output = os.path.splitext(in_file_path)[1]
    if ext_output is not '':
        # load the Geo-json file
        with open(in_file_path) as f:
            data = json.load(f)
        # find the minimum and maximum values of the 1st set of coordinates
        bounding_box = min_max_calculation(data['features'][0]['geometry']['type'], data['features'][0]['geometry']['coordinates'])
        output_data.append([data['features'][0]['geometry']['type'], data['features'][0]['geometry']['coordinates']])
        # process all geometries excluding the 1st one
        for index in range(len(data['features'])):
            # skip the 1st one
            if index == 0:
                continue
            # find a bounding box given a set of coordinates
            tmp_bounding_box= min_max_calculation(data['features'][index]['geometry']['type'],
                                                  data['features'][index]['geometry']['coordinates'])
            output_data.append([data['features'][index]['geometry']['type'], data['features'][index]['geometry']['coordinates']])

            # update the minimum and maximum values
            bounding_box[0] = update_function(bounding_box[0], tmp_bounding_box[0], 0)
            bounding_box[1] = update_function(bounding_box[1], tmp_bounding_box[1], 0)
            bounding_box[2] = update_function(bounding_box[2], tmp_bounding_box[2], 1)
            bounding_box[3] = update_function(bounding_box[3], tmp_bounding_box[3], 1)
        bounding_box_set.append(bounding_box)
    else:
        print('multiple files')
        # loop through all geojson files
        for f in os.listdir(in_file_path):
            # load the Geo-json file
            with open(os.path.join(in_file_path, f)) as f:
                data = json.load(f)
            # find the minimum and maximum values of the 1st set of coordinates
            bounding_box = min_max_calculation(data['features'][0]['geometry']['type'], data['features'][0]['geometry']['coordinates'])
            output_data.append([data['features'][0]['geometry']['type'], data['features'][0]['geometry']['coordinates']])
            # process all geometries excluding the 1st one
            for index in range(len(data['features'])):
                # skip the 1st one
                if index == 0:
                    continue
                # find a bounding box given a set of coordinates
                tmp_bounding_box= min_max_calculation(data['features'][index]['geometry']['type'],
                                                  data['features'][index]['geometry']['coordinates'])
                output_data.append([data['features'][index]['geometry']['type'], data['features'][index]['geometry']['coordinates']])

                # update the minimum and maximum values
                bounding_box[0] = update_function(bounding_box[0], tmp_bounding_box[0], 0)
                bounding_box[1] = update_function(bounding_box[1], tmp_bounding_box[1], 0)
                bounding_box[2] = update_function(bounding_box[2], tmp_bounding_box[2], 1)
                bounding_box[3] = update_function(bounding_box[3], tmp_bounding_box[3], 1)
            bounding_box_set.append(bounding_box)
    
    #return data, bounding_box
    return output_data, bounding_box_set
# =======================================
# Write out geojson files
def geojson_write(level_val, bounding_box_collec, hist, directory_path):
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
        geometry_dic['coordinates'] = bounding_box_collec[index]
        properties_dic['counts'] = hist[index]
        
        tmp_dic['type'] = 'Feature'
        tmp_dic['geometry'] = geometry_dic
        tmp_dic['properties'] = properties_dic
        feature_list.append(tmp_dic)
        del tmp_dic
        del geometry_dic
        del properties_dic
    json_dic['features'] = feature_list
    # save the dictionary structure as a Geojson file
    with open(os.path.join(directory_path, 'level-' + str(level_val) + '.geojson'), 'w') as f:
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
    #threshold_value = sys.argv[3]
    
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
    
    # loop through different levels
    path = 'distribution'
    geojson_path = 'geojson'
    
    if not os.path.exists(path):
        print('Create the distribution directory !!')
        os.makedirs(path)

    if not os.path.exists(geojson_path):
        print('Create the geojson directory !!')
        os.makedirs(geojson_path)

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
        distribution.distribution_computation(count, path)

        # write out a Geojson file
        geojson_write(count, bb_collec, hist, geojson_path)
        
if __name__ == "__main__":
    main()
    
