import numpy as np
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class probability_distribution:
    def __init__(self, input_histogram):
        self.hist = input_histogram
    # =====================================
    # calculate the probability distribution given a histogram
    def distribution_computation(self, in_count, path):
        # create X-axis and Y-axis in order to plot histograms
        """
        X - Counts (or other measurements)
        Y - # of cells that has that counts/value (Frequency)
        """
        statistics_result = dict((i, list(self.hist).count(i)) for i in list(self.hist))
        statistics_result.pop(0, None)

        x_axis = list(statistics_result.keys())

        fig, ax = plt.subplots()
        ax.bar(range(len(statistics_result)), list(statistics_result.values()),
               align='center', tick_label = x_axis)
        plt.xlabel('Counts (or other measurements)')
        plt.ylabel('Frequency (# of grids has that counts)')
        fig.savefig(os.path.join(path, 'level-' + str(in_count) + '.png'))

        
        #print(x_axis)
        #print(y_axis)
        #print(self.hist)
        #print(statistics_result)
        #prob_list = counts_array / sum(self.hist)
        # plot the histogram
        #x = np.array(list(range(1, len(self.hist) + 1)))
        
















