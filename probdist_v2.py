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
    def distribution_computation(self, name):
        # create X-axis and Y-axis in order to plot histograms
        """
        X - Counts (or other measurements)
        Y - # of cells that has that counts/value (Frequency)
        """
        statistics_result = dict((i, list(self.hist).count(i)) for i in list(self.hist))
        statistics_result = dict(sorted(statistics_result.items()))
        count_0_pair = []
        if 0 in statistics_result:
            count_0_pair = [0, statistics_result[0]]
        
        statistics_result.pop(0, None)

        x_axis = list(statistics_result.keys())

        fig, ax = plt.subplots()
        ax.bar(range(len(statistics_result)), list(statistics_result.values()), align='center')
        plt.xticks((0, len(statistics_result) - 1), (x_axis[0], x_axis[len(statistics_result) - 1]))
        plt.xlabel('Counts (or other measurements)')
        plt.ylabel('Frequency (# of grids has that counts)')
        fig.savefig(name)

        return statistics_result, x_axis, count_0_pair, len(statistics_result)
    













