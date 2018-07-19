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
        numpy_array = np.array(self.hist)
        prob_list = numpy_array / sum(self.hist)
        
        # plot the histogram
        x = list(range(len(self.hist)))
        fig, ax = plt.subplots()
        ax.bar(x, prob_list)
        #plt.show()
        fig.savefig(os.path.join(path, 'level-' + str(in_count) + '.png'))
        
