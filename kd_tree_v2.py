import numpy as np

class kdTree:
    def __init__(self, tree_depth, bounding_box, data):
        self.root = None
        self.max_depth = tree_depth
        self.initial_bb = bounding_box
        self.data = data
        #self.ratio_threshold = threshold_value
        self.histogram = None
        self.bb_collection= []
    # =====================================
    # get a split rule
    def Get_split(self, level_count, in_bb):
        # if the counter is 0 or even numbers, we would like to partition a 2-D region along X-axis
        if level_count == 0 or (level_count & 1) == 0:
            # get a middle value given min_X and max_X
            return {'X_Middle_Value' : in_bb[0] + (in_bb[2] - in_bb[0]) / 2 }
        elif (level_count & 1) == 1:
            # get a middle value given min_Y and max_Y
            return { 'Y_Middle_Value' : in_bb[1] + (in_bb[3] - in_bb[1]) / 2 }
    # =====================================
    # split the bounding box into two boxes
    def BB_split(self, in_node, input_BB, level_value):
        left_up_BB = []
        right_down_BB = []
        if (level_value & 1) == 0 or level_value == 0:
            left_up_BB = [input_BB[0], input_BB[1], input_BB[0] + (input_BB[2] - input_BB[0]) / 2, input_BB[3]]
            right_down_BB = [input_BB[0] + (input_BB[2] - input_BB[0]) / 2, input_BB[1], input_BB[2], input_BB[3]] 
        elif (level_value & 1) == 1:
            left_up_BB = [input_BB[0], input_BB[1] + (input_BB[3] - input_BB[1]) / 2, input_BB[2], input_BB[3]]
            right_down_BB = [input_BB[0], input_BB[1], input_BB[2], input_BB[1] + (input_BB[3] - input_BB[1]) / 2] 
        return left_up_BB, right_down_BB
    # =====================================
    # build subtrees
    def build_subtree(self, node, depth_value, input_bb):
        # split the initial bounding box into two bounding boxes
        left_up_bb, right_down_bb = self.BB_split(node, input_bb, depth_value)
        
        # stop conditions
        if depth_value >= self.max_depth:
            node['left'] = left_up_bb #self.create_terminal_node(left_up_bb)
            # ==========================================================
            node['right'] = right_down_bb #self.create_terminal_node(right_down_bb)
            return
        
        # process left subtrees
        node['left'] = self.Get_split(depth_value, left_up_bb)   #(self.RSS_Calculation(left_data))
        self.build_subtree(node['left'], depth_value + 1, left_up_bb)
        
        # process right subtrees
        node['right'] = self.Get_split(depth_value, right_down_bb)  #(self.RSS_Calculation(right_data))
        self.build_subtree(node['right'], depth_value + 1, right_down_bb)
        
    # =====================================
    # help function
    def help_fun(self, input_tree, level_val):
        if isinstance(input_tree, dict):
            self.help_fun(input_tree['left'], level_val + 1)
            self.help_fun(input_tree['right'], level_val + 1)
        else:
            self.bb_collection.append(input_tree)
    # =====================================
    # get all leaves
    def get_leaves(self, input_tree):
        # get all leaves
        self.help_fun(input_tree, 0)
        return self.bb_collection
    # =====================================
    def point_within_grid(self, ind, geo_coordinate, bb_coordinate, in_tmp_array):
        if self.bb_collection[ind][3] == self.initial_bb[3] and self.bb_collection[ind][2] == self.initial_bb[2]:
            if (geo_coordinate[0] >= bb_coordinate[0] and geo_coordinate[0] <= bb_coordinate[2] and
                geo_coordinate[1] >= bb_coordinate[1] and geo_coordinate[1] <= bb_coordinate[3]):
                if not (in_tmp_array is None):
                    in_tmp_array[ind] += 1
                else:
                    self.histogram[ind] += 1                
        elif self.bb_collection[ind][3] == self.initial_bb[3] and self.bb_collection[ind][2] != self.initial_bb[2]:
            if (geo_coordinate[0] >= bb_coordinate[0] and geo_coordinate[0] < bb_coordinate[2] and
                geo_coordinate[1] >= bb_coordinate[1] and geo_coordinate[1] <= bb_coordinate[3]):
                if not (in_tmp_array is None):
                    in_tmp_array[ind] += 1
                else:
                    self.histogram[ind] += 1
        elif self.bb_collection[ind][3] != self.initial_bb[3] and self.bb_collection[ind][2] == self.initial_bb[2]:
            if (geo_coordinate[0] >= bb_coordinate[0] and geo_coordinate[0] <= bb_coordinate[2] and
                geo_coordinate[1] >= bb_coordinate[1] and geo_coordinate[1] < bb_coordinate[3]):
                if not (in_tmp_array is None):
                    in_tmp_array[ind] += 1
                else:
                    self.histogram[ind] += 1
        elif self.bb_collection[ind][3] != self.initial_bb[3] and self.bb_collection[ind][2] != self.initial_bb[2]:
            if (geo_coordinate[0] >= bb_coordinate[0] and geo_coordinate[0] < bb_coordinate[2] and
                geo_coordinate[1] >= bb_coordinate[1] and geo_coordinate[1] < bb_coordinate[3]):
                if not (in_tmp_array is None):
                    in_tmp_array[ind] += 1
                else:
                    self.histogram[ind] += 1
    # =====================================
    # calculate the counts in every cell
    def object_count(self, geo_type, in_coordinates):
        # ==================================
        if geo_type == 'Point':
            np_array = np.array(in_coordinates)
            # loop through all cells
            for ind in range(len(self.bb_collection)):
                self.point_within_grid(ind, np_array, self.bb_collection[ind], None)
        # ==================================
        elif geo_type == 'LineString':
            np_array = np.array(in_coordinates)
            tmp_array = np.zeros(len(self.bb_collection))
            # loop through all cells
            for ind in range(len(self.bb_collection)):
                for coordinate_ind in range(np_array.shape[0]):
                    self.point_within_grid(ind, np_array[coordinate_ind, :], self.bb_collection[ind], tmp_array)
            
            #print('temp :', tmp_array)
            for ind2 in range(len(self.bb_collection)):
                if tmp_array[ind2] > 0:
                    self.histogram[ind2] += 1
        # ==================================
        elif geo_type == 'Polygon':
            # discuss the aproach....
            print('Polygon')
    # =====================================
    # calculate the counts in every cell
    def counts_calculation(self):
        self.histogram = np.zeros(len(self.bb_collection))
        
        # loop through each geometry
        for index in range(len(self.data)):
            self.object_count(self.data[index][0], self.data[index][1])
            
        return self.histogram
    # =====================================
    # build a 2-d tree
    def tree_building(self):
        # get the split point and start with the root
        self.root = self.Get_split(0, self.initial_bb)
        # build the subtree
        self.build_subtree(self.root, 1, self.initial_bb)
        return self.root











    # =====================================
    # create leaves (calculate the number geometries within a bounding box)
#    def create_terminal_node(self, input_bounding_box):
#        tmp_id_list = []
#        # loop through each geometry to store its ID into a given bounding box
#        for index in range(len(self.data)):
#            tmp_id_list.append(self.Id_calculation(index, input_bounding_box, self.data[index][0],
#                                                   self.data[index][1]))
#        return tmp_id_list



#        return geometry_count
    # calculate the ratio and increment the geometry number
            #val = self.ratio_calculation(input_bounding_box, self.data[index][0],
            #                             self.data[index][1])
            #if val >= self.ratio_threshold:
            #    geometry_count += 1



    # calculate the counts in every cell
#    def object_count(self, input_bounding_box, geo_type, in_coordinates):
        # declare variables
#        count_value = 0
#        if geo_type == 'Point':
#            np_array = np.array(in_coordinates)
#            if (np_array[0] >= input_bounding_box[0] and np_array[0] < input_bounding_box[2] and
#                np_array[1] >= input_bounding_box[1] and np_array[1] < input_bounding_box[3]):
 #               count_value += 1
#        elif geo_type == 'LineString':
#            print('Line')
#        return count_value


    # calculate the ratio of that one geometry is in the bounding box
    #def ratio_calculation(self, input_bounding_box, geo_type, in_coordinates):
        # declare variables
#        total_point = 0
#        included_points = 0
        
#        if geo_type == 'Point' or geo_type == 'LineString' or geo_type == 'MultiPoint':
#            np_array = np.array(in_coordinates)
#            dim_value = len(np_array.shape)
#            if dim_value == 1:
#                total_point = 1
#                if (np_array[0] >= input_bounding_box[0] and np_array[0] < input_bounding_box[2] and
#                    np_array[1] >= input_bounding_box[1] and np_array[1] < input_bounding_box[3]):
#                    included_points += 1
#            elif dim_value == 2:
#                total_point = np_array.shape[0]
#                for coordinate_ind in range(total_point):
#                    if (np_array[coordinate_ind, :][0] >= input_bounding_box[0] and np_array[coordinate_ind, :][0] < input_bounding_box[2] and
#                        np_array[coordinate_ind, :][1] >= input_bounding_box[1] and np_array[coordinate_ind, :][1] < input_bounding_box[3]):
#                        included_points += 1
#        elif geo_type == 'Polygon' or geo_type == 'MultiLineString': # dimension = 3
#            # example: [
#            #            [[35, 10], [45, 45], [15, 40], [10, 20], [35, 10]],  ==> one polygon
#            #            [[20, 30], [35, 35], [30, 20], [20, 30]]             ==> the other
#            #           ]
#            total_point, included_points = self.dim_3_point_calculation(input_bounding_box, in_coordinates)
#        elif geo_type == 'MultiPolygon': # dimension = 4
#            # calculate the total point and all included points (loop through all 3-dimensional lists)
#            for index in range(len(in_coordinates)):
#                out_total, out_included = self.dim_3_point_calculation(input_bounding_box, in_coordinates[index])
#                total_point += out_total
#                included_points += out_included

#        return included_points / (total_point + 1e-8)



    # =====================================
    # record geometry ID
#    def Id_calculation(self, id_val, input_bounding_box, geo_type, in_coordinates):
#       if geo_type == 'Point':
#            np_array = np.array(in_coordinates)
#            if (np_array[0] >= input_bounding_box[0] and np_array[0] < input_bounding_box[2] and
#                np_array[1] >= input_bounding_box[1] and np_array[1] < input_bounding_box[3]):
#                return id_val
#        elif geo_type == 'LineString':
#            # return [ geometry ID, counts within the bounding box] if counts > 0
#            counts = 0
#            np_array = np.array(in_coordinates)
#            # loop through all coordinates
#            for coordinate_ind in range(np_array.shape[0]):
#                if (np_array[coordinate_ind, :][0] >= input_bounding_box[0] and np_array[coordinate_ind, :][0] < input_bounding_box[2] and
#                    np_array[coordinate_ind, :][1] >= input_bounding_box[1] and np_array[coordinate_ind, :][1] < input_bounding_box[3]):
#                    counts += 1
#            if counts > 0:
#                return [id_val, counts]
#        elif geo_type == 'Polygon':
#            print('Polygon')
#
